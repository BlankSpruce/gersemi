from contextlib import contextmanager
import os
import shutil
import subprocess
import tempfile


def gersemi(*args):
    return subprocess.run(["gersemi", *args], check=False)


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


def test_help_just_works():
    assert gersemi("--help").returncode == 0


def test_check_on_formatted_file_should_return_zero():
    assert gersemi("--check", case("formatted_file.cmake")).returncode == 0


def test_check_on_not_formatted_file_should_return_one():
    assert gersemi("--check", case("not_formatted_file.cmake")).returncode == 1


def test_format_file_in_place():
    with temporary_copy(case("not_formatted_file.cmake")) as copy:
        assert gersemi("--check", copy).returncode == 1
        gersemi("--in-place", copy)
        assert gersemi("--check", copy).returncode == 0
