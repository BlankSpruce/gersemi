from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path
import sys
from typing import List


def pop_all(in_list: List) -> List:
    popped, in_list[:] = in_list[:], []
    return popped


def fromfile(path):
    return "<stdin>" if path == Path("-") else str(path)


def tofile(path):
    return "<stdout>" if path == Path("-") else str(path)


class StdinWrapper:
    @staticmethod
    @lru_cache(maxsize=None)
    def read():
        return sys.stdin.read()


def standard_stream_open(mode):
    if mode is None or mode == "" or "r" in mode:
        return StdinWrapper()
    return sys.stdout


@contextmanager
def smart_open(filename, mode, *args, **kwargs):
    if filename == Path("-"):
        yield standard_stream_open(mode)
    else:
        with open(filename, mode, *args, **kwargs, encoding="utf-8") as fh:
            yield fh
