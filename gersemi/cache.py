from contextlib import contextmanager
from pathlib import Path
import sqlite3
from typing import Dict, Iterable, Tuple
from appdirs import user_cache_dir
from gersemi.__version__ import __author__, __title__, __version__


def cache_path() -> Path:
    directory = Path(
        user_cache_dir(appname=__title__, appauthor=__author__, version=__version__)
    )
    directory.mkdir(parents=True, exist_ok=True)
    return directory / "cache.db"


def create_tables(cursor: sqlite3.Cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS files (
            path TEXT PRIMARY KEY,
            size INTEGER NOT NULL,
            modification_time INTEGER NOT NULL
        )"""
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS formatted (
            path TEXT PRIMARY KEY,
            configuration_summary TEXT NOT NULL,
            FOREIGN KEY (path) REFERENCES files (path)
        )"""
    )


@contextmanager
def database_cursor(path):
    connection = sqlite3.connect(str(path), detect_types=sqlite3.PARSE_DECLTYPES)
    connection.execute("PRAGMA foreign_keys = 1")
    try:
        cursor = connection.cursor()
        create_tables(cursor)
        yield cursor
    finally:
        connection.commit()
        connection.close()


def create_file_entry(path: Path):
    s = path.stat()
    return str(path), s.st_size, s.st_mtime_ns


class Cache:
    def __init__(self, cursor: sqlite3.Cursor):
        self.cursor = cursor

    def store_files(self, configuration_summary: str, files: Iterable[Path]) -> None:
        f = list(files)
        self.cursor.executemany(
            "INSERT OR REPLACE INTO files VALUES (?, ?, ?)",
            map(create_file_entry, f),
        )
        self.cursor.executemany(
            "INSERT OR REPLACE INTO formatted VALUES (?, ?)",
            [(str(path), configuration_summary) for path in f],
        )

    def get_files(self, configuration_summary: str) -> Dict[Path, Tuple[int, int]]:
        return {
            Path(path): (size, modification_time)
            for path, size, modification_time in self.cursor.execute(
                """
                SELECT *
                FROM files
                WHERE files.path IN (
                    SELECT formatted.path
                    FROM formatted
                    WHERE formatted.configuration_summary = (?)
                )""",
                (configuration_summary,),
            )
        }


class DummyCache:
    def store_files(self, *args, **kwargs) -> None:
        pass

    def get_files(self, _) -> Dict[Path, Tuple[int, int, str]]:
        return {}


@contextmanager
def create_cache():
    try:
        with database_cursor(cache_path()) as cursor:
            yield Cache(cursor)
    except sqlite3.Error:
        yield DummyCache()
