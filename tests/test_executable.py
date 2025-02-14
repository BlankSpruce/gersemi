# pylint: disable=too-many-lines
from contextlib import contextmanager, ExitStack
import filecmp
from functools import partial
import os
from pathlib import Path
import sqlite3
from stat import S_IREAD, S_IRGRP, S_IROTH
import yaml
import pytest
from gersemi.return_codes import FAIL, SUCCESS
from tests.fixtures.app import ExpectedOutcome, fail, match_not, success


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


def test_help_just_works(app):
    assert app("--help") == success()


def test_check_on_formatted_file_should_return_zero(app, testfiles):
    assert app("--check", testfiles / "formatted_file.cmake") == success()


def test_check_on_not_formatted_file_should_return_one(app, testfiles):
    target = (testfiles / "not_formatted_file.cmake").resolve()
    assert app("--check", target) == fail(
        stdout="",
        stderr=f"""{target} would be reformatted
""",
    )


def test_diff_on_not_formatted_files_should_return_zero(app, testfiles):
    target = testfiles / "directory_with_not_formatted_files"
    assert app("--diff", target) == success(stdout=match_not(""), stderr="")


def test_check_with_diff_on_not_formatted_files_should_return_one(app, testfiles):
    target = testfiles / "directory_with_not_formatted_files"
    file1 = (target / "file1.cmake").resolve()
    file2 = (target / "file2.cmake").resolve()
    file3 = (target / "file3.cmake").resolve()

    assert app("--check", "--diff", target) == fail(
        stdout=match_not(""),
        stderr=f"""{file1} would be reformatted
{file2} would be reformatted
{file3} would be reformatted
""",
    )


def test_format_file_in_place(app, testfiles):
    f = testfiles / "not_formatted_file.cmake"
    assert app("--check", f) == fail()
    assert app("--in-place", f) == success()
    assert app("--check", f) == success()


def test_check_formatted_input_from_stdin(app):
    inp = """set(FOO BAR)
"""
    assert app("--check", "-", input=inp) == success()


def test_check_not_formatted_input_from_stdin(app):
    inp = """set(FOO BAR)"""  # missing newline at the end
    assert app("--check", "-", input=inp) == fail()


def test_format_formatted_input_from_stdin(app):
    inp = """set(FOO BAR)
"""
    assert app("-", input=inp) == success(stdout=inp, stderr="")


def test_format_not_formatted_input_from_stdin(app):
    inp = "set(FOO BAR)"  # missing newline at the end

    assert app("-", input=inp) == success(stdout=inp + "\n", stderr="")


def test_when_run_with_no_input_should_return_zero(app):
    # no args
    assert app() == success()


def test_dont_mix_stdin_and_file_input(app, testfiles):
    f = testfiles / "formatted_file.cmake"
    assert app(f, "-") == fail(stderr="Don't mix stdin with file input\n")
    assert app("-", f) == fail(stderr="Don't mix stdin with file input\n")
    assert app(f, "-", f) == fail(stderr="Don't mix stdin with file input\n")


def test_check_multiple_formatted_input_files(app, testfiles):
    files = [
        testfiles / "directory_with_formatted_files" / f
        for f in ["file1.cmake", "file2.cmake", "file3.cmake"]
    ]
    assert app("--check", *files) == success()


def test_check_multiple_not_formatted_input_files(app, testfiles):
    files = [
        testfiles / "directory_with_not_formatted_files" / f
        for f in ["file1.cmake", "file2.cmake", "file3.cmake"]
    ]
    assert app("--check", *files) == fail()


def test_check_multiple_input_files_when_some_are_not_formatted(app, testfiles):
    files = [
        testfiles / "directory_with_some_not_formatted_files" / f
        for f in [
            "formatted_file1.cmake",
            "formatted_file2.cmake",
            "formatted_file3.cmake",
            "not_formatted_file1.cmake",
            "not_formatted_file2.cmake",
            "not_formatted_file3.cmake",
        ]
    ]
    assert app("--check", *files) == fail()


def test_check_directory_with_formatted_files(app, testfiles):
    assert app("--check", testfiles / "directory_with_formatted_files") == success()


def test_check_directory_with_not_formatted_files(app, testfiles):
    assert app("--check", testfiles / "directory_with_not_formatted_files") == fail()


def test_check_directory_with_some_not_formatted_files(app, testfiles):
    assert (
        app("--check", testfiles / "directory_with_some_not_formatted_files") == fail()
    )


def test_format_in_place_multiple_formatted_files(app, testfiles):
    files = [
        testfiles / "directory_with_formatted_files" / f
        for f in ["file1.cmake", "file2.cmake", "file3.cmake"]
    ]
    assert app("--check", *files) == success()
    assert app("--in-place", *files) == success()
    assert app("--check", *files) == success()


