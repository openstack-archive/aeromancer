import contextlib
import os


@contextlib.contextmanager
def working_dir(new_dir):
    before = os.getcwd()
    os.chdir(new_dir)
    yield
    os.chdir(before)
