import logging
import os

from aeromancer.db import models
from aeromancer.oslo import models as oslo_models
from aeromancer import project
from aeromancer import utils

from cliff.lister import Lister

from sqlalchemy import distinct
from sqlalchemy.orm import aliased


class List(Lister):
    """List the Oslo modules used by a project"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(List, self).get_parser(prog_name)
        parser.add_argument(
            'project',
            help=('project directory name under the project root, '
                  'for example: "stackforge/aeromancer"'),
        )
        return parser

    def take_action(self, parsed_args):
        session = self.app.get_db_session()
        query = session.query(oslo_models.Module).join(models.Project).filter(
            models.Project.name == parsed_args.project
        ).order_by(oslo_models.Module.name)
        return (('Name',),
                ((r.name,)
                 for r in query.all()))


class Uses(Lister):
    """List the projects that use the Oslo module"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Uses, self).get_parser(prog_name)
        parser.add_argument(
            'module',
            help='the module name',
        )
        return parser

    def take_action(self, parsed_args):
        session = self.app.get_db_session()
        query = session.query(oslo_models.Module).join(models.Project).filter(
            oslo_models.Module.name == parsed_args.module
        ).order_by(models.Project.name)
        return (('Project',),
                ((r.project.name,) for r in query.all()))