def test_format_in_place_multiple_not_formatted_files(app, testfiles):
    files = [
        testfiles / "directory_with_not_formatted_files" / f
        for f in ["file1.cmake", "file2.cmake", "file3.cmake"]
    ]
    assert app("--check", *files) == fail()
    assert app("--in-place", *files) == success()
    assert app("--check", *files) == success()


def test_format_in_place_multiple_input_files_when_some_are_not_formatted(
    app, testfiles
):
    files = [
        testfiles / "directory_with_some_not_formatted_files" / f
        for f in [
            "formatted_file1.cmake",
            "formatted_file2.cmake",
            "formatted_file3.cmake",
            "not_formatted_file1.cmake",
            "not_formatted_file2.cmake",
            "not_formatted_file3.cmake",
        ]
    ]
    formatted, not_formatted = files[:3], files[3:]

    assert app("--check", *formatted) == success()
    assert app("--check", *not_formatted) == fail()
    assert app("--in-place", *formatted, *not_formatted) == success()
    assert app("--check", *formatted, *not_formatted) == success()


def test_format_in_place_directory_with_formatted_files(app, testfiles):
    d = testfiles / "directory_with_formatted_files"
    assert app("--check", d) == success()
    assert app("--in-place", d) == success()
    assert app("--check", d) == success()


def test_format_in_place_directory_with_not_formatted_files(app, testfiles):
    d = testfiles / "directory_with_not_formatted_files"
    assert app("--check", d) == fail()
    assert app("--in-place", d) == success()
    assert app("--check", d) == success()


def test_format_in_place_directory_with_some_not_formatted_files(app, testfiles):
    d = testfiles / "directory_with_some_not_formatted_files"
    assert app("--check", d) == fail()
    assert app("--in-place", d) == success()
    assert app("--check", d) == success()


def test_format_with_default_line_length(app):
    inp = "set(FOO long_argument__________________________________________________________)"
    assert len(inp) == 80
    assert app("-", input=inp) == success(stdout=inp + "\n", stderr="")

    inp2 = "set(FOO long_argument____________________________________________________________)"
    outp2 = """set(FOO
    long_argument____________________________________________________________
)
"""
    assert len(inp2) > 80
    assert app("-", input=inp2) == success(stdout=outp2, stderr="")


def test_format_with_non_default_line_length(app):
    line_length = 30
    inp = "set(FOO long_argument________)"
    assert len(inp) == line_length
    assert app("--line-length", line_length, "-", input=inp) == success(
        stdout=inp + "\n", stderr=""
    )

    inp2 = "set(FOO long_argument__________)"
    outp2 = """set(FOO
    long_argument__________
)
"""
    assert len(inp2) > line_length
    assert app("--line-length", line_length, "-", input=inp2) == success(
        stdout=outp2, stderr=""
    )


def test_check_project_with_custom_commands(app, testfiles):
    not_formatted = testfiles / "custom_project" / "not_formatted"
    assert app("--check", not_formatted, "--definitions", not_formatted) == fail()

    formatted = testfiles / "custom_project" / "formatted"
    assert app("--check", formatted, "--definitions", formatted) == success()


def test_check_project_with_custom_commands_but_without_definitions(app, testfiles):
    not_formatted = testfiles / "custom_project" / "not_formatted"
    assert app("--check", not_formatted) == fail()

    formatted = testfiles / "custom_project" / "only_custom_commands_not_formatted"
    assert app("--check", formatted) == success()


def test_format_project_with_custom_commands(app, testfiles):
    not_formatted = testfiles / "custom_project" / "not_formatted"
    formatted = testfiles / "custom_project" / "formatted"

    assert_that_directories_differ(not_formatted, formatted)
    assert app("--check", formatted, "--definitions", formatted) == success()
    assert app("--check", not_formatted, "--definitions", not_formatted) == fail()
    assert app("--in-place", not_formatted, "--definitions", not_formatted) == success()
    assert_that_directories_have_the_same_content(not_formatted, formatted)


def test_format_project_with_custom_commands_but_without_definitions(app, testfiles):
    not_formatted = testfiles / "custom_project" / "not_formatted"
    formatted = testfiles / "custom_project" / "only_custom_commands_not_formatted"

    assert_that_directories_differ(not_formatted, formatted)
    assert app("--check", formatted) == success()
    assert app("--check", not_formatted) == fail()
    assert app("--in-place", not_formatted) == success()
    assert_that_directories_have_the_same_content(not_formatted, formatted)


def test_non_empty_stderr_when_files_are_not_formatted(app, testfiles):
    f = testfiles / "custom_project" / "not_formatted"
    assert app("--check", f) == fail(stdout="", stderr=match_not(""))


def test_empty_stderr_when_files_are_not_formatted_but_quiet_is_supplied(
    app, testfiles
):
    f = testfiles / "custom_project" / "not_formatted"
    assert app("--check", f, "--quiet") == fail(stderr="")


