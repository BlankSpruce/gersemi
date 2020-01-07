import pytest
from gersemi.parser import create_parser
from gersemi.formatter import create_formatter


@pytest.fixture(scope="session")
def parser():
    return create_parser()


@pytest.fixture(scope="session")
def formatter(parser):  # pylint: disable=redefined-outer-name
    return create_formatter(parser, do_sanity_check=False)
