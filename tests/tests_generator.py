import collections
import os
import pathlib


InputOnlyCase = collections.namedtuple("InputOnlyCase", ["name", "content"])
InputOutputCase = collections.namedtuple(
    "InputOutputCase", ["name", "given", "expected"]
)


def has_extension(expected_extension):
    def verify(filename):
        extension = "".join(pathlib.Path(filename).suffixes)
        return extension == expected_extension

    return verify


def get_directory_path(directory):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), directory)


def get_files_with_extension(directory, extension):
    files = os.listdir(get_directory_path(directory))
    return list(filter(has_extension(extension), files))


def remove_extension(filename):
    return filename.replace("".join(pathlib.Path(filename).suffixes), "")


def get_content(filename, directory):
    filepath = os.path.join(get_directory_path(directory), filename)
    with open(filepath, "r") as opened_file:
        return opened_file.read()


def create_tests_generator(cases):
    def tests_generator(metafunc):
        if "case" in metafunc.fixturenames:
            metafunc.parametrize(
                argnames="case", argvalues=cases, ids=[case.name for case in cases]
            )

    return tests_generator


def discover_input_only_cases(where, input_extension):
    return [
        InputOnlyCase(remove_extension(f), get_content(f, directory=where))
        for f in get_files_with_extension(where, input_extension)
    ]


def get_matching_output_filename(input_filename, output_extension):
    return "{}{}".format(remove_extension(input_filename), output_extension)


def make_input_output_case(input_filename, output_extension, where):
    output_filename = get_matching_output_filename(input_filename, output_extension)
    return InputOutputCase(
        remove_extension(input_filename),
        get_content(input_filename, directory=where),
        get_content(output_filename, directory=where),
    )


def discover_input_output_cases(where, input_extension, output_extension):
    input_files = get_files_with_extension(where, input_extension)
    output_files = get_files_with_extension(where, output_extension)
    for inp in input_files:
        matching_output_file = get_matching_output_filename(inp, output_extension)
        assert (
            matching_output_file in output_files
        ), "Incomplete input-output pair, missing {}".format(matching_output_file)

    return [make_input_output_case(inp, output_extension, where) for inp in input_files]


def generate_input_only_tests(where, input_extension):
    return create_tests_generator(discover_input_only_cases(where, input_extension))


def generate_input_output_tests(where, input_extension, output_extension):
    return create_tests_generator(
        discover_input_output_cases(where, input_extension, output_extension)
    )
