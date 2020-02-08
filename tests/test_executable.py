from contextlib import contextmanager, ExitStack
import os
import shutil
import subprocess
import sys
import tempfile


def gersemi(*gersemi_args, **subprocess_kwargs):
    return subprocess.run(
        [sys.executable, "-m", "gersemi", *gersemi_args],
        check=False,
        **subprocess_kwargs,
    )


THIS_FILE_DIR = os.path.dirname(os.path.realpath(__file__))


def case(filepath):
    return f"{THIS_FILE_DIR}/executable/{filepath}"


@contextmanager
def temporary_copy(original):
    temp_directory = tempfile.gettempdir()
    original_base = os.path.basename(original)
    temp_path = os.path.join(temp_directory, original_base)
    try:
        shutil.copy2(original, temp_path)
        yield temp_path
    finally:
        os.remove(temp_path)


@contextmanager
def temporary_dir_copy(original):
    temp_directory = tempfile.gettempdir()
    original_base = os.path.basename(original)
    temp_path = os.path.join(temp_directory, original_base)
    try:
        shutil.copytree(original, temp_path)
        yield temp_path
    finally:
        shutil.rmtree(temp_path)


def assert_success(*args, **kwargs):
    assert gersemi(*args, **kwargs).returncode == 0


def assert_fail(*args, **kwargs):
    assert gersemi(*args, **kwargs).returncode == 1


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
    case_ = lambda filename: case("/directory_with_formatted_files/" + filename)
    with ExitStack() as stack:
        files = ["file1.cmake", "file2.cmake", "file3.cmake"]
        copies = [stack.enter_context(temporary_copy(case_(f))) for f in files]
        assert_success("--check", *copies)
        gersemi("--in-place", *copies)
        assert_success("--check", *copies)


def test_format_in_place_multiple_not_formatted_files():
    case_ = lambda filename: case("/directory_with_not_formatted_files/" + filename)
    with ExitStack() as stack:
        files = ["file1.cmake", "file2.cmake", "file3.cmake"]
        copies = [stack.enter_context(temporary_copy(case_(f))) for f in files]
        assert_fail("--check", *copies)
        gersemi("--in-place", *copies)
        assert_success("--check", *copies)


def test_format_in_place_multiple_input_files_when_some_are_not_formatted():
    case_ = lambda filename: case(
        "/directory_with_some_not_formatted_files/" + filename
    )
    with ExitStack() as stack:
        formatted_files = [
            "formatted_file1.cmake",
            "formatted_file2.cmake",
            "formatted_file3.cmake",
        ]
        not_formatted_files = [
            "not_formatted_file1.cmake",
            "not_formatted_file2.cmake",
            "not_formatted_file3.cmake",
        ]
        formatted_copies = [
            stack.enter_context(temporary_copy(case_(f))) for f in formatted_files
        ]
        not_formatted_copies = [
            stack.enter_context(temporary_copy(case_(f))) for f in not_formatted_files
        ]

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
