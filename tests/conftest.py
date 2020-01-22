import pytest
from gersemi.parser import create_parser
from gersemi.formatter import create_formatter


@pytest.fixture(scope="module")
def parser(experimental_enabled):  # pylint: disable=redefined-outer-name
    return create_parser(propagate_positions=experimental_enabled)


@pytest.fixture(scope="module")
def experimental_enabled():
    return False


@pytest.fixture(scope="module")
def formatter(parser, experimental_enabled):  # pylint: disable=redefined-outer-name
    return create_formatter(
        parser,
        do_sanity_check=False,
        enable_experimental_features=experimental_enabled,
    )
