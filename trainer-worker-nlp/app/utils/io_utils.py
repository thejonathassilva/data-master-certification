import os
from contextlib import contextmanager

@contextmanager
def temp_chdir(path):
    old = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old)
