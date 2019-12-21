import collections
from helpers import get_files_with_extension, remove_extension, get_content


Case = collections.namedtuple("Case", ["filename", "given", "expected"])


def test_formatter(formatter, case):
    assert formatter.format(case.given) == case.expected


def get_list_of_cases():
    input_files = get_files_with_extension(directory="formatter", extension=".in")
    output_files = get_files_with_extension(directory="formatter", extension=".out")
    for inp, outp in zip(input_files, output_files):
        assert remove_extension(inp) == remove_extension(outp), "Incomplete input-output pair"

    return [
        Case(
            remove_extension(inp),
            get_content(inp, directory="formatter"),
            get_content(outp, directory="formatter")
        ) for inp, outp in zip(input_files, output_files)
    ]


def pytest_generate_tests(metafunc):
    if 'case' in metafunc.fixturenames:
        cases = get_list_of_cases()
        metafunc.parametrize(
            argnames='case',
            argvalues=cases,
            ids=[c.filename for c in cases]
        )