def test_project_with_dot_gersemirc_will_use_configuration_defined_in_file(
    app, testfiles
):
    not_formatted = testfiles / "custom_project" / "not_formatted"
    formatted = testfiles / "custom_project" / "formatted_with_line_length_100"

    assert_that_directories_differ(not_formatted, formatted)

    def creator(dirname):
        return {"line_length": 100, "definitions": [str(dirname)]}

    with create_configuration_files([not_formatted, formatted], creator):
        assert app("--check", formatted) == success()
        assert app("--check", not_formatted) == fail()
        assert app("--in-place", not_formatted) == success()

    assert_that_directories_have_the_same_content(not_formatted, formatted)


def test_line_length_from_command_line_takes_precedence_over_configuration_file(
    app, testfiles
):
    formatted = testfiles / "custom_project" / "formatted_with_line_length_100"

    app_ = partial(app, "--check", formatted, "--definitions", formatted)

    # without configuration file
    assert app_() == fail()
    assert app_("--line-length", "100") == success()
    assert app_("--line-length", "80") == fail()

    # with configuration file
    with create_dot_gersemirc(where=formatted, line_length=100):
        assert app_() == success()
        assert app_("--line-length", "100") == success()
        assert app_("--line-length", "80") == fail()

    # and without configuration file again
    assert app_() == fail()
    assert app_("--line-length", "100") == success()
    assert app_("--line-length", "80") == fail()


def test_definitions_from_command_line(app, testfiles):
    not_formatted = testfiles / "custom_project" / "not_formatted"
    formatted = testfiles / "custom_project" / "formatted"

    assert_that_directories_differ(not_formatted, formatted)
    assert app("--check", formatted, "--definitions", formatted) == success()
    assert app("--check", not_formatted, "--definitions", not_formatted) == fail()
    assert app("--in-place", not_formatted, "--definitions", not_formatted) == success()
    assert_that_directories_have_the_same_content(not_formatted, formatted)


def test_definitions_from_command_line_take_precedence_over_configuration_file_with_no_definitions(
    app, testfiles
):
    not_formatted = testfiles / "custom_project" / "not_formatted"
    formatted = testfiles / "custom_project" / "formatted"

    def empty_creator(_):
        return {}

    assert_that_directories_differ(not_formatted, formatted)

    with create_configuration_files([not_formatted, formatted], empty_creator):
        assert app("--check", formatted) == success()
        assert app("--check", not_formatted) == fail()
        assert app("--in-place", not_formatted) == success()

    assert_that_directories_differ(not_formatted, formatted)


def test_missing_definitions_in_configuration_file_but_provided_from_command_line(
    app, testfiles
):
    not_formatted = testfiles / "custom_project" / "not_formatted"
    formatted = testfiles / "custom_project" / "formatted"

    def empty_creator(_):
        return {}

    assert_that_directories_differ(not_formatted, formatted)

    with create_configuration_files([not_formatted, formatted], empty_creator):
        assert app("--check", formatted, "--definitions", formatted) == success()
        assert app("--check", not_formatted, "--definitions", not_formatted) == fail()
        assert (
            app("--in-place", not_formatted, "--definitions", not_formatted)
            == success()
        )

    assert_that_directories_have_the_same_content(not_formatted, formatted)


def test_best_definitions_in_configuration_file_but_overridden_by_command_line(
    app, testfiles
):
    not_formatted = testfiles / "custom_project" / "not_formatted"
    formatted = testfiles / "custom_project" / "formatted"

    assert_that_directories_differ(not_formatted, formatted)

    def creator(dirname):
        return {"definitions": [str(dirname)]}

    with create_configuration_files([not_formatted, formatted], creator):
        with ExitStack() as fake_definitions:
            definitions_in_not_formatted, definitions_in_formatted = [
                fake_definitions.enter_context(
                    create_fake_definitions(where=dirname, name="definitions.cmake")
                )
                for dirname in map(str, [not_formatted, formatted])
            ]

            assert (
                app("--check", formatted, "--definitions", definitions_in_formatted)
                == success()
            )
            assert (
                app(
                    "--check",
                    not_formatted,
                    "--definitions",
                    definitions_in_not_formatted,
                )
                == fail()
            )
            assert (
                app(
                    "--in-place",
                    not_formatted,
                    "--definitions",
                    definitions_in_not_formatted,
                )
                == success()
            )

    assert_that_directories_differ(not_formatted, formatted)


def test_use_paths_relative_to_root_as_definitions_in_configuration_file(
    app, testfiles
):
    not_formatted = testfiles / "custom_project" / "not_formatted"
    formatted = testfiles / "custom_project" / "formatted_with_line_length_100"

    assert_that_directories_differ(not_formatted, formatted)

    def creator(_):
        return {
            "line_length": 100,
            "definitions": [
                "back_to_the_future.cmake",
                "back_to_the_future_sequels.cmake",
            ],
        }

    with create_configuration_files([not_formatted, formatted], creator):
        assert app("--check", formatted) == success()
        assert app("--check", not_formatted) == fail()
        assert app("--in-place", not_formatted) == success()

    assert_that_directories_have_the_same_content(not_formatted, formatted)


