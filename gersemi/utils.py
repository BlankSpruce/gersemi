from functools import lru_cache
from pathlib import Path
import sys


def fromfile(path):
    return "<stdin>" if path == Path("-") else str(path)


def tofile(path):
    return "<stdout>" if path == Path("-") else str(path)


class StdinWrapper:
    @staticmethod
    @lru_cache(maxsize=None)
    def read():
        return sys.stdin.read()
