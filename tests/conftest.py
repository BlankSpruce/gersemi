import os
import pytest
from gersemi.parser import create_parser, create_parser_with_postprocessing
from gersemi.formatter import create_formatter


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


@pytest.fixture(scope="module")
def formatter():
    return create_formatter(
        do_sanity_check=False, line_length=80, custom_command_definitions={}
    )
