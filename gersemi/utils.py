from functools import lru_cache
import sys


class StdinWrapper:
    @staticmethod
    @lru_cache(maxsize=None)
    def read():
        return sys.stdin.read()
