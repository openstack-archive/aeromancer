import fnmatch
import glob
import io
import itertools
import logging
import os
import subprocess

from sqlalchemy.orm.exc import NoResultFound

from aeromancer.db.models import Project, File, Line
from aeromancer import filehandler
from aeromancer import utils


LOG = logging.getLogger(__name__)


def discover(repo_root, organizations):
    """Discover project-like directories under the repository root"""
    glob_patterns = ['%s/*' % o for o in organizations]
    with utils.working_dir(repo_root):
        return itertools.ifilter(
            lambda x: os.path.isdir(os.path.join(repo_root, x)),
            itertools.chain(*(glob.glob(g) for g in glob_patterns))
        )

def _find_files_in_project(path):
    """Return a list of the files managed in the project.

    Uses 'git ls-files'
    """
    with utils.working_dir(path):
        cmd = subprocess.Popen(['git', 'ls-files', '-z'],
                               stdout=subprocess.PIPE)
        output = cmd.communicate()[0]
        return output.split('\0')


class ProjectManager(object):

    _DO_NOT_READ = [
        '*.doc', '*.docx', '*.graffle', '*.odp', '*.pptx', '*.vsd', '*.xsd',
        '*.gif', '*.ico', '*.jpeg', '*.jpg', '*.png', '*.tiff',
        '*.gpg',
        '*.jar',  # Why do we check in jar files?!
        '*.swf', '*.eot',
        '*.ttf', '*.woff',  # webfont; horizon
        '*.xml',
        '*.gz', '*.zip', '*.z',
        '*.mo', '*.db',
    ]

    def __init__(self, session):
        self.file_handlers = filehandler.load_handlers()
        self.session = session

    def _delete_filehandler_data_from_project(self, proj_obj):
        # We have to explicitly have the handlers delete their data
        # because the parent-child relationship of the tables is reversed
        # because the plugins define the relationships.
        LOG.debug('deleting plugin data for %s', proj_obj.name)
        for file_obj in proj_obj.files:
            for fh in self.file_handlers:
                if fh.obj.supports_file(file_obj):
                    fh.obj.delete_data_for_file(self.session, file_obj)

    def get_project(self, name):
        """Return an existing project, if there is one"""
        query = self.session.query(Project).filter(Project.name == name)
        try:
            return query.one()
        except NoResultFound:
            return None

    def add_or_update(self, name, path):
        """Create a new project definition or update an existing one"""
        proj_obj = self.get_project(name)
        if proj_obj:
            proj_obj.path = path
            LOG.info('updating project %s from %s', name, path)
        else:
            proj_obj = Project(name=name, path=path)
            LOG.info('adding project %s from %s', name, path)
            self.session.add(proj_obj)
        self.update(proj_obj)
        return proj_obj

    def update(self, proj_obj):
        """Update the settings for an existing project"""
        self._update_project_files(proj_obj)

    def remove(self, name):
        """Delete stored data for the named project"""
        query = self.session.query(Project).filter(Project.name == name)
        try:
            proj_obj = query.one()
            LOG.info('removing project %s', name)
        except NoResultFound:
            return
        self._delete_filehandler_data_from_project(proj_obj)
        self.session.delete(proj_obj)

    def _update_project_files(self, proj_obj):
        """Update the files stored for each project"""
        LOG.debug('reading file contents in %s', proj_obj.name)
        # Delete any existing files in case the list of files being
        # managed has changed. This naive, and we can do better, but as a
        # first version it's OK.
        self._delete_filehandler_data_from_project(proj_obj)
        for file_obj in proj_obj.files:
            self.session.delete(file_obj)

        # Now load the files currently being managed by git.
        for filename in _find_files_in_project(proj_obj.path):
            fullname = os.path.join(proj_obj.path, filename)
            if not os.path.isfile(fullname):
                continue
            new_file = File(project=proj_obj, name=filename, path=fullname)
            self.session.add(new_file)
            if any(fnmatch.fnmatch(filename, dnr) for dnr in self._DO_NOT_READ):
                LOG.debug('ignoring contents of %s', fullname)
            else:
                with io.open(fullname, mode='r', encoding='utf-8') as f:
                    try:
                        body = f.read()
                    except UnicodeDecodeError:
                        # FIXME(dhellmann): Be smarter about trying other
                        # encodings?
                        LOG.warn('Could not read %s as a UTF-8 encoded file, ignoring',
                                 fullname)
                        continue
                    lines = body.splitlines()
                    LOG.debug('%s/%s has %s lines', proj_obj.name, filename, len(lines))
                    for num, content in enumerate(lines, 1):
                        self.session.add(Line(file=new_file, number=num, content=content))

            # Invoke plugins for processing files in special ways
            for fh in self.file_handlers:
                if fh.obj.supports_file(new_file):
                    fh.obj.process_file(self.session, new_file)