def test_use_absolute_paths_as_definitions_in_configuration_file(app, testfiles):
    not_formatted = testfiles / "custom_project" / "not_formatted"
    formatted = testfiles / "custom_project" / "formatted_with_line_length_100"

    assert_that_directories_differ(not_formatted, formatted)

    def creator(dirname):
        return {
            "line_length": 100,
            "definitions": [
                os.path.join(dirname, "back_to_the_future.cmake"),
                os.path.join(dirname, "back_to_the_future_sequels.cmake"),
            ],
        }

    with create_configuration_files([not_formatted, formatted], creator):
        assert app("--check", formatted) == success()
        assert app("--check", not_formatted) == fail()
        assert app("--in-place", not_formatted) == success()

    assert_that_directories_have_the_same_content(not_formatted, formatted)


def test_use_configuration_file_from_current_directory_when_input_is_from_stdin(
    tmpdir, app
):
    line_length = 30
    inp = "set(FOO long_argument__________)"
    outp = """set(FOO
    long_argument__________
)
"""
    assert len(inp) > line_length
    with create_dot_gersemirc(where=tmpdir, line_length=30):
        assert app("-", input=inp, cwd=tmpdir) == success(stdout=outp, stderr="")


def test_use_configuration_file_from_parent_directory_when_input_is_from_stdin(
    tmpdir, app
):
    line_length = 30
    inp = "set(FOO long_argument__________)"
    outp = """set(FOO
    long_argument__________
)
"""
    assert len(inp) > line_length

    nested_directory = tmpdir.mkdir("foo").mkdir("bar")
    app_ = partial(app, cwd=nested_directory)

    assert app_("-", input=inp) == success(stdout=match_not(outp), stderr="")
    with create_dot_gersemirc(where=tmpdir, line_length=30):
        assert app("-", input=inp) == success(stdout=outp, stderr="")


def test_formatted_files_are_stored_in_cache_on_check(app, cache, testfiles):
    d = testfiles / "custom_project" / "formatted"
    cache.assert_that_has_no_tables()

    assert app("--check", d, "--definitions", d) == success()

    cache.assert_that_has_initialized_tables()

    assert len(cache.get_files()) > 0
    assert len(cache.get_formatted()) > 0


def test_not_formatted_files_are_not_stored_in_cache_on_check(app, cache, testfiles):
    d = testfiles / "custom_project" / "not_formatted"

    cache.assert_that_has_no_tables()

    assert app("--check", d, "--definitions", d) == fail()

    cache.assert_that_has_initialized_tables()
    assert len(cache.get_files()) == 0
    assert len(cache.get_formatted()) == 0


def test_not_formatted_files_are_stored_in_cache_after_formatting(
    app, cache, testfiles
):
    d = testfiles / "custom_project" / "not_formatted"

    cache.assert_that_has_no_tables()

    assert app("--in-place", d, "--definitions", d) == success()

    cache.assert_that_has_initialized_tables()
    assert len(cache.get_files()) > 0
    assert len(cache.get_formatted()) > 0


def test_formatted_files_in_cache_dont_get_updated_on_subsequent_run(
    app, cache, testfiles
):
    d = testfiles / "custom_project" / "not_formatted"

    cache.assert_that_has_no_tables()

    assert app("--in-place", d, "--definitions", d) == success()
    cache.assert_that_has_initialized_tables()
    assert len(cache.get_files()) > 0
    formatted_after_first_run = cache.get_formatted()
    assert len(formatted_after_first_run) > 0

    assert app("--in-place", d, "--definitions", d) == success()
    cache.assert_that_has_initialized_tables()
    assert len(cache.get_files()) > 0
    formatted_after_second_run = cache.get_formatted()
    assert len(formatted_after_second_run) > 0

    assert formatted_after_first_run == formatted_after_second_run


def test_different_configuration_leads_to_overriding_data_stored_in_cache(
    app, cache, testfiles
):
    d = testfiles / "custom_project" / "not_formatted"

    cache.assert_that_has_no_tables()

    assert app("--in-place", d, "--definitions", d) == success()
    cache.assert_that_has_initialized_tables()
    assert len(cache.get_files()) > 0
    formatted_after_first_run = cache.get_formatted()
    assert len(formatted_after_first_run) > 0

    assert app("--in-place", d, "--definitions", d, "--line-length", "100") == success()
    cache.assert_that_has_initialized_tables()
    assert len(cache.get_files()) > 0
    formatted_after_second_run = cache.get_formatted()
    assert len(formatted_after_first_run) > 0

    only_paths_from_first_run = [path for (path, *_) in formatted_after_first_run]
    only_paths_from_second_run = [path for (path, *_) in formatted_after_second_run]

    assert only_paths_from_first_run == only_paths_from_second_run
    assert formatted_after_first_run != formatted_after_second_run


