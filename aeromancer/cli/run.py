from __future__ import print_function

import logging
import os
import shlex

from aeromancer import project
from aeromancer import project_filter

from cliff.command import Command


class ArgumentParserWrapper(object):
    """Wrap a regular argument parser to replace
    parse_args with parse_known_args.

    Cliff calls parse_args() for subcommands, but we want
    parse_known_args() so any extra values that look like command
    switches will be ignored.

    """

    def __init__(self, parser):
        self._parser = parser

    def parse_args(self, argv):
        return self._parser.parse_known_args(argv)


class ProjectShellCommandBase(Command):
    """Run a command for each project"""

    log = logging.getLogger(__name__)

    DEFAULT_SEP = ''

    def get_parser(self, prog_name):
        parser = super(ProjectShellCommandBase, self).get_parser(prog_name)
        project_filter.ProjectFilter.add_arguments(parser)
        parser.add_argument(
            '--sep',
            action='store',
            default=self.DEFAULT_SEP,
            help=('separator between project name and command output, '
                  'defaults to %(default)r'),
        )
        return ArgumentParserWrapper(parser)

    def _show_text_output(self, parsed_args, project, out):
        for line in out.decode('utf-8').splitlines():
            print(project.name + parsed_args.sep + line)

    def _get_command(self, parsed_args):
        raise NotImplementedError()

    def _show_output(self, parsed_args, proj_obj, out, err):
        self._show_text_output(parsed_args, proj_obj, err or out)

    def take_action(self, parsed_args_tuple):
        # Handle the tuple we'll get from the parser wrapper.
        parsed_args, extra = parsed_args_tuple
        self._extra = extra
        session = self.app.get_db_session()
        pm = project.ProjectManager(session)
        prj_filt = project_filter.ProjectFilter.from_parsed_args(parsed_args)
        command = self._get_command(parsed_args)
        results = pm.run(command, prj_filt)
        for proj_obj, out, err in results:
            self._show_output(parsed_args, proj_obj, out, err)


class Run(ProjectShellCommandBase):
    """Run a command for each project"""

    log = logging.getLogger(__name__)

    DEFAULT_SEP = ':'

    def get_parser(self, prog_name):
        parser = super(Run, self).get_parser(prog_name)
        return parser

    def _get_command(self, parsed_args):
        return self._extra
