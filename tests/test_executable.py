# pylint: disable=unnecessary-lambda-assignment
from contextlib import contextmanager, ExitStack
import filecmp
import os
from pathlib import Path
import re
import shutil
from stat import S_IREAD, S_IRGRP, S_IROTH
import subprocess
import sys
import tempfile
import yaml
from tests.cache_inspector import inspect_cache


def gersemi_with_cache_path(cache_path, *gersemi_args, **subprocess_kwargs):
    this_file_dir = os.path.dirname(os.path.realpath(__file__))
    subprocess_kwargs["input"] = cache_path + "\n" + subprocess_kwargs.get("input", "")
    return subprocess.run(
        [sys.executable, f"{this_file_dir}/patched_gersemi", *gersemi_args],
        check=False,
        encoding="utf8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        **subprocess_kwargs,
    )


@contextmanager
def make_temporary_cache():
    with tempfile.TemporaryDirectory() as directory:
        temporary_cache = str(Path(directory) / "temporary_cache.db")
        yield temporary_cache


def gersemi(*gersemi_args, **subprocess_kwargs):
    with make_temporary_cache() as temporary_cache:
        return gersemi_with_cache_path(
            temporary_cache, *gersemi_args, **subprocess_kwargs
        )


HERE = os.path.dirname(os.path.realpath(__file__))


def case(filepath):
    return f"{HERE}/executable/{filepath}"


@contextmanager
def temporary_copy(original):
    with tempfile.TemporaryDirectory() as temp_directory:
        original_base = os.path.basename(original)
        temp_path = os.path.join(temp_directory, original_base)
        try:
            shutil.copy2(original, temp_path)
            yield temp_path
        finally:
            os.remove(temp_path)


@contextmanager
def temporary_copies(file_paths):
    with ExitStack() as stack:
        copies = [stack.enter_context(temporary_copy(p)) for p in file_paths]
        yield copies


@contextmanager
def temporary_dir_copy(original):
    with tempfile.TemporaryDirectory() as temp_directory:
        original_base = os.path.basename(original)
        temp_path = os.path.join(temp_directory, original_base)
        try:
            shutil.copytree(original, temp_path)
            yield temp_path
        finally:
            shutil.rmtree(temp_path)


@contextmanager
def temporary_dir_copies(directory_paths):
    with ExitStack() as stack:
        copies = [stack.enter_context(temporary_dir_copy(p)) for p in directory_paths]
        yield copies


def assert_success(*args, **kwargs):
    process = gersemi(*args, **kwargs)
    assert process.returncode == 0, (process.stdout, process.stderr)


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
        with open(p, "w", encoding="utf-8") as f:
            f.write(yaml.dump(kwargs))
        yield
    finally:
        os.remove(p)


@contextmanager
def create_fake_definitions(where, name):
    p = os.path.join(where, name)
    try:
        with open(os.path.join(where, name), "w", encoding="utf-8") as f:
            f.write("\n")
        yield p
    finally:
        os.remove(p)


@contextmanager
def create_configuration_files(directories, creator):
    with ExitStack() as stack:
        configuration_files = [
            stack.enter_context(create_dot_gersemirc(where=d, **creator(d)))
            for d in directories
        ]
        yield configuration_files


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
    with temporary_copy(case("formatted_file.cmake")) as copy:
        assert_success("--check", copy)


def test_check_on_not_formatted_file_should_return_one():
    with temporary_copy(case("not_formatted_file.cmake")) as copy:
        assert_fail("--check", copy)


def test_format_file_in_place():
    with temporary_copy(case("not_formatted_file.cmake")) as copy:
        assert_fail("--check", copy)
        gersemi("--in-place", copy)
        assert_success("--check", copy)


def test_check_formatted_input_from_stdin():
    inp = """set(FOO BAR)
"""
    assert_success("--check", "-", input=inp)


def test_check_not_formatted_input_from_stdin():
    inp = """set(FOO BAR)"""  # missing newline at the end
    assert_fail("--check", "-", input=inp)


def test_format_formatted_input_from_stdin():
    inp = """set(FOO BAR)
"""
    completed_process = gersemi("-", input=inp)
    assert completed_process.returncode == 0
    assert completed_process.stdout == inp
    assert completed_process.stderr == ""


