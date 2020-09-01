from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path
import sys
from typing import Any, Iterator, List


def pop_all(in_list: List) -> List:
    popped, in_list[:] = in_list[:], []
    return popped


def advance(iterator: Iterator, times: int, default: Any) -> Any:
    result = default
    for _ in range(times):
        new_result = next(iterator, default)
        if new_result == default:
            break
        result = new_result
    return result


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
        try:
            fh = open(filename, mode, *args, **kwargs)
            yield fh
        finally:
            fh.close()
