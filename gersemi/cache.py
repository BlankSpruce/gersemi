from contextlib import contextmanager
from pathlib import Path
import gersemi_rust_backend
from platformdirs import user_cache_dir
from gersemi.__version__ import __author__, __title__, __version__


def default_cache_dir() -> Path:
    return Path(
        user_cache_dir(appname=__title__, appauthor=__author__, version=__version__)
    )


def cache_path(cache_dir: Path) -> Path:
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / "cache.db"


@contextmanager
def create_cache(enable_cache: bool, cache_dir: Path):
    yield gersemi_rust_backend.Cache(enable_cache, cache_path(cache_dir))
