# pylint: disable=redefined-outer-name
from functools import partial
import pytest
from tests.fixtures.app import success


@pytest.fixture(scope="function")
def base_directory(testfiles):
    return testfiles / "extensions" / "example"


@pytest.fixture(scope="function")
def app(app):
    return partial(app, "--extensions", "extension_example")


@pytest.mark.parametrize("case", ["favour-inlining", "favour-expansion"])
def test_extension_example(app, base_directory, case):
    file_to_format = base_directory / "code_to_format" / f"{case}.cmake"
    with open(file_to_format, "r", encoding="utf-8") as f:
        code = f.read()

    assert app("--list-expansion", case, "--", file_to_format) == success(stdout=code)
    assert app("--list-expansion", case, "--check", file_to_format) == success()
