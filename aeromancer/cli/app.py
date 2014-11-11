import logging
import os
import sys

from cliff.app import App
from cliff.commandmanager import CommandManager
import pkg_resources
from sqlalchemy.orm import sessionmaker

from aeromancer.db import connect, migrations


class Aeromancer(App):

    log = logging.getLogger(__name__)
    # CONSOLE_MESSAGE_FORMAT = \
    #     '[%(asctime)s] %(levelname)-8s %(name)s %(message)s'

    def __init__(self):
        dist = pkg_resources.get_distribution('aeromancer')
        super(Aeromancer, self).__init__(
            description='OpenStack source divination',
            version=dist.version,
            command_manager=CommandManager('aeromancer.cli'),
        )

    def build_option_parser(self, description, version,
                            argparse_kwargs=None):
        parser = super(Aeromancer, self).build_option_parser(
            description,
            version,
            argparse_kwargs,
        )
        default_repo_root = os.environ.get('AEROMANCER_REPOS', '~/repos')
        parser.add_argument(
            '--repo-root',
            default=os.path.expanduser(default_repo_root),
            help=('directory where repositories are checked out; '
                  'set with AEROMANCER_REPOS environment variable; '
                  'defaults to %(default)s'),
        )
        return parser

    def configure_logging(self):
        super(Aeromancer, self).configure_logging()
        if self.options.verbose_level < 2:
            # Quiet the logger that talks about updating the database.
            alembic_logger = logging.getLogger('alembic.migration')
            alembic_logger.setLevel(logging.WARN)
        return

    def initialize_app(self, argv):
        # Make sure our application directory exists, so we have a
        # place to put the database and any other configuration files.
        self.app_dir = os.path.expanduser('~/.aeromancer')
        if not os.path.exists(self.app_dir):
            os.mkdir(self.app_dir)
        self.log.debug('updating database')
        migrations.run_migrations()
        self.engine = connect.connect()
        self._session_maker = sessionmaker(bind=self.engine)

    def get_db_session(self):
        return self._session_maker()

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
