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
            modification_time INTEGER NOT NULL,
            configuration_summary TEXT NOT NULL
        )"""
    )


@contextmanager
def database_cursor(path):
    connection = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)
    try:
        cursor = connection.cursor()
        create_tables(cursor)
        yield cursor
    finally:
        connection.commit()
        connection.close()


def create_cache_entries(configuration_summary: str, paths: Iterable[Path]):
    for path in paths:
        s = path.stat()
        yield str(path), s.st_size, s.st_mtime_ns, configuration_summary


class Cache:
    def __init__(self, cursor: sqlite3.Cursor):
        self.cursor = cursor

    def store_files(self, configuration_summary: str, files: Iterable[Path]) -> None:
        self.cursor.executemany(
            "INSERT OR REPLACE INTO files VALUES (?, ?, ?, ?)",
            create_cache_entries(configuration_summary, files),
        )

    def get_files(self) -> Dict[Path, Tuple[int, int, str]]:
        return {
            Path(path): (size, modification_time, configuration_summary)
            for path, size, modification_time, configuration_summary in self.cursor.execute(
                "SELECT * FROM files"
            )
        }


class DummyCache:
    def store_files(self, *args, **kwargs) -> None:
        pass

    def get_files(self) -> Dict[Path, Tuple[int, int, str]]:
        return {}


@contextmanager
def create_cache():
    try:
        with database_cursor(cache_path()) as cursor:
            yield Cache(cursor)
    except sqlite3.Error:
        yield DummyCache()
