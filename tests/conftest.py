import os
import pathlib
import pytest
from gersemi.configuration import ListExpansion
from gersemi.parser import create_parser, create_parser_with_postprocessing
from gersemi.formatter import create_formatter
from gersemi.runner import find_all_custom_command_definitions


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
    return find_all_custom_command_definitions(paths, Pool())


@pytest.fixture(scope="module")
def formatter_creator():
    def creator(config):
        return create_formatter(
            do_sanity_check=False,
            line_length=config.get("line_length", 80),
            custom_command_definitions=get_custom_command_definitions(
                config.get("definitions", [])
            ),
            list_expansion=ListExpansion(
                config.get("list_expansion", ListExpansion.FavourInlining)
            ),
        )

    return creator
