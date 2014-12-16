import logging
import os

from aeromancer.db import models
from aeromancer.requirements import models as req_models
from aeromancer import project
from aeromancer import utils

from cliff.lister import Lister

from sqlalchemy import distinct
from sqlalchemy.orm import aliased


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
        query = session.query(req_models.Requirement).join(models.Project).filter(
            models.Project.name == parsed_args.project
        ).order_by(req_models.Requirement.name)
        return (('Name', 'Spec', 'File'),
                ((r.name, r.line.content.strip(), r.line.file.name)
                 for r in query.all()))


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
        query = session.query(req_models.Requirement).join(models.Project).filter(
            req_models.Requirement.name.ilike(parsed_args.requirement)
        ).order_by(models.Project.name)
        return (('Name', 'Spec', 'File'),
                ((r.project.name, r.line.content.strip(), r.line.file.name) for r in query.all()))


class Unused(Lister):
    """List global requirements not used by any projects"""

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        session = self.app.get_db_session()
        used_requirements = session.query(distinct(req_models.Requirement.name))
        query = session.query(req_models.GlobalRequirement).filter(
            req_models.GlobalRequirement.name.notin_(used_requirements)
        ).order_by(req_models.GlobalRequirement.name)
        return (('Name', 'Spec'),
                ((r.name, r.line.content.strip()) for r in query.all()))


class Outdated(Lister):
    """List requirements in projects that do not match the global spec"""

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        session = self.app.get_db_session()
        used_requirements = session.query(distinct(req_models.Requirement.name))
        global_line = aliased(models.Line)
        project_line = aliased(models.Line)
        query = session.query(req_models.Requirement,
                              models.Project,
                              global_line,
                              project_line,
                              req_models.GlobalRequirement).filter(
                                  req_models.Requirement.project_id == models.Project.id,
                                  req_models.Requirement.name == req_models.GlobalRequirement.name,
                                  project_line.id == req_models.Requirement.line_id,
                                  global_line.id == req_models.GlobalRequirement.line_id,
                                  project_line.content != global_line.content,
                              ).order_by(models.Project.name, req_models.Requirement.name)
        return (('Project', 'Local', 'Global'),
                ((r[1].name, r[3].content.strip(), r[2].content.strip())
                 for r in query.all()))
