import logging
import os

from aeromancer.db.models import *

from cliff.command import Command
from cliff.lister import Lister
from sqlalchemy.orm.exc import NoResultFound

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
        for project in parsed_args.project:
            project_path = os.path.join(self.app.options.repo_root, project)
            query = session.query(Project).filter(Project.name == project)
            try:
                proj_obj = query.one()
                proj_obj.path = project_path
                self.log.info('updating project %s from %s', project, project_path)
            except NoResultFound:
                proj_obj = Project(name=project, path=project_path)
                self.log.info('adding project %s from %s', project, project_path)
                session.add(proj_obj)
        session.commit()


class List(Lister):
    """Show the registered projects"""

    def take_action(self, parsed_args):
        session = self.app.get_db_session()
        query = session.query(Project).order_by(Project.name)
        return (('Name', 'Path'),
                ((p.name, p.path) for p in query.all()))
