import collections
import lark
import pytest
from helpers import get_files_with_extension, remove_extension, get_content


Case = collections.namedtuple("Case", ["filename", "content"])


def test_parser(parser, case):
    try:
        parser.parse(case.content)
    except lark.UnexpectedInput:
        pytest.fail("invalid input to parse")
        raise


def get_list_of_cases():
    files = get_files_with_extension(directory="parser")
    return [
        Case(remove_extension(f), get_content(f, directory="parser")) for f in files
    ]


def pytest_generate_tests(metafunc):
    if "case" in metafunc.fixturenames:
        cases = get_list_of_cases()
        metafunc.parametrize(
            argnames="case", argvalues=cases, ids=[c.filename for c in cases]
        )
