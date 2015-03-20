from __future__ import print_function

import logging
import os

from aeromancer import project
from aeromancer import project_filter

from aeromancer.cli.run import ProjectShellCommandBase


class Grep(ProjectShellCommandBase):
    """Search the contents of files

    Accepts most of the arguments of git-grep, unless they conflict
    with other arguments to this command.

    """

    log = logging.getLogger(__name__)

    DEFAULT_SEP = '/'

    def _get_command(self, parsed_args):
        return ['git', 'grep'] + self._extra
