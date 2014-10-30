import logging

from alembic.config import Config
from alembic import command
from alembic.environment import EnvironmentContext
from alembic.script import ScriptDirectory
from sqlalchemy import engine_from_config, pool


LOG = logging.getLogger(__name__)


def run_migrations():
    config = Config()
    config.set_main_option("script_location", "aeromancer.db:alembic")
    config.set_main_option("sqlalchemy.url", "sqlite:////Users/dhellmann/.aeromancer/aeromancer.db")
    command.upgrade(config, 'head')


if __name__ == '__main__':
    run_migrations()
