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
    """Return a list of the files managed in the project and their sha hash.

    Uses 'git ls-files -s'
    """
    with utils.working_dir(path):
        # Ask git to tell us the sha hash so we can tell if the file
        # has changed since we looked at it last.
        cmd = subprocess.Popen(['git', 'ls-files', '-z', '-s'],
                               stdout=subprocess.PIPE)
        output = cmd.communicate()[0]
        entries = output.split('\0')
        for e in entries:
            if not e:
                continue
            metadata, ignore, filename = e.partition('\t')
            sha = metadata.split(' ')[1]
            yield (filename, sha)


class ProjectManager(object):

    _DO_NOT_READ = [
        '*.doc', '*.docx', '*.graffle', '*.odp', '*.pptx', '*.vsd', '*.xsd',
        '*.gif', '*.ico', '*.jpeg', '*.jpg', '*.png', '*.tiff', '*.JPG',
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

    def get_project(self, name):
        """Return an existing project, if there is one"""
        query = self.session.query(Project).filter(Project.name == name)
        try:
            return query.one()
        except NoResultFound:
            return None

    def add_or_update(self, name, path, force=False):
        """Create a new project definition or update an existing one"""
        proj_obj = self.get_project(name)
        if proj_obj:
            proj_obj.path = path
            LOG.info('updating project %s from %s', name, path)
        else:
            proj_obj = Project(name=name, path=path)
            LOG.info('adding project %s from %s', name, path)
            self.session.add(proj_obj)
            self.session.flush()
            assert proj_obj.id, 'No id for new project'
        self.update(proj_obj, force=force)
        return proj_obj

    def update(self, proj_obj, force=False):
        """Update the settings for an existing project"""
        self._update_project_files(proj_obj, force=force)

    def remove(self, name):
        """Delete stored data for the named project"""
        query = self.session.query(Project).filter(Project.name == name)
        try:
            proj_obj = query.one()
            LOG.info('removing project %s', name)
        except NoResultFound:
            return
        for file_obj in proj_obj.files:
            self._remove_plugin_data_for_file(file_obj)
        self.session.delete(proj_obj)

    def _remove_plugin_data_for_file(self, file_obj):
        # We have to explicitly have the handlers delete their data
        # because the parent-child relationship of the tables is reversed
        # because the plugins define the relationships.
        for fh in self.file_handlers:
            if fh.obj.supports_file(file_obj):
                LOG.debug('removing %s plugin data for %s', fh.name, file_obj.name)
                fh.obj.delete_data_for_file(self.session, file_obj)

    def _remove_file_data(self, file_obj, reason='file has changed'):
        """Delete the data associated with the file, including plugin data and
        file contents.

        """
        LOG.debug('removing cached contents of %s: %s', file_obj.name, reason)
        self._remove_plugin_data_for_file(file_obj)
        self.session.query(Line).filter(Line.file_id == file_obj.id).delete()
        self.session.delete(file_obj)

    def _update_project_files(self, proj_obj, force):
        """Update the files stored for each project"""
        LOG.debug('reading file contents in %s', proj_obj.name)

        # Collect the known files in a project so we can test their
        # SHAs quickly.
        known = {f.name: f for f in proj_obj.files}

        # Track the files we've seen so we can delete any files that
        # are no longer present.
        seen = set()

        # Now load the files currently being managed by git.
        for filename, sha in _find_files_in_project(proj_obj.path):
            # Remember that we have seen the file in the project.
            seen.add(filename)
            # Skip things that are not files (usually symlinks).
            fullname = os.path.join(proj_obj.path, filename)
            if not os.path.isfile(fullname):
                continue
            try:
                existing_file = known[filename]
                if existing_file.sha == sha and not force:
                    # File has not changed, we can use the content we
                    # already have.
                    LOG.debug('using cached version of %s', filename)
                    continue
                self._remove_file_data(existing_file)
            except KeyError:
                pass
            new_file = File(project=proj_obj, name=filename, path=fullname, sha=sha)
            self.session.add(new_file)
            self.session.flush()  # make sure new_file gets an id
            assert new_file.id, 'No id for new file'
            if any(fnmatch.fnmatch(filename, dnr) for dnr in self._DO_NOT_READ):
                LOG.debug('ignoring contents of %s', fullname)
            else:
                LOG.debug('reading %s', fullname)
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
                    # Use SQLalchemy's core mode to bulk insert the lines.
                    if lines:
                        self.session.execute(
                            Line.__table__.insert(),
                            [{'file_id': new_file.id,
                              'number': num,
                              'content': content}
                             for num, content in enumerate(lines, 1)]
                        )
                    LOG.debug('%s/%s has %s lines', proj_obj.name, filename, len(lines))

            # Invoke plugins for processing files in special ways
            for fh in self.file_handlers:
                if fh.obj.supports_file(new_file):
                    fh.obj.process_file(self.session, new_file)

            self.session.flush()

        # Remove files that we have in the database but that were no
        # longer seen in the git repository.
        for name, obj in known.items():
            if name not in seen:
                self._remove_file_data(obj, reason='file no longer exists')
                self.session.flush()

    def grep(self, pattern, prj_filter):
        """Given a pattern, search for lines in files in all projects that match it.

        Returns results of the query, including the four columns line
        number, line content, filename, and project name.

        """
        # TODO: Would it be more efficient to register the regexp
        # function on the db session here instead of when we connect?
        # We could pre-compile the regex and not pass it to each
        # invocation of the function.
        query = self.session.query(Project)
        if prj_filter:
            query = prj_filter.update_query(query)
        query = query.order_by(Project.name)
        #return query.yield_per(20).all()
        for project in query.all():
            cmd = subprocess.Popen(
                ['git', 'grep', pattern],
                stdout=subprocess.PIPE,
                cwd=project.path,
                env={'PAGER': ''},
            )
            out, err = cmd.communicate()
            if not out:
                continue
            for line in out.decode('utf-8').splitlines():
                yield project.name + line
