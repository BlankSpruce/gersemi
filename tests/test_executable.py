from contextlib import contextmanager, ExitStack
import filecmp
import os
import shutil
import subprocess
import sys
import tempfile
import uuid
import yaml


def gersemi(*gersemi_args, **subprocess_kwargs):
    return subprocess.run(
        [sys.executable, "-m", "gersemi", *gersemi_args],
        check=False,
        **subprocess_kwargs,
    )


HERE = os.path.dirname(os.path.realpath(__file__))


def case(filepath):
    return f"{HERE}/executable/{filepath}"


@contextmanager
def temporary_copy(original):
    temp_directory = tempfile.gettempdir()
    original_base = os.path.basename(original)
    temp_path = os.path.join(temp_directory, uuid.uuid4().hex + original_base)
    try:
        shutil.copy2(original, temp_path)
        yield temp_path
    finally:
        os.remove(temp_path)


@contextmanager
def temporary_copies(file_paths):
    with ExitStack() as stack:
        copies = [stack.enter_context(temporary_copy(p)) for p in file_paths]
        try:
            yield copies
        finally:
            pass


@contextmanager
def temporary_dir_copy(original):
    temp_directory = tempfile.gettempdir()
    original_base = os.path.basename(original)
    temp_path = os.path.join(temp_directory, uuid.uuid4().hex + original_base)
    try:
        shutil.copytree(original, temp_path)
        yield temp_path
    finally:
        shutil.rmtree(temp_path)


@contextmanager
def temporary_dir_copies(directory_paths):
    with ExitStack() as stack:
        copies = [stack.enter_context(temporary_dir_copy(p)) for p in directory_paths]
        try:
            yield copies
        finally:
            pass


def assert_success(*args, **kwargs):
    assert gersemi(*args, **kwargs).returncode == 0


def assert_fail(*args, **kwargs):
    assert gersemi(*args, **kwargs).returncode == 1


def compare_directories(left, right):
    comparison = filecmp.dircmp(left, right)
    return {
        "left_only": comparison.left_only,
        "right_only": comparison.right_only,
        "diff_files": comparison.diff_files,
        "funny_files": comparison.funny_files,
    }


@contextmanager
def create_dot_gersemirc(where, **kwargs):
    p = os.path.join(where, ".gersemirc")
    try:
        with open(p, "w") as f:
            f.write(yaml.dump(kwargs))
        yield
    finally:
        os.remove(p)


@contextmanager
def create_fake_definitions(where, name):
    p = os.path.join(where, name)
    try:
        with open(os.path.join(where, name), "w") as f:
            f.write("\n")
        yield p
    finally:
        os.remove(p)


def assert_that_directories_differ(left, right):
    comparison = compare_directories(left, right)
    for value in comparison.values():
        if len(value) > 0:
            return
    raise AssertionError("directories have the same content")


def assert_that_directories_have_the_same_content(left, right):
    comparison = compare_directories(left, right)
    report = []
    for key, value in comparison.items():
        if len(value) > 0:
            report += [f"{key}: {value}"]

    assert len(report) == 0, "directories differences:\n" + "\n".join(report)


def test_help_just_works():
    assert_success("--help")


def test_check_on_formatted_file_should_return_zero():
    assert_success("--check", case("formatted_file.cmake"))


def test_check_on_not_formatted_file_should_return_one():
    assert_fail("--check", case("not_formatted_file.cmake"))


def test_format_file_in_place():
    with temporary_copy(case("not_formatted_file.cmake")) as copy:
        assert_fail("--check", copy)
        gersemi("--in-place", copy)
        assert_success("--check", copy)


def test_check_formatted_input_from_stdin():
    inp = """set(FOO BAR)
"""
    assert_success("--check", "-", input=inp, text=True)


def test_check_not_formatted_input_from_stdin():
    inp = """set(FOO BAR)"""  # missing newline at the end
    assert_fail("--check", "-", input=inp, text=True)


def test_format_formatted_input_from_stdin():
    inp = """set(FOO BAR)
"""
    completed_process = gersemi("-", input=inp, text=True, capture_output=True)
    assert completed_process.returncode == 0
    assert completed_process.stdout == inp
    assert completed_process.stderr == ""


