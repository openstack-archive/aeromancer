import logging

import pkg_resources

from aeromancer.filehandler import base
from . import models

LOG = logging.getLogger(__name__)


def read_requirements_file(file_obj):
    for line in file_obj.lines:
        text = line.content.strip()
        if not text or text.startswith('#'):
            continue
        try:
            # FIXME(dhellmann): Use pbr's requirements parser.
            dist_name = pkg_resources.Requirement.parse(text).project_name
        except ValueError:
            LOG.warn('could not parse dist name from %r',
                     line.content)
            continue
        yield dist_name, line


class RequirementsHandler(base.FileHandler):

    INTERESTING_PATTERNS = [
        'requirements.txt',
        'requirements-py*.txt',
        'test-requirements.txt',
        'test-requirements-py*.txt',
    ]

    def process_file(self, session, file_obj):
        LOG.info('loading requirements from %s', file_obj.project_path)
        parent_project = file_obj.project
        for dist_name, line in read_requirements_file(file_obj):
            LOG.debug('requirement: %s', dist_name)
            new_r = models.Requirement(
                name=dist_name,
                line=line,
                project=parent_project,
            )
            session.add(new_r)

    def delete_data_for_file(self, session, file_obj):
        LOG.debug('deleting requirements from %r', file_obj.path)
        for line in file_obj.lines:
            query = session.query(models.Requirement).filter(
                models.Requirement.line_id == line.id
            )
            for req in query.all():
                session.delete(req)
        return
