from contextlib import contextmanager
import os
import shutil
import subprocess
import tempfile


def gersemi(*gersemi_args, **subprocess_kwargs):
    return subprocess.run(["gersemi", *gersemi_args], check=False, **subprocess_kwargs)


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
