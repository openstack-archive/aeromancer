import logging

from alembic.config import Config
from alembic import command
from alembic.environment import EnvironmentContext
from alembic.script import ScriptDirectory
from sqlalchemy import engine_from_config, pool

from aeromancer.db import connect

LOG = logging.getLogger(__name__)


def run_migrations():
    config = Config()
    config.set_main_option("script_location", "aeromancer.db:alembic")
    url = connect.get_url()
    config.set_main_option("sqlalchemy.url", url)
    command.upgrade(config, 'head')
    # NOTE(dhellmann): Load migration settings from the plugins for
    # processing special types of files, and run them.


if __name__ == '__main__':
    run_migrations()
