import logging

from aeromancer.db.models import Project

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