def test_no_files_are_stored_in_cache_on_diff(app, cache, testfiles):
    d = testfiles / "custom_project" / "not_formatted"

    cache.assert_that_has_no_tables()
    assert app("--diff", d, "--definitions", d) == success(stdout=match_not(""))
    cache.assert_that_has_initialized_tables()
    assert len(cache.get_files()) == 0
    assert len(cache.get_formatted()) == 0


def test_when_cache_cant_be_modified_it_is_ignored(app, cache, testfiles):
    d = testfiles / "custom_project" / "formatted"
    os.chmod(cache.path, S_IREAD | S_IRGRP | S_IROTH)

    cache.assert_that_has_no_tables()
    assert app("--check", d, "--definitions", d) == success(stdout="", stderr="")
    cache.assert_that_has_no_tables()


def test_when_cache_is_malformed_it_is_ignored(app, cache, testfiles):
    d = testfiles / "custom_project" / "formatted"
    with open(cache.path, "wb") as c:
        c.write("foobarbaz1231212312312312313".encode("ascii"))
        c.flush()

    with pytest.raises(sqlite3.DatabaseError):
        cache.get_files()

    assert app("--check", d, "--definitions", d) == success(stdout="", stderr="")

    with pytest.raises(sqlite3.DatabaseError):
        cache.get_files()


def test_cache_is_not_updated_when_input_is_from_stdin(app, cache):
    inp = """set(FOO BAR)
"""
    cache.assert_that_has_no_tables()
    assert app("--check", "-", input=inp) == success()

    # first use initialized tables in cache
    cache.assert_that_has_initialized_tables()
    assert len(cache.get_files()) == 0
    assert len(cache.get_formatted()) == 0

    assert app("--check", "-", input=inp) == success()
    cache.assert_that_has_initialized_tables()
    assert len(cache.get_files()) == 0
    assert len(cache.get_formatted()) == 0


warning_params = [
    ("default", (), SUCCESS),
    ("warnings as errors", ("--warnings-as-errors",), FAIL),
]


@pytest.mark.parametrize(
    ["warning_args", "returncode"],
    [rest for __, *rest in warning_params],
    ids=[name for name, *__ in warning_params],
)
def test_check_project_with_conflicting_command_definitions(
    app, testfiles, warning_args, returncode
):
    base = testfiles / "conflicting_definitions"
    foo1 = (base / "foo1.cmake").resolve()
    foo2 = (base / "foo2.cmake").resolve()
    assert app(
        "--check", base, "--definitions", base, *warning_args
    ) == ExpectedOutcome(
        returncode=returncode,
        stdout="",
        stderr=f"""Warning: conflicting definitions for 'foo':
(used)    {foo1}:1:10
(ignored) {foo2}:1:10
(ignored) {foo2}:5:10
(ignored) {foo2}:9:10
""",
    )

    assert app(
        "--check", "--no-quiet", base, "--definitions", base, *warning_args
    ) == ExpectedOutcome(
        returncode=returncode,
        stdout="",
        stderr=f"""Warning: conflicting definitions for 'foo':
(used)    {foo1}:1:10
(ignored) {foo2}:1:10
(ignored) {foo2}:5:10
(ignored) {foo2}:9:10
""",
    )


def test_check_project_with_conflicting_command_definitions_dont_warn_when_quiet(
    app, testfiles
):
    base = testfiles / "conflicting_definitions"
    assert app("--check", "--quiet", base, "--definitions", base) == success(
        stdout="",
        stderr="",
    )


@pytest.mark.parametrize(
    ["warning_args", "returncode"],
    [rest for __, *rest in warning_params],
    ids=[name for name, *__ in warning_params],
)
def test_format_file_with_conflicting_command_definitions(
    app, testfiles, warning_args, returncode
):
    base = testfiles / "conflicting_definitions"
    foo1 = (base / "foo1.cmake").resolve()
    foo2 = (base / "foo2.cmake").resolve()
    assert app(
        f"{base}/CMakeLists.txt",
        "--definitions",
        base,
        "--list-expansion=favour-expansion",
        *warning_args,
    ) == ExpectedOutcome(
        returncode=returncode,
        stdout="""foo(ONE
    TWO x
    THREE
        y
        z
)
""",
        stderr=f"""Warning: conflicting definitions for 'foo':
(used)    {foo1}:1:10
(ignored) {foo2}:1:10
(ignored) {foo2}:5:10
(ignored) {foo2}:9:10
""",
    )


def test_cached_result_doesnt_inhibit_printing_in_stdout_mode(app, testfiles):
    f = testfiles / "formatted_file.cmake"

    with open(f, "r", encoding="utf-8") as fh:
        file_content = fh.read()

    assert app("--check", f) == success(stdout="")
    assert app(f) == success(stdout=file_content)


