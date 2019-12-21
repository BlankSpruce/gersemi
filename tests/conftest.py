import pytest
from formatter.parser import create_parser
from formatter.formatter import create_formatter


@pytest.fixture
def parser():
    return create_parser()


@pytest.fixture
def formatter(parser):
    return create_formatter(parser)
