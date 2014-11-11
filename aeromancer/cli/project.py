import logging
import os

from aeromancer.db.models import *
from aeromancer import project
from aeromancer import utils

from cliff.command import Command
from cliff.lister import Lister


class Add(Command):
    "(Re)register a project to be scanned"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Add, self).get_parser(prog_name)
        parser.add_argument(
            'project',
            nargs='+',
            default=[],
            help=('project directory names under the project root, '
                  'for example: "stackforge/aeromancer"'),
        )
        return parser

    def take_action(self, parsed_args):
        session = self.app.get_db_session()
        pm = project.ProjectManager(session)
        for project_name in parsed_args.project:
            project_path = os.path.join(self.app.options.repo_root, project_name)
            pm.add_or_update(project_name, project_path)
            session.commit()


class List(Lister):
    """Show the registered projects"""

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        session = self.app.get_db_session()
        query = session.query(Project).order_by(Project.name)
        return (('Name', 'Path'),
                ((p.name, p.path) for p in query.all()))


class Rescan(Command):
    "Rescan all known projects"

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        session = self.app.get_db_session()
        query = session.query(Project).order_by(Project.name)
        for proj_obj in query.all():
            project.update(session, proj_obj)
            session.commit()


class Discover(Command):
    "Find all projects in the repository root"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Discover, self).get_parser(prog_name)
        parser.add_argument(
            '--organization', '--org', '-o',
            action='append',
            default=[],
            help=('organization directory names under the project root, '
                  'for example: "stackforge", defaults to "openstack"'),
        )
        return parser

    def take_action(self, parsed_args):
        session = self.app.get_db_session()
        pm = project.ProjectManager(session)
        orgs = parsed_args.organization
        if not orgs:
            orgs = ['openstack']
        for project_name in project.discover(self.app.options.repo_root, orgs):
            full_path = os.path.join(self.app.options.repo_root,
                                     project_name)
            pm.add_or_update(project_name, full_path)
            session.commit()


class Remove(Command):
    "Remove a project from the database"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Remove, self).get_parser(prog_name)
        parser.add_argument(
            'project',
            nargs='+',
            default=[],
            help=('project directory names under the project root, '
                  'for example: "stackforge/aeromancer"'),
        )
        return parser

    def take_action(self, parsed_args):
        session = self.app.get_db_session()
        pm = project.ProjectManager(session)
        for project_name in parsed_args.project:
            pm.remove(project_name)
            session.commit()