def test_format_not_formatted_input_from_stdin():
    inp = "set(FOO BAR)"  # missing newline at the end

    completed_process = gersemi("-", input=inp, text=True, capture_output=True)
    assert completed_process.returncode == 0
    assert completed_process.stdout == inp + "\n"
    assert completed_process.stderr == ""


def test_when_run_with_no_input_should_return_zero():
    assert_success()  # no args


def test_dont_mix_stdin_and_file_input():
    assert_fail(case("formatted_file.cmake"), "-")
    assert_fail("-", case("formatted_file.cmake"))
    assert_fail(case("formatted_file.cmake"), "-", case("formatted_file.cmake"))


def test_check_multiple_formatted_input_files():
    case_ = lambda filename: case("/directory_with_formatted_files/" + filename)
    assert_success(
        "--check", case_("file1.cmake"), case_("file2.cmake"), case_("file3.cmake"),
    )


def test_check_multiple_not_formatted_input_files():
    case_ = lambda filename: case("/directory_with_not_formatted_files/" + filename)
    assert_fail(
        "--check", case_("file1.cmake"), case_("file2.cmake"), case_("file3.cmake"),
    )


def test_check_multiple_input_files_when_some_are_not_formatted():
    case_ = lambda filename: case(
        "/directory_with_some_not_formatted_files/" + filename
    )
    assert_fail(
        "--check",
        case_("formatted_file1.cmake"),
        case_("formatted_file2.cmake"),
        case_("formatted_file3.cmake"),
        case_("not_formatted_file1.cmake"),
        case_("not_formatted_file2.cmake"),
        case_("not_formatted_file3.cmake"),
    )


def test_check_directory_with_formatted_files():
    assert_success("--check", case("directory_with_formatted_files"))


def test_check_directory_with_not_formatted_files():
    assert_fail("--check", case("directory_with_not_formatted_files"))


def test_check_directory_with_some_not_formatted_files():
    assert_fail("--check", case("directory_with_some_not_formatted_files"))


def test_format_in_place_multiple_formatted_files():
    files = ["file1.cmake", "file2.cmake", "file3.cmake"]
    with temporary_copies(
        case("/directory_with_formatted_files/" + f) for f in files
    ) as copies:
        assert_success("--check", *copies)
        gersemi("--in-place", *copies)
        assert_success("--check", *copies)


def test_format_in_place_multiple_not_formatted_files():
    files = ["file1.cmake", "file2.cmake", "file3.cmake"]
    with temporary_copies(
        case("/directory_with_not_formatted_files/" + f) for f in files
    ) as copies:
        assert_fail("--check", *copies)
        gersemi("--in-place", *copies)
        assert_success("--check", *copies)


def test_format_in_place_multiple_input_files_when_some_are_not_formatted():
    files = [
        "formatted_file1.cmake",
        "formatted_file2.cmake",
        "formatted_file3.cmake",
        "not_formatted_file1.cmake",
        "not_formatted_file2.cmake",
        "not_formatted_file3.cmake",
    ]
    with temporary_copies(
        case("/directory_with_some_not_formatted_files/" + f) for f in files
    ) as copies:
        formatted_copies, not_formatted_copies = copies[:3], copies[3:]
        assert_success("--check", *formatted_copies)
        assert_fail("--check", *not_formatted_copies)
        gersemi("--in-place", *formatted_copies, *not_formatted_copies)
        assert_success("--check", *formatted_copies, *not_formatted_copies)


def test_format_in_place_directory_with_formatted_files():
    with temporary_dir_copy(case("directory_with_formatted_files")) as copy:
        assert_success("--check", copy)
        gersemi("--in-place", copy)
        assert_success("--check", copy)


def test_format_in_place_directory_with_not_formatted_files():
    with temporary_dir_copy(case("directory_with_not_formatted_files")) as copy:
        assert_fail("--check", copy)
        gersemi("--in-place", copy)
        assert_success("--check", copy)


def test_format_in_place_directory_with_some_not_formatted_files():
    with temporary_dir_copy(case("directory_with_some_not_formatted_files")) as copy:
        assert_fail("--check", copy)
        gersemi("--in-place", copy)
        assert_success("--check", copy)


