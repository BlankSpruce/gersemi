from contextlib import contextmanager
import sqlite3


class CacheInspector:
    def __init__(self, cursor):
        self.cursor = cursor

    def get_tables(self):
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

    def get_files(self):
        return list(fields for fields in self.cursor.execute("SELECT * FROM files"))


@contextmanager
def inspect_cache(path):
    connection = sqlite3.connect(path)
    try:
        yield CacheInspector(connection.cursor())
    finally:
        connection.close()
