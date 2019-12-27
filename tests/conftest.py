from formatter.parser import create_parser
from formatter.formatter import create_formatter
import pytest


@pytest.fixture
def parser():
    return create_parser()


@pytest.fixture
def formatter(parser):  # pylint: disable=redefined-outer-name
    return create_formatter(parser)
