import logging
import os

from cliff.command import Command


class Add(Command):
    "(Re)register a project to be scanned"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Add, self).get_parser(prog_name)
        parser.add_argument(
            'project',
            nargs='+',
            default=[],
            help='project directory names under the project root, e.g., "stackforge/aeromancer"',
        )
        return parser

    def take_action(self, parsed_args):
        for project in parsed_args.project:
            project_path = os.path.join(self.app.options.repo_root, project)
            self.log.info('adding project %s from %s', project, project_path)
