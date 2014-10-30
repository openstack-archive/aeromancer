import io
import logging
import os
import subprocess

from aeromancer.db.models import Project, File

from sqlalchemy.orm.exc import NoResultFound


LOG = logging.getLogger(__name__)


def add_or_update(session, name, path):
    """Create a new project definition or update an existing one"""
    query = session.query(Project).filter(Project.name == name)
    try:
        proj_obj = query.one()
        proj_obj.path = path
        LOG.info('updating project %s from %s', name, path)
    except NoResultFound:
        proj_obj = Project(name=name, path=path)
        LOG.info('adding project %s from %s', name, path)
        session.add(proj_obj)

    update_project_files(session, proj_obj)
    return proj_obj


def remove(session, name):
    """Delete stored data for the named project"""
    query = session.query(Project).filter(Project.name == name)
    try:
        proj_obj = query.one()
        LOG.info('removing project %s', name)
    except NoResultFound:
        return
    session.delete(proj_obj)


def update_project_files(session, proj_obj):
    """Update the files stored for each project"""
    # Delete any existing files in case the list of files being
    # managed has changed. This naive, and we can do better, but as a
    # first version it's OK.
    for file_obj in proj_obj.files:
        session.delete(file_obj)

    # Now load the files currently being managed by git.
    before = os.getcwd()
    os.chdir(proj_obj.path)
    try:
        cmd = subprocess.Popen(['git', 'ls-files', '-z'],
                               stdout=subprocess.PIPE)
        output = cmd.communicate()[0]
        filenames = output.split('\0')
    finally:
        os.chdir(before)
    for filename in filenames:
        fullname = os.path.join(proj_obj.path, filename)
        if not os.path.isfile(fullname):
            continue
        with io.open(fullname, mode='r', encoding='utf-8') as f:
            body = f.read()
            lines = body.splitlines()
            LOG.info('%s has %s lines', filename, len(lines))
        session.add(File(project=proj_obj, name=filename, path=fullname))
