import logging
import os

from aeromancer.db import models
from aeromancer.requirements import models as req_models
from aeromancer import project
from aeromancer import utils

from cliff.lister import Lister


class List(Lister):
    """List the requirements for a project"""

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
        query = session.query(models.Project).filter(
            models.Project.name == parsed_args.project
        )
        proj_obj = query.one()
        return (('Name', 'Spec'),
                ((r.name, r.line.content.strip()) for r in proj_obj.requirements))


class Uses(Lister):
    """List the projects that use requirement"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Uses, self).get_parser(prog_name)
        parser.add_argument(
            'requirement',
            help='the dist name for the requirement',
        )
        return parser

    def take_action(self, parsed_args):
        session = self.app.get_db_session()
        query = session.query(req_models.Requirement).filter(
            req_models.Requirement.name == parsed_args.requirement
        )
        return (('Name', 'Spec', 'File'),
                ((r.project.name, r.line.content.strip(), r.line.file.name) for r in query.all()))
