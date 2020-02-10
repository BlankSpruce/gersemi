import pytest
from gersemi.parser import create_parser
from gersemi.formatter import create_formatter


@pytest.fixture(scope="module")
def parser():
    return create_parser()


@pytest.fixture(scope="module")
def experimental_enabled():
    return False


@pytest.fixture(scope="module")
def preserve_custom_command_formatting():
    return False


@pytest.fixture(scope="module")
def formatter(
    parser, experimental_enabled, preserve_custom_command_formatting
):  # pylint: disable=redefined-outer-name
    return create_formatter(
        parser,
        do_sanity_check=False,
        enable_experimental_features=experimental_enabled,
        preserve_custom_command_formatting=preserve_custom_command_formatting,
    )