def test_format_not_formatted_input_from_stdin():
    inp = "set(FOO BAR)"  # missing newline at the end

    completed_process = gersemi("-", input=inp)
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
    with temporary_copies(
        [case_("file1.cmake"), case_("file2.cmake"), case_("file3.cmake")]
    ) as copies:
        assert_success("--check", *copies)


def test_check_multiple_not_formatted_input_files():
    case_ = lambda filename: case("/directory_with_not_formatted_files/" + filename)
    with temporary_copies(
        [case_("file1.cmake"), case_("file2.cmake"), case_("file3.cmake")]
    ) as copies:
        assert_fail("--check", *copies)


def test_check_multiple_input_files_when_some_are_not_formatted():
    case_ = lambda filename: case(
        "/directory_with_some_not_formatted_files/" + filename
    )
    with temporary_copies(
        [
            case_("formatted_file1.cmake"),
            case_("formatted_file2.cmake"),
            case_("formatted_file3.cmake"),
            case_("not_formatted_file1.cmake"),
            case_("not_formatted_file2.cmake"),
            case_("not_formatted_file3.cmake"),
        ]
    ) as copies:
        assert_fail("--check", *copies)


def test_check_directory_with_formatted_files():
    with temporary_dir_copy(case("directory_with_formatted_files")) as copy:
        assert_success("--check", copy)


def test_check_directory_with_not_formatted_files():
    with temporary_dir_copy(case("directory_with_not_formatted_files")) as copy:
        assert_fail("--check", copy)


def test_check_directory_with_some_not_formatted_files():
    with temporary_dir_copy(case("directory_with_some_not_formatted_files")) as copy:
        assert_fail("--check", copy)


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


def test_format_with_default_line_length(tmpdir):
    inp = "set(FOO long_argument__________________________________________________________)"
    outp = inp + "\n"
    assert len(inp) == 80
    completed_process = gersemi("-", input=inp + "\n", cwd=tmpdir)
    assert completed_process.returncode == 0
    assert completed_process.stdout == outp
    assert completed_process.stderr == ""

    inp2 = "set(FOO long_argument____________________________________________________________)"
    outp2 = """set(FOO
    long_argument____________________________________________________________
)
"""
    assert len(inp2) > 80
    completed_process = gersemi("-", input=inp2 + "\n", cwd=tmpdir)
    assert completed_process.returncode == 0
    assert completed_process.stdout == outp2
    assert completed_process.stderr == ""