@pytest.mark.parametrize(
    ["warning_args", "returncode"],
    [rest for __, *rest in warning_params],
    ids=[name for name, *__ in warning_params],
)
@pytest.mark.parametrize(
    ["args", "check_cache"],
    [
        ((), False),
        (("--check",), True),
        (("--warn-about-unknown-commands", "--check"), True),
        (("--in-place",), True),
        (("--warn-about-unknown-commands", "--in-place"), True),
        (("--diff",), False),
    ],
)
def test_warn_about_unknown_commands(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    app, testfiles, cache, args, check_cache, warning_args, returncode
):
    target = testfiles / "warn_about_unknown_commands"
    cmakelists = target / "CMakeLists.txt"
    definitions = target / "watch_movies.cmake"

    if check_cache:
        cache.assert_that_has_no_tables()

    assert app(
        *args, cmakelists, "--definitions", definitions, *warning_args
    ) == success(stderr="")

    if check_cache:
        cache.assert_that_has_initialized_tables()
        assert len(cache.get_files()) > 0
        assert len(cache.get_formatted()) > 0

    cache.clear()

    if check_cache:
        cache.assert_that_has_no_tables()

    assert app(*args, cmakelists, *warning_args) == ExpectedOutcome(
        returncode=returncode,
        stderr=f"""Warning: unknown command 'watch_nolan_movies' used at:
{str(cmakelists.resolve())}:3:1
{str(cmakelists.resolve())}:8:5

Warning: unknown command 'watch_tarantino_movies' used at:
{str(cmakelists.resolve())}:6:5
{str(cmakelists.resolve())}:11:1

""",
    )

    if check_cache:
        cache.assert_that_has_initialized_tables()
        assert len(cache.get_files()) == 0
        assert len(cache.get_formatted()) == 0


@pytest.mark.parametrize(
    ["warning_args", "returncode"],
    [rest for __, *rest in warning_params],
    ids=[name for name, *__ in warning_params],
)
@pytest.mark.parametrize(
    ["args"],
    [
        ((),),
        (("--check",),),
        (("--diff",),),
    ],
)
def test_warn_about_unknown_commands_with_stdin(
    app, testfiles, args, warning_args, returncode
):
    target = testfiles / "warn_about_unknown_commands"
    definitions = target / "watch_movies.cmake"
    with open(target / "CMakeLists.txt", "r", encoding="utf-8") as f:
        content = f.read()

    assert app(
        *args, "-", "--definitions", definitions, *warning_args, input=content
    ) == success(stderr="")

    assert app(*args, "-", *warning_args, input=content) == ExpectedOutcome(
        returncode=returncode,
        stderr="""Warning: unknown command 'watch_nolan_movies' used at:
<stdin>:3:1
<stdin>:8:5

Warning: unknown command 'watch_tarantino_movies' used at:
<stdin>:6:5
<stdin>:11:1

""",
    )


@pytest.mark.parametrize(
    ["args", "check_cache"],
    [
        ((), False),
        (("--check",), True),
        (("--in-place",), True),
        (("--diff",), False),
    ],
)
def test_dont_warn_about_unknown_commands_when_definition_arent_required(
    app, testfiles, cache, args, check_cache
):
    target = testfiles / "warn_about_unknown_commands"
    cmakelists = target / "CMakeLists.txt"

    if check_cache:
        cache.assert_that_has_no_tables()

    assert app(*args, "--no-warn-about-unknown-commands", cmakelists) == success(
        stderr=""
    )

    if check_cache:
        cache.assert_that_has_initialized_tables()
        assert len(cache.get_files()) > 0
        assert len(cache.get_formatted()) > 0

    cache.clear()

    if check_cache:
        cache.assert_that_has_no_tables()

    with create_dot_gersemirc(where=target, warn_about_unknown_commands=False):
        assert app(*args, cmakelists) == success(stderr="")

    if check_cache:
        cache.assert_that_has_initialized_tables()
        assert len(cache.get_files()) > 0
        assert len(cache.get_formatted()) > 0

    cache.clear()

    if check_cache:
        cache.assert_that_has_no_tables()

    with create_dot_gersemirc(where=target, warn_about_unknown_commands=True):
        assert app(*args, "--no-warn-about-unknown-commands", cmakelists) == success(
            stderr=""
        )

    if check_cache:
        cache.assert_that_has_initialized_tables()
        assert len(cache.get_files()) > 0
        assert len(cache.get_formatted()) > 0


def test_cache_is_disabled(app, testfiles, cache):
    target = testfiles / "custom_project" / "formatted"
    common_args = ["--check", target, "--definitions", target]

    cache.assert_that_has_no_tables()
    assert app("--no-cache", *common_args) == success()
    cache.assert_that_has_no_tables()


