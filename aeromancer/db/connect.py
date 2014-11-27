import os
import re

from sqlalchemy import create_engine
from sqlalchemy import event


def get_url():
    """Return the database URL"""
    db_file_path = os.path.expanduser('~/.aeromancer/aeromancer.db')
    return "sqlite:///%s" % db_file_path


def _re_fn(expr, item):
    "Registered as the regexp function with sqlite."
    reg = re.compile(expr, re.I)
    return reg.search(item) is not None


def connect():
    """Return a database engine"""
    engine = create_engine(get_url())

    @event.listens_for(engine, "begin")
    def do_begin(conn):
        conn.connection.create_function('regexp', 2, _re_fn)

    return engine
