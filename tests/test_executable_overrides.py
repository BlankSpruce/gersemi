# pylint: disable=redefined-outer-name
from functools import partial
import pytest
from tests.fixtures.app import success


@pytest.fixture
def app(app, testfiles):
    extension = (testfiles / "overrides" / "extension.py").resolve()
    return partial(app, "--extensions", extension)


@pytest.fixture
def bad_file(testfiles):
    return (testfiles / "overrides" / "bad.cmake").resolve()


@pytest.fixture
def good_file(testfiles):
    return (testfiles / "overrides" / "good.cmake").resolve()


def test_extension_can_override_builtins(app, bad_file, good_file):
    assert app("-i", "--", bad_file) == success(stdout="", stderr="")

    with open(bad_file, "r", encoding="utf-8") as bad_f, open(
        good_file, "r", encoding="utf-8"
    ) as good_f:
        bad = bad_f.read()
        good = good_f.read()

        assert bad == good
