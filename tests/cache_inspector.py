from contextlib import contextmanager
import sqlite3


class CacheInspector:
    def __init__(self, cursor):
        self.cursor = cursor

    def _get_tables(self):
        return list(
            name
            for (name,) in self.cursor.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                """
            )
        )

    def assert_that_has_no_tables(self):
        assert len(self._get_tables()) == 0

    def assert_that_has_initialized_tables(self):
        assert self._get_tables() == ["files", "formatted"]

    def get_files(self):
        return list(fields for fields in self.cursor.execute("SELECT * FROM files"))

    def get_formatted(self):
        return list(fields for fields in self.cursor.execute("SELECT * FROM formatted"))


@contextmanager
def inspect_cache(path):
    connection = sqlite3.connect(path)
    try:
        yield CacheInspector(connection.cursor())
    finally:
        connection.close()
