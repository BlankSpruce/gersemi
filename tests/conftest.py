import pathlib
import shutil
import gersemi_rust_backend
import pytest
from gersemi.configuration import (
    Configuration,
    ControlConfiguration,
    ListExpansion,
    OutcomeConfiguration,
    SortOrder,
    indent_type,
)
from gersemi.runner import find_all_custom_command_definitions
from tests.fixtures.app import App
from tests.fixtures.cache import Cache
from tests.utils import Parser


@pytest.fixture(scope="module")
def rust_parser():
    return Parser()


@pytest.fixture(scope="module")
def formatter_creator():
    def creator(config):
        configuration = Configuration(
            control=ControlConfiguration(respect_ignore_files=False),
            outcome=OutcomeConfiguration(
                unsafe=config.get("unsafe", True),
                line_length=config.get("line_length", 80),
                indent=indent_type(config.get("indent", 4)),
                list_expansion=ListExpansion(
                    config.get("list_expansion", ListExpansion.FavourInlining)
                ),
                sort_order=SortOrder(config.get("sort_order", SortOrder.CaseSensitive)),
                definitions=[
                    pathlib.Path(d).resolve() for d in config.get("definitions", [])
                ],
                extensions=["tests/custom_commands/extension.py"],
            ),
        )
        return gersemi_rust_backend.Formatter(
            configuration=configuration,
            definition_schemas=find_all_custom_command_definitions(configuration),
            lines_to_format=[],
        )

    return creator


@pytest.fixture
def cache(tmpdir):
    return Cache(pathlib.Path(tmpdir))


@pytest.fixture
def app(cache, tmpdir):  # pylint: disable=redefined-outer-name
    return App(cache=cache, fallback_cwd=tmpdir)


@pytest.fixture
def testfiles(tmpdir):
    original = pathlib.Path(__file__).parent / "executable"
    copy = tmpdir / original.name
    shutil.copytree(original, copy)
    return pathlib.Path(copy)
