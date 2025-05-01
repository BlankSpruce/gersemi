# pylint: disable=redefined-outer-name
from functools import partial
import pytest
from tests.fixtures.app import success, fail


@pytest.fixture(scope="function")
def app(app, testfiles):
    extension = (testfiles / "overrides" / "extension.py").resolve()
    return partial(app, "--extensions", extension)


@pytest.fixture(scope="function")
def bad_file(testfiles):
    return (testfiles / "overrides" / "without-overrides.cmake").resolve()


@pytest.fixture(scope="function")
def good_file(testfiles):
    return (testfiles / "overrides" / "with-overrides.cmake").resolve()


def test_extension_can_override_builtins(app, bad_file, good_file):
    assert app("--check", "--", bad_file) == fail(
        stdout="",
        stderr=f"""{bad_file} would be reformatted
""",
    )

    assert app("--check", "--", good_file) == success(stdout="", stderr="")
