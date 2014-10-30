import os

from sqlalchemy import create_engine


def get_url():
    """Return the database URL"""
    db_file_path = os.path.expanduser('~/.aeromancer/aeromancer.db')
    return "sqlite:///%s" % db_file_path


def connect():
    """Return a database engine"""
    return create_engine(get_url())