def test_cache_is_enabled(app, testfiles, cache):
    target = testfiles / "custom_project" / "formatted"
    common_args = ["--check", target, "--definitions", target]

    def assert_that_cache_was_used():
        cache.assert_that_has_initialized_tables()
        assert len(cache.get_files()) > 0
        assert len(cache.get_formatted()) > 0

    # enabled by default
    cache.assert_that_has_no_tables()
    assert app(*common_args) == success()
    assert_that_cache_was_used()

    cache.clear()

    # enabled explicitly
    cache.assert_that_has_no_tables()
    assert app("--cache", *common_args) == success()
    assert_that_cache_was_used()


def test_definition_path_doesnt_exist(app, testfiles):
    project = testfiles / "custom_project"
    sources = project / "formatted"
    definitions = project / "formatted"
    common_args = ["--check", sources, "--definitions"]

    assert app(*common_args, definitions) == success()
    assert app(*common_args, project / "this_path_doesnt_exist") == fail()
    assert app(*common_args, definitions / ".." / "formatted") == success()
    assert app(*common_args, definitions / ".." / ".." / "formatted") == fail()

    definitions_as_files = [
        definitions / "back_to_the_future.cmake",
        definitions / "back_to_the_future_sequels.cmake",
    ]
    assert app(*common_args, *definitions_as_files) == success()

    definitions_as_files_with_path_that_doesnt_exist = [
        definitions / "back_to_the_future.cmake",
        definitions / "back_to_the_future_sequels.cmake",
        definitions / "back_to_the_future_four.cmake",
    ]
    assert (
        app(*common_args, *definitions_as_files_with_path_that_doesnt_exist) == fail()
    )


def test_source_path_doesnt_exist(app, testfiles):
    project = testfiles / "custom_project"
    sources = project / "formatted"
    definitions = project / "formatted"
    common_args = ["--check", sources, "--definitions"]

    assert app(*common_args, sources) == success()
    assert app(*common_args, Path(project) / "this_path_doesnt_exist") == fail()
    assert app(*common_args, sources / ".." / "formatted") == success()
    assert app(*common_args, definitions / ".." / ".." / "formatted") == fail()

    sources_as_files = [
        sources / "CMakeLists.txt",
        sources / "subdirectory_one" / "CMakeLists.txt",
        sources / "subdirectory_two" / "CMakeLists.txt",
    ]
    assert app(*common_args, *sources_as_files) == success()

    sources_as_files_with_path_that_doesnt_exist = [
        sources / "CMakeLists.txt",
        sources / "this_subdirectory_doesnt_exist" / "CMakeLists.txt",
        sources / "subdirectory_one" / "CMakeLists.txt",
        sources / "subdirectory_two" / "CMakeLists.txt",
    ]
    assert app(*common_args, *sources_as_files_with_path_that_doesnt_exist) == fail()


def test_just_works_with_not_supported_options_in_configuration_file(app, testfiles):
    f = testfiles / "directory_with_formatted_files"
    dotfile = (testfiles / ".gersemirc").resolve()
    with create_dot_gersemirc(where=testfiles, command_definitions=100):
        assert app("--check", f) == success(
            stdout="",
            stderr=f"{dotfile}: these options are not supported: command_definitions\n",
        )

    with create_dot_gersemirc(
        where=testfiles,
        line_length=80,
        kambei=1,
        katsushiro=2,
        list_expansion="favour-inlining",
        gorobei="3",
        heihachi=True,
    ):
        assert app("--check", f) == success(
            stdout="",
            # pylint: disable=line-too-long
            stderr=f"{dotfile}: these options are not supported: gorobei, heihachi, kambei, katsushiro\n",
        )

    with create_dot_gersemirc(
        where=testfiles,
        cache=False,
        color=True,
        workers=8,
        quiet=False,
        line_length=80,
        kyuzo=123,
        shichiroji="foo",
        kikuchiyo=["foo", "bar"],
    ):
        assert app("--check", f) == success(
            stdout="",
            # pylint: disable=line-too-long
            stderr=f"""{dotfile}: these options are supported only through command line: cache, color, quiet, workers
{dotfile}: these options are not supported: kikuchiyo, kyuzo, shichiroji
""",
        )


def test_when_quiet_not_supported_options_in_configuration_file_are_not_printed(
    app, testfiles
):
    f = testfiles / "formatted_file.cmake"
    with create_dot_gersemirc(where=testfiles, command_definitions=100):
        assert app("--quiet", "--check", f) == success(stdout="", stderr="")

    with create_dot_gersemirc(
        where=testfiles,
        line_length=80,
        kambei=1,
        katsushiro=2,
        list_expansion="favour-inlining",
        gorobei="3",
        heihachi=True,
    ):
        assert app("--quiet", "--check", f) == success(stdout="", stderr="")

    with create_dot_gersemirc(
        where=testfiles,
        cache=False,
        color=True,
        workers=8,
        quiet=False,
        line_length=80,
        kyuzo=123,
        shichiroji="foo",
        kikuchiyo=["foo", "bar"],
    ):
        assert app("--quiet", "--check", f) == success(stdout="", stderr="")


