from pathlib import Path
from platformdirs import user_cache_dir
from gersemi.__version__ import __author__, __title__, __version__


def default_cache_dir() -> Path:
    return Path(
        user_cache_dir(appname=__title__, appauthor=__author__, version=__version__)
    )
