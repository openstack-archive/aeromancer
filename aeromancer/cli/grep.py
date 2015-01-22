from __future__ import print_function

import logging
import os

from aeromancer import project
from aeromancer import project_filter

from aeromancer.cli.run import ProjectShellCommandBase


class Grep(ProjectShellCommandBase):
    """Search the contents of files"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Grep, self).get_parser(prog_name)
        parser.add_argument('pattern',
                            action='store',
                            help='regular expression',
                            )
        return parser

    def _get_command(self, parsed_args):
        return ['git', 'grep', parsed_args.pattern]