def test_format_with_non_default_line_length(tmpdir):
    line_length = 30
    inp = "set(FOO long_argument________)"
    outp = inp + "\n"
    assert len(inp) == line_length
    completed_process = gersemi(
        "--line-length",
        str(line_length),
        "-",
        input=inp + "\n",
        universal_newlines=True,
        cwd=tmpdir,
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
        universal_newlines=True,
        cwd=tmpdir,
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
    completed_process = gersemi("--check", case("custom_project/not_formatted"))
    assert completed_process.returncode == 1
    assert completed_process.stderr != ""


def test_empty_stderr_when_files_are_not_formatted_but_quiet_is_supplied():
    completed_process = gersemi(
        "--check",
        case("custom_project/not_formatted"),
        "--quiet",
        universal_newlines=True,
    )
    assert completed_process.returncode == 1
    assert completed_process.stderr == ""


def test_project_with_dot_gersemirc_will_use_configuration_defined_in_file():
    with temporary_dir_copies(
        case("custom_project/" + d)
        for d in ["not_formatted", "formatted_with_line_length_100"]
    ) as (not_formatted, formatted):
        assert_that_directories_differ(not_formatted, formatted)

        creator = lambda dirname: {"line_length": 100, "definitions": [dirname]}
        with create_configuration_files([not_formatted, formatted], creator):
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
        assert_fail("--check", not_formatted, "--definitions", not_formatted)
        assert_success("--in-place", not_formatted, "--definitions", not_formatted)
        assert_that_directories_have_the_same_content(not_formatted, formatted)

    # missing definitions in configuration file
    with temporary_dir_copies(directories) as (not_formatted, formatted):
        assert_that_directories_differ(not_formatted, formatted)

        creator = lambda _: {}
        with create_configuration_files([not_formatted, formatted], creator):
            assert_success("--check", formatted)
            assert_fail("--check", not_formatted)
            assert_success("--in-place", not_formatted)

        assert_that_directories_differ(not_formatted, formatted)

    # missing definitions in configuration file but provided from command line
    with temporary_dir_copies(directories) as (not_formatted, formatted):
        assert_that_directories_differ(not_formatted, formatted)

        creator = lambda _: {}
        with create_configuration_files([not_formatted, formatted], creator):
            assert_success("--check", formatted, "--definitions", formatted)
            assert_fail("--check", not_formatted, "--definitions", not_formatted)
            assert_success("--in-place", not_formatted, "--definitions", not_formatted)

        assert_that_directories_have_the_same_content(not_formatted, formatted)

    # best definitions are in configuration file but they are overriden by command line
    with temporary_dir_copies(directories) as (not_formatted, formatted):
        assert_that_directories_differ(not_formatted, formatted)

        creator = lambda dirname: {"definitions": [dirname]}
        with create_configuration_files([not_formatted, formatted], creator):
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


def test_use_paths_relative_to_root_as_definitions_in_configuration_file():
    with temporary_dir_copies(
        case("custom_project/" + d)
        for d in ["not_formatted", "formatted_with_line_length_100"]
    ) as (not_formatted, formatted):
        assert_that_directories_differ(not_formatted, formatted)

        creator = lambda dirname: {
            "line_length": 100,
            "definitions": [
                "back_to_the_future.cmake",
                "./back_to_the_future_sequels.cmake",
            ],
        }
        with create_configuration_files([not_formatted, formatted], creator):
            assert_success("--check", formatted)
            assert_fail("--check", not_formatted)
            assert_success("--in-place", not_formatted)

        assert_that_directories_have_the_same_content(not_formatted, formatted)


def test_use_absolute_paths_as_definitions_in_configuration_file():
    with temporary_dir_copies(
        case("custom_project/" + d)
        for d in ["not_formatted", "formatted_with_line_length_100"]
    ) as (not_formatted, formatted):
        assert_that_directories_differ(not_formatted, formatted)

        creator = lambda dirname: {
            "line_length": 100,
            "definitions": [
                os.path.join(dirname, "back_to_the_future.cmake"),
                os.path.join(dirname, "back_to_the_future_sequels.cmake"),
            ],
        }
        with create_configuration_files([not_formatted, formatted], creator):
            assert_success("--check", formatted)
            assert_fail("--check", not_formatted)
            assert_success("--in-place", not_formatted)

        assert_that_directories_have_the_same_content(not_formatted, formatted)


def test_use_configuration_file_from_current_directory_when_input_is_from_stdin(tmpdir):
    line_length = 30
    inp = "set(FOO long_argument__________)"
    outp = """set(FOO
    long_argument__________
)
"""
    assert len(inp) > line_length

    with create_dot_gersemirc(where=tmpdir, line_length=30):
        completed_process = gersemi("-", input=inp + "\n", cwd=tmpdir)
        assert completed_process.returncode == 0
        assert completed_process.stdout == outp
        assert completed_process.stderr == ""


def test_use_configuration_file_from_parent_directory_when_input_is_from_stdin(tmpdir):
    line_length = 30
    inp = "set(FOO long_argument__________)"
    outp = """set(FOO
    long_argument__________
)
"""
    assert len(inp) > line_length

    with create_dot_gersemirc(where=tmpdir, line_length=30):
        nested_directory = tmpdir.mkdir("foo").mkdir("bar")
        completed_process = gersemi("-", input=inp + "\n", cwd=nested_directory)
        assert completed_process.returncode == 0
        assert completed_process.stdout == outp
        assert completed_process.stderr == ""


@contextmanager
def cache_tests(files_to_format):
    with ExitStack() as stack:
        copy, temporary_cache = [
            stack.enter_context(temporary_dir_copy(files_to_format)),
            stack.enter_context(make_temporary_cache()),
        ]
        gersemi_ = lambda *args, **kwargs: gersemi_with_cache_path(
            temporary_cache, *args, **kwargs
        )
        inspector = stack.enter_context(inspect_cache(temporary_cache))
        yield copy, gersemi_, inspector


def test_formatted_files_are_stored_in_cache_on_check():
    with cache_tests(case("custom_project/formatted")) as (copy, gersemi_, inspector):
        inspector.assert_that_has_no_tables()

        gersemi_("--check", copy, "--definitions", copy)

        inspector.assert_that_has_initialized_tables()

        assert len(inspector.get_files()) > 0
        assert len(inspector.get_formatted()) > 0


def test_not_formatted_files_are_not_stored_in_cache_on_check():
    with cache_tests(case("custom_project/not_formatted")) as (
        copy,
        gersemi_,
        inspector,
    ):
        inspector.assert_that_has_no_tables()

        gersemi_("--check", copy, "--definitions", copy)

        inspector.assert_that_has_initialized_tables()
        assert len(inspector.get_files()) == 0
        assert len(inspector.get_formatted()) == 0


def test_not_formatted_files_are_stored_in_cache_after_formatting():
    with cache_tests(case("custom_project/not_formatted")) as (
        copy,
        gersemi_,
        inspector,
    ):
        inspector.assert_that_has_no_tables()

        gersemi_("--in-place", copy, "--definitions", copy)

        inspector.assert_that_has_initialized_tables()
        assert len(inspector.get_files()) > 0
        assert len(inspector.get_formatted()) > 0


def test_formatted_files_in_cache_dont_get_updated_on_subsequent_run():
    with cache_tests(case("custom_project/not_formatted")) as (
        copy,
        gersemi_,
        inspector,
    ):
        inspector.assert_that_has_no_tables()

        gersemi_("--in-place", copy, "--definitions", copy)
        inspector.assert_that_has_initialized_tables()
        assert len(inspector.get_files()) > 0
        formatted_after_first_run = inspector.get_formatted()
        assert len(formatted_after_first_run) > 0

        gersemi_("--in-place", copy, "--definitions", copy)
        inspector.assert_that_has_initialized_tables()
        assert len(inspector.get_files()) > 0
        formatted_after_second_run = inspector.get_formatted()
        assert len(formatted_after_second_run) > 0

        assert formatted_after_first_run == formatted_after_second_run


def test_different_configuration_leads_to_overriding_data_stored_in_cache():
    with cache_tests(case("custom_project/not_formatted")) as (
        copy,
        gersemi_,
        inspector,
    ):
        inspector.assert_that_has_no_tables()

        gersemi_("--in-place", copy, "--definitions", copy)
        inspector.assert_that_has_initialized_tables()
        assert len(inspector.get_files()) > 0
        formatted_after_first_run = inspector.get_formatted()
        assert len(formatted_after_first_run) > 0

        gersemi_("--in-place", copy, "--definitions", copy, "--line-length", "100")
        inspector.assert_that_has_initialized_tables()
        assert len(inspector.get_files()) > 0
        formatted_after_second_run = inspector.get_formatted()
        assert len(formatted_after_first_run) > 0

        only_paths_from_first_run = [path for (path, *_) in formatted_after_first_run]
        only_paths_from_second_run = [path for (path, *_) in formatted_after_second_run]

        assert only_paths_from_first_run == only_paths_from_second_run
        assert formatted_after_first_run != formatted_after_second_run


def test_no_files_are_stored_in_cache_on_diff():
    with cache_tests(case("custom_project/not_formatted")) as (
        copy,
        gersemi_,
        inspector,
    ):
        inspector.assert_that_has_no_tables()
        gersemi_("--diff", copy, "--definitions", copy)
        inspector.assert_that_has_initialized_tables()
        assert len(inspector.get_files()) == 0
        assert len(inspector.get_formatted()) == 0


def test_when_cache_cant_be_modified_it_is_ignored():
    with temporary_dir_copy(
        case("custom_project/formatted")
    ) as copy, tempfile.NamedTemporaryFile(mode="r") as cache_path:
        os.chmod(cache_path.name, S_IREAD | S_IRGRP | S_IROTH)

        gersemi_ = lambda *args, **kwargs: gersemi_with_cache_path(
            cache_path.name, *args, **kwargs
        )

        completed_process = gersemi_("--check", copy, "--definitions", copy)
        assert completed_process.returncode == 0
        assert completed_process.stdout == ""
        assert completed_process.stderr == ""


def test_when_cache_is_malformed_it_is_ignored():
    with temporary_dir_copy(
        case("custom_project/formatted")
    ) as copy, tempfile.NamedTemporaryFile() as cache_path:
        cache_path.write("foobarbaz1231212312312312313".encode("ascii"))
        cache_path.flush()

        gersemi_ = lambda *args, **kwargs: gersemi_with_cache_path(
            cache_path.name, *args, **kwargs
        )

        completed_process = gersemi_("--check", copy, "--definitions", copy)
        assert completed_process.returncode == 0
        assert completed_process.stdout == ""
        assert completed_process.stderr == ""


def test_cache_is_not_updated_when_input_is_from_stdin():
    inp = """set(FOO BAR)
"""
    with make_temporary_cache() as cache_path, inspect_cache(cache_path) as inspector:
        gersemi_ = lambda *args, **kwargs: gersemi_with_cache_path(
            cache_path, *args, **kwargs
        )

        inspector.assert_that_has_no_tables()
        gersemi_("--check", "-", input=inp)

        # first use initialized tables in cache
        inspector.assert_that_has_initialized_tables()
        assert len(inspector.get_files()) == 0
        assert len(inspector.get_formatted()) == 0

        gersemi_("--check", "-", input=inp)
        inspector.assert_that_has_initialized_tables()
        assert len(inspector.get_files()) == 0
        assert len(inspector.get_formatted()) == 0


def test_check_project_with_conflicting_command_definitions():
    with temporary_dir_copy(case("conflicting_definitions")) as copy:
        completed_process = gersemi("--check", copy, "--definitions", copy)
        assert completed_process.returncode == 0
        assert completed_process.stdout == ""
        assert re.search(
            """Warning: conflicting definitions for 'foo':
\\(used\\)    .*foo1\\.cmake:1:10
\\(ignored\\) .*foo2\\.cmake:1:10
\\(ignored\\) .*foo2\\.cmake:5:10
\\(ignored\\) .*foo2\\.cmake:9:10
""",
            completed_process.stderr,
            re.MULTILINE,
        )


def test_format_file_with_conflicting_command_definitions():
    with temporary_dir_copy(case("conflicting_definitions")) as copy:
        completed_process = gersemi(
            f"{copy}/CMakeLists.txt",
            "--definitions",
            copy,
            "--list-expansion=favour-expansion",
        )
        assert completed_process.returncode == 0
        assert (
            completed_process.stdout
            == """foo(ONE
    TWO x
    THREE
        y
        z
)
"""
        )
        assert re.search(
            """Warning: conflicting definitions for 'foo':
\\(used\\)    .*foo1\\.cmake:1:10
\\(ignored\\) .*foo2\\.cmake:1:10
\\(ignored\\) .*foo2\\.cmake:5:10
\\(ignored\\) .*foo2\\.cmake:9:10
""",
            completed_process.stderr,
            re.MULTILINE,
        )


def test_cached_result_doesnt_inhibit_printing_in_stdout_mode():
    with temporary_copy(
        case("formatted_file.cmake")
    ) as copy, make_temporary_cache() as cache_path:
        gersemi_ = lambda *args, **kwargs: gersemi_with_cache_path(
            cache_path, *args, **kwargs
        )

        check_run = gersemi_("--check", copy)
        assert check_run.returncode == 0, (
            check_run.stdout,
            check_run.stderr,
        )
        assert len(check_run.stdout) == 0, check_run.stdout

        subsequent_non_check_run = gersemi_(copy)
        assert subsequent_non_check_run.returncode == 0, (
            subsequent_non_check_run.stdout,
            subsequent_non_check_run.stderr,
        )

        with open(copy, "r", encoding="utf-8") as f:
            file_content = f.read()

        assert (
            subsequent_non_check_run.stdout == file_content
        ), subsequent_non_check_run.stdout
