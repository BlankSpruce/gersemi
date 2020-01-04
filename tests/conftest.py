import pytest
from gersemi.parser import create_parser
from gersemi.formatter import create_formatter


@pytest.fixture
def parser():
    return create_parser()


@pytest.fixture
def formatter(parser):  # pylint: disable=redefined-outer-name
    return create_formatter(parser)