def test_format_with_default_line_length():
    inp = "set(FOO long_argument__________________________________________________________)"
    outp = inp + "\n"
    assert len(inp) == 80
    completed_process = gersemi("-", input=inp + "\n", text=True, capture_output=True)
    assert completed_process.returncode == 0
    assert completed_process.stdout == outp
    assert completed_process.stderr == ""

    inp2 = "set(FOO long_argument____________________________________________________________)"
    outp2 = """set(FOO
    long_argument____________________________________________________________
)
"""
    assert len(inp2) > 80
    completed_process = gersemi("-", input=inp2 + "\n", text=True, capture_output=True)
    assert completed_process.returncode == 0
    assert completed_process.stdout == outp2
    assert completed_process.stderr == ""


def test_format_with_non_default_line_length():
    line_length = 30
    inp = "set(FOO long_argument________)"
    outp = inp + "\n"
    assert len(inp) == line_length
    completed_process = gersemi(
        "--line-length",
        str(line_length),
        "-",
        input=inp + "\n",
        text=True,
        capture_output=True,
    )
    assert completed_process.returncode == 0
    assert completed_process.stdout == outp
    assert completed_process.stderr == ""

    inp2 = "set(FOO long_argument__________)"
    outp2 = """set(FOO
    long_argument__________
)
"""
    assert len(inp2) > line_length
    completed_process = gersemi(
        "--line-length",
        str(line_length),
        "-",
        input=inp2 + "\n",
        text=True,
        capture_output=True,
    )
    assert completed_process.returncode == 0
    assert completed_process.stdout == outp2
    assert completed_process.stderr == ""


def test_check_project_with_custom_commands():
    with temporary_dir_copy(case("custom_project/not_formatted")) as copy:
        assert_fail("--check", copy, "--definitions", copy)

    with temporary_dir_copy(case("custom_project/formatted")) as copy:
        assert_success("--check", copy, "--definitions", copy)


def test_check_project_with_custom_commands_but_without_definitions():
    with temporary_dir_copy(case("custom_project/not_formatted")) as copy:
        assert_fail("--check", copy)

    with temporary_dir_copy(
        case("custom_project/only_custom_commands_not_formatted")
    ) as copy:
        assert_success("--check", copy)


def test_format_project_with_custom_commands():
    with temporary_dir_copies(
        case("custom_project/" + d) for d in ["not_formatted", "formatted"]
    ) as (
        not_formatted,
        formatted,
    ):
        assert_that_directories_differ(not_formatted, formatted)
        assert_success("--check", formatted, "--definitions", formatted)
        assert_fail("--check", not_formatted, "--definitions", not_formatted)
        assert_success("--in-place", not_formatted, "--definitions", not_formatted)
        assert_that_directories_have_the_same_content(not_formatted, formatted)


def test_format_project_with_custom_commands_but_without_definitions():
    with temporary_dir_copies(
        case("custom_project/" + d)
        for d in ["not_formatted", "only_custom_commands_not_formatted"]
    ) as (not_formatted, formatted):
        assert_that_directories_differ(not_formatted, formatted)
        assert_success("--check", formatted)
        assert_fail("--check", not_formatted)
        assert_success("--in-place", not_formatted)
        assert_that_directories_have_the_same_content(not_formatted, formatted)


def test_non_empty_stderr_when_files_are_not_formatted():
    completed_process = gersemi(
        "--check", case("custom_project/not_formatted"), text=True, capture_output=True,
    )
    assert completed_process.returncode == 1
    assert completed_process.stderr != ""


def test_empty_stderr_when_files_are_not_formatted_but_quiet_is_supplied():
    completed_process = gersemi(
        "--check",
        case("custom_project/not_formatted"),
        "--quiet",
        text=True,
        capture_output=True,
    )
    assert completed_process.returncode == 1
    assert completed_process.stderr == ""


def test_project_with_dot_gersemirc_will_use_configuration_defined_in_file():
    with temporary_dir_copies(
        case("custom_project/" + d)
        for d in ["not_formatted", "formatted_with_line_length_100"]
    ) as (not_formatted, formatted):
        assert_that_directories_differ(not_formatted, formatted)

        with ExitStack() as configuration_files:
            for dirname in [not_formatted, formatted]:
                configuration_files.enter_context(
                    create_dot_gersemirc(
                        where=dirname, line_length=100, definitions=[dirname]
                    )
                )

            assert_success("--check", formatted)
            assert_fail("--check", not_formatted)
            assert_success("--in-place", not_formatted)

        assert_that_directories_have_the_same_content(not_formatted, formatted)


