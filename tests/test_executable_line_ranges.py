# pylint: disable=redefined-outer-name
import pytest
from tests.fixtures.app import fail, success
from tests.tests_generator import generate_input_output_tests

LR = "--line-ranges"


@pytest.fixture
def testfiles(testfiles):
    return testfiles / "line_ranges"


def test_line_range_with_no_files_succeeds(app):
    assert app(LR, "123-456") == success()


def test_line_range_with_two_files_fails(app, testfiles):
    given1 = testfiles / "simple--12-20.in.cmake"
    given2 = testfiles / "single-line--7-7.in.cmake"
    assert app(LR, "123-456", "--", given1, given2) == fail(
        stderr="""Line range formatting available only with one source file
""",
    )


def test_line_range_with_directory_with_more_than_one_file_fails(app, testfiles):
    assert app(LR, "123-456", "--", testfiles) == fail(
        stderr="""Line range formatting available only with one source file
""",
    )


def test_multiple_line_range_arguments(app, testfiles):
    given = testfiles / "simple--1-10,22-31.in.cmake"
    with open(testfiles / "simple--1-10,22-31.out.cmake", "r", encoding="utf-8") as f:
        expected = f.read()
        assert app(LR, "1-10,22-31", given) == success(stdout=expected)
        assert app(LR, "1-10", LR, "22-31", given) == success(stdout=expected)
        assert app(LR, "22-31", LR, "1-10", given) == success(stdout=expected)
        assert app(LR, "1-10,22-31", LR, "22-31", given) == success(stdout=expected)
        assert app(LR, "1-10,22-31", LR, "1-10,22-31", given) == success(
            stdout=expected
        )


def test_format_only_line_ranges(app, case):
    _, given_range = case.name.split("--")
    assert app(LR, given_range, "-", input=case.given) == success(stdout=case.expected)


pytest_generate_tests = generate_input_output_tests(
    where="executable/line_ranges",
    input_extension=".in.cmake",
    output_extension=".out.cmake",
)
