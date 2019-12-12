import pytest
from formatter.parser import create_parser


@pytest.fixture
def parser():
    return create_parser()
