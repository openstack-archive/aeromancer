import logging
import sys

from cliff.app import App
from cliff.commandmanager import CommandManager
import pkg_resources


class Aeromancer(App):

    log = logging.getLogger(__name__)

    def __init__(self):
        dist = pkg_resources.get_distribution('aeromancer')
        super(Aeromancer, self).__init__(
            description='OpenStack source divination',
            version=dist.version,
            command_manager=CommandManager('aeromancer.cli'),
        )

    # def initialize_app(self, argv):
    #     self.log.debug('initialize_app')

    # def prepare_to_run_command(self, cmd):
    #     self.log.debug('prepare_to_run_command %s', cmd.__class__.__name__)

    # def clean_up(self, cmd, result, err):
    #     self.log.debug('clean_up %s', cmd.__class__.__name__)
    #     if err:
    #         self.log.debug('got an error: %s', err)


def main(argv=sys.argv[1:]):
    myapp = Aeromancer()
    return myapp.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
