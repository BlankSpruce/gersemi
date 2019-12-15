import collections
from formatter.converter import convert_to_string
from helpers import get_files_with_extension, remove_extension, get_content


Case = collections.namedtuple("Case", ["filename", "given", "expected"])


def test_converter(parser, case):
    tree = parser.parse(case.given)
    assert convert_to_string(tree) == case.expected


def get_list_of_cases():
    input_files = get_files_with_extension(directory="inputs")
    output_files = get_files_with_extension(directory="converter")
    for inp, outp in zip(input_files, output_files):
        assert remove_extension(inp) == remove_extension(outp), "Incomplete input-output pair"

    return [
        Case(
            remove_extension(inp),
            get_content(inp, directory="inputs"),
            get_content(inp, directory="converter")
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