def test_line_length_from_command_line_takes_precedence_over_configuration_file():
    with temporary_dir_copy(
        case("custom_project/formatted_with_line_length_100")
    ) as formatted:
        # without configuration file
        assert_fail("--check", formatted, "--definitions", formatted)
        assert_success(
            "--line-length", "100", "--check", formatted, "--definitions", formatted
        )
        assert_fail(
            "--line-length", "80", "--check", formatted, "--definitions", formatted
        )

        # with configuration file
        with create_dot_gersemirc(where=formatted, line_length=100):
            assert_success("--check", formatted, "--definitions", formatted)
            assert_success(
                "--line-length", "100", "--check", formatted, "--definitions", formatted
            )
            assert_fail(
                "--line-length", "80", "--check", formatted, "--definitions", formatted
            )

        # and without configuration file again
        assert_fail("--check", formatted, "--definitions", formatted)

        assert_success(
            "--line-length", "100", "--check", formatted, "--definitions", formatted
        )
        assert_fail(
            "--line-length", "80", "--check", formatted, "--definitions", formatted
        )


def test_definitions_from_command_line_take_precedence_over_configuration_file():
    directories = [case("custom_project/" + d) for d in ["not_formatted", "formatted"]]

    with temporary_dir_copies(directories) as (not_formatted, formatted):
        assert_that_directories_differ(not_formatted, formatted)
        assert_success("--check", formatted, "--definitions", formatted)
        assert_fail(
            "--check", not_formatted, "--definitions", not_formatted,
        )
        assert_success(
            "--in-place", not_formatted, "--definitions", not_formatted,
        )
        assert_that_directories_have_the_same_content(not_formatted, formatted)

    # missing definitions in configuration file
    with temporary_dir_copies(directories) as (not_formatted, formatted):
        assert_that_directories_differ(not_formatted, formatted)

        with ExitStack() as configuration_files:
            for dirname in [not_formatted, formatted]:
                configuration_files.enter_context(create_dot_gersemirc(where=dirname))

            assert_success("--check", formatted)
            assert_fail("--check", not_formatted)
            assert_success("--in-place", not_formatted)

        assert_that_directories_differ(not_formatted, formatted)

    # missing definitions in configuration file but provided from command line
    with temporary_dir_copies(directories) as (not_formatted, formatted):
        assert_that_directories_differ(not_formatted, formatted)

        with ExitStack() as configuration_files:
            for dirname in [not_formatted, formatted]:
                configuration_files.enter_context(create_dot_gersemirc(where=dirname))

            assert_success("--check", formatted, "--definitions", formatted)
            assert_fail("--check", not_formatted, "--definitions", not_formatted)
            assert_success("--in-place", not_formatted, "--definitions", not_formatted)

        assert_that_directories_have_the_same_content(not_formatted, formatted)

    # best definitions are in configuration file but they are overriden by command line
    with temporary_dir_copies(directories) as (not_formatted, formatted):
        assert_that_directories_differ(not_formatted, formatted)

        with ExitStack() as configuration_files:
            for dirname in [not_formatted, formatted]:
                configuration_files.enter_context(
                    create_dot_gersemirc(where=dirname, definitions=[dirname])
                )

            with ExitStack() as fake_definitions:
                fake_definitions_in_not_formatted, fake_definitions_in_formatted = [
                    fake_definitions.enter_context(
                        create_fake_definitions(where=dirname, name="definitions.cmake")
                    )
                    for dirname in [not_formatted, formatted]
                ]

                assert_success(
                    "--check", formatted, "--definitions", fake_definitions_in_formatted
                )
                assert_fail(
                    "--check",
                    not_formatted,
                    "--definitions",
                    fake_definitions_in_not_formatted,
                )
                assert_success(
                    "--in-place",
                    not_formatted,
                    "--definitions",
                    fake_definitions_in_not_formatted,
                )

        assert_that_directories_differ(not_formatted, formatted)
