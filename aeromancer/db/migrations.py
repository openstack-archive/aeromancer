import logging

from alembic import config
from alembic import command
from alembic import environment
from alembic import script

from sqlalchemy import engine_from_config, pool

from aeromancer.db import connect
from aeromancer import filehandler

LOG = logging.getLogger(__name__)


def _run_migrations_in_location(location):
    LOG.debug('loading migrations from %s', location)

    url = connect.get_url()

    # We need a unique version_table for each set of migrations.
    version_table = location.replace('.', '_') + '_versions'

    # Modified version of alembic.command.upgrade().
    # command.upgrade(cfg, 'head')
    revision = 'head'

    cfg = config.Config()
    cfg.set_main_option('script_location', location + ':alembic')
    cfg.set_main_option("sqlalchemy.url", url)

    script_dir = script.ScriptDirectory.from_config(cfg)

    def upgrade(rev, context):
        return script_dir._upgrade_revs(revision, rev)

    with environment.EnvironmentContext(
        cfg,
        script_dir,
        fn=upgrade,
        as_sql=False,
        starting_rev=None,
        destination_rev=revision,
        tag=None,
        version_table=version_table,
    ):
        script_dir.run_env()


def run_migrations():
    _run_migrations_in_location("aeromancer.db")
    file_handlers = filehandler.load_handlers()
    for fh in file_handlers:
        _run_migrations_in_location(fh.entry_point.module_name)


if __name__ == '__main__':
    run_migrations()
