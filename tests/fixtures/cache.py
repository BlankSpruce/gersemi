import sqlite3


class Cache:
    def __init__(self, directory):
        self.directory = directory
        self.path = directory / "cache.db"
        self.clear()

    def __str__(self):
        return str(self.directory)

    def clear(self):
        with open(self.path, "w") as f:
            f.write("")

    def _execute(self, query):
        connection = sqlite3.connect(self.path)
        cursor = connection.cursor()
        yield from cursor.execute(query)
        connection.close()

    def _get_tables(self):
        return list(
            name
            for (name,) in self._execute(
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
        return list(fields for fields in self._execute("SELECT * FROM files"))

    def get_formatted(self):
        return list(fields for fields in self._execute("SELECT * FROM formatted"))