def test_each_file_uses_closest_configuration_file(app, testfiles):
    d = testfiles / "closest_configuration_file"
    assert app("--check", d) == success(stdout="", stderr="")


def test_each_file_uses_closest_configuration_file_with_some_not_supported_options(
    app, testfiles
):
    d = testfiles / "closest_configuration_file"
    d40 = d
    d60 = d / "60_different_config_than_root"
    d80 = (
        d
        / "mixed_config_80_subdirectory_40_files_not_in_subdirectory"
        / "80_subdirectory"
    )

    d40_dotfile = (d40 / ".gersemirc").resolve()
    d60_dotfile = (d60 / ".gersemirc").resolve()
    d80_dotfile = (d80 / ".gersemirc").resolve()

    with ExitStack() as config_files:

        def cf(**kwargs):
            config_files.enter_context(create_dot_gersemirc(**kwargs))

        cf(where=d80, line_length=80, cache=False, gorobei="3")
        cf(where=d40, line_length=40, command_definitions=100)
        cf(where=d60, line_length=60, kambei=100, katsushiro="abc")

        assert app("--check", d) == success(
            stdout="",
            stderr=f"""{d40_dotfile}: these options are not supported: command_definitions
{d60_dotfile}: these options are not supported: kambei, katsushiro
{d80_dotfile}: these options are supported only through command line: cache
{d80_dotfile}: these options are not supported: gorobei
""",
        )


def test_disable_formatting(app, testfiles):
    not_formatted = testfiles / "custom_project" / "not_formatted"

    assert app("--check", not_formatted) == fail()

    with create_dot_gersemirc(where=not_formatted, disable_formatting=True):
        assert app("--check", not_formatted) == success()
        assert app("--enable-formatting", "--check", not_formatted) == fail()
        assert app("--disable-formatting", "--check", not_formatted) == success()

    with create_dot_gersemirc(where=not_formatted, disable_formatting=False):
        assert app("--check", not_formatted) == fail()
        assert app("--enable-formatting", "--check", not_formatted) == fail()
        assert app("--disable-formatting", "--check", not_formatted) == success()


def test_disable_formatting_with_multiple_configuration_files_at_play(app, testfiles):
    d = testfiles / "closest_configuration_file"
    d40 = d
    d60 = d / "60_different_config_than_root"
    d80 = (
        d
        / "mixed_config_80_subdirectory_40_files_not_in_subdirectory"
        / "80_subdirectory"
    )

    def cf(**kwargs):
        config_files.enter_context(create_dot_gersemirc(**kwargs))

    with ExitStack() as config_files:
        cf(where=d40, line_length=60, disable_formatting=True)
        cf(where=d60, line_length=80, disable_formatting=True)
        cf(where=d80, line_length=100, disable_formatting=True)

        assert app("--check", d40) == success()
        assert app("--check", d60) == success()
        assert app("--check", d80) == success()
        assert app("--check", d) == success()

    with ExitStack() as config_files:
        cf(where=d40, line_length=70, disable_formatting=False)
        cf(where=d60, line_length=60, disable_formatting=False)
        cf(where=d80, line_length=80, disable_formatting=False)

        assert app("--check", d40) == fail()
        assert app("--check", d60) == success()
        assert app("--check", d80) == success()
        assert app("--check", d) == fail()

    with ExitStack() as config_files:
        cf(where=d80, line_length=100, disable_formatting=False)
        cf(where=d40, line_length=60, disable_formatting=False)
        cf(where=d60, line_length=80, disable_formatting=False)

        assert app("--check", d40) == fail()
        assert app("--check", d60) == fail()
        assert app("--check", d80) == fail()
        assert app("--check", d) == fail()


def test_config_parameter(app, testfiles):
    base = testfiles
    target = base / "directory_with_formatted_files"
    configuration_file_elsewhere = base / "directory_with_not_formatted_files"
    configuration_file = configuration_file_elsewhere / ".gersemirc"
    config = ["--config", configuration_file_elsewhere / ".gersemirc"]

    assert app("--check", target) == success(stderr="")
    assert app("-l", 100, "--check", target) == fail()

    with create_dot_gersemirc(where=configuration_file_elsewhere, line_length=100):
        assert app("--check", target) == success(stderr="")
        assert app("-l", 100, "--check", target) == fail()

        assert app(*config, "--check", target) == fail()
        assert app(*config, "-l", 80, "--check", target) == success(stderr="")

    with create_dot_gersemirc(
        where=configuration_file_elsewhere, line_length=100, color=True, kambei=314
    ):
        assert app("--check", target) == success(stderr="")
        assert app("-l", 100, "--check", target) == fail()

        assert app(*config, "--check", target) == fail()
        assert app(*config, "-l", 80, "--check", target) == success(
            # pylint: disable=line-too-long
            stderr=f"""{configuration_file}: these options are supported only through command line: color
{configuration_file}: these options are not supported: kambei
"""
        )
