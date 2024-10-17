import os
import pathlib
import shutil
import pytest
from gersemi.configuration import indent_type, ListExpansion
from gersemi.parser import create_parser, create_parser_with_postprocessing
from gersemi.formatter import create_formatter
from gersemi.runner import find_all_custom_command_definitions
from tests.fixtures.app import App
from tests.fixtures.cache import Cache


@pytest.fixture(scope="module")
def parser():
    return create_parser()


@pytest.fixture(scope="module")
def parser_with_simple_grammar():
    this_file_dir = os.path.dirname(os.path.realpath(__file__))
    grammar = os.path.join(this_file_dir, "simple_cmake.lark")
    return create_parser(grammar)


@pytest.fixture(scope="module")
def parser_with_postprocessing(parser):  # pylint: disable=redefined-outer-name
    return create_parser_with_postprocessing(parser)


def get_custom_command_definitions(configuration_definitions):
    class Pool:
        def imap_unordered(
            self, func, files, *args, **kwargs
        ):  # pylint: disable=unused-argument
            yield from map(func, files)

    paths = [pathlib.Path(d).resolve() for d in configuration_definitions]
    return find_all_custom_command_definitions(paths=paths, quiet=False, pool=Pool())


@pytest.fixture(scope="module")
def formatter_creator():
    def creator(config):
        return create_formatter(
            do_sanity_check=not config.get("unsafe", False),
            line_length=config.get("line_length", 80),
            indent=indent_type(config.get("indent", 4)),
            custom_command_definitions=get_custom_command_definitions(
                config.get("definitions", [])
            ),
            list_expansion=ListExpansion(
                config.get("list_expansion", ListExpansion.FavourInlining)
            ),
        )

    return creator


@pytest.fixture(scope="function")
def cache(tmpdir):
    return Cache(pathlib.Path(tmpdir) / "temporary_cache.db")


@pytest.fixture(scope="function")
def app(cache, tmpdir):  # pylint: disable=redefined-outer-name
    return App(cache=cache, fallback_cwd=tmpdir)


@pytest.fixture(scope="function")
def testfiles(tmpdir):
    original = pathlib.Path(os.path.dirname(os.path.realpath(__file__))) / "executable"
    original_base = os.path.basename(original)
    copy = os.path.join(tmpdir, original_base)
    shutil.copytree(original, copy)
    return pathlib.Path(copy)
