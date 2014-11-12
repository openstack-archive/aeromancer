import logging

import pkg_resources

from aeromancer.db import models as models
from aeromancer.filehandler import base
from aeromancer.oslo import models as oslo_models

LOG = logging.getLogger(__name__)


def read_sync_file(file_obj):
    for line in file_obj.lines:
        text = line.content.strip()
        if not text or text.startswith('#'):
            continue
        if not text.startswith('module'):
            continue
        text = text[len('module'):]
        text = text.lstrip('= ')
        modules = text.split(',')
        for m in modules:
            yield m.strip(), line


class OsloSyncHandler(base.FileHandler):

    INTERESTING_PATTERNS = [
        'openstack-common.conf',
    ]

    def process_file(self, session, file_obj):
        LOG.info('loading Oslo settings from %s', file_obj.project_path)
        parent_project = file_obj.project
        for module_name, line in read_sync_file(file_obj):
            LOG.debug('module: %s', module_name)
            new_r = oslo_models.Module(
                name=module_name,
                line=line,
                project=parent_project,
            )
            session.add(new_r)

    def delete_data_for_file(self, session, file_obj):
        LOG.debug('deleting Oslo modules from %r', file_obj.path)
        query = session.query(oslo_models.Module).join(models.Line).filter(
            models.Line.file_id == file_obj.id
        )
        for r in query.all():
            session.delete(r)
        return
