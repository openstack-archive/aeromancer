from __future__ import print_function

import logging
import os

from aeromancer import project

from cliff.command import Command


class Grep(Command):
    """Search the contents of files"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Grep, self).get_parser(prog_name)
        parser.add_argument('pattern',
                            action='store',
                            help='regular expression',
                            )
        return parser

    def take_action(self, parsed_args):
        session = self.app.get_db_session()
        pm = project.ProjectManager(session)
        for r in pm.grep(parsed_args.pattern):
            line_num, content, filename, project_name = r
            print('%s/%s:%s:%s' %
                  (project_name, filename, line_num, content.rstrip())
            )
