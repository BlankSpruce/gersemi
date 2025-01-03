# pylint: disable=attribute-defined-outside-init
from functools import partial
from pathlib import Path
import pytest
from tests.fixtures.app import Matcher, success
from tests.test_executable import create_dot_gersemirc


def based_on_defaults(text):
    return f"## Outcome configuration based on defaults,\n## {text}\n"


def based_on_file(text, config_file):
    return f"## Outcome configuration based on {config_file},\n## {text}\n"


def args_equivalent_to_defaults():
    return based_on_defaults("none of the defaults are overridden.\n")


def file_equivalent_to_defaults(config_file):
    return based_on_file(
        "none of the defaults are overridden.\n", config_file=config_file
    )


def args_differ(text):
    part = based_on_defaults("following options differ from default configuration:")
    return f"{part}{text}\n\n"


def file_differs(text, config_file):
    part = based_on_file(
        "following options differ from default configuration:",
        config_file=config_file,
    )
    return f"{part}{text}\n\n"


class TestPrintConfigMinimalWithoutConfigurationFile:
    @pytest.fixture(autouse=True)
    def _fixtures(self, app, testfiles):
        self.app = partial(app, "--print-config", "minimal")
        self.target = testfiles / "directory_with_formatted_files"

    def test_no_args(self):
        assert self.app(self.target) == success(
            stdout=args_equivalent_to_defaults(), stderr=""
        )

    def test_override_line_length(self):
        assert self.app("-l", 123, self.target) == success(
            stdout=args_differ("line_length: 123"), stderr=""
        )

    def test_override_multiple_args(self):
        assert self.app("-l", 123, "--indent", "tabs", self.target) == success(
            stdout=args_differ("indent: tabs\nline_length: 123"), stderr=""
        )


class TestPrintConfigMinimalWithConfigurationFile:
    @pytest.fixture(autouse=True)
    def _fixtures(self, app, testfiles):
        self.app = partial(app, "--print-config", "minimal")
        self.target = testfiles / "directory_with_formatted_files"
        self.elsewhere = testfiles / "directory_with_not_formatted_files"
        self.dotfile = (self.target / ".gersemirc").resolve()
        self.dotfile_elsewhere = (self.elsewhere / ".gersemirc").resolve()

    @property
    def file_equivalent_to_defaults(self):
        return file_equivalent_to_defaults(config_file=self.dotfile)

    def file_differs(self, text, config_file=None):
        if config_file is None:
            return file_differs(text, self.dotfile)
        return file_differs(text, config_file)

    def test_empty_file(self):
        with create_dot_gersemirc(where=self.target):
            assert self.app(self.target) == success(
                stdout=self.file_equivalent_to_defaults, stderr=""
            )

    def test_defaults_set_explicitly_in_file(self):
        with create_dot_gersemirc(
            where=self.target,
            line_length=80,
            indent=4,
            unsafe=False,
            disable_formatting=False,
        ):
            assert self.app(self.target) == success(
                stdout=self.file_equivalent_to_defaults, stderr=""
            )

    def test_file_with_line_length(self):
        with create_dot_gersemirc(where=self.target, line_length=345):
            assert self.app(self.target) == success(
                stdout=self.file_differs("line_length: 345"), stderr=""
            )

    def test_file_with_definitions(self):
        with create_dot_gersemirc(
            where=self.target,
            definitions=[
                str(self.target),
                str(self.elsewhere),
            ],
        ):
            assert self.app(self.target) == success(
                stdout=self.file_differs(
                    f"""definitions:
- {Path('.')}
- {Path('../directory_with_not_formatted_files')}"""
                ),
                stderr="",
            )

    def test_file_with_multiple_options(self):
        with create_dot_gersemirc(
            where=self.target, unsafe=True, list_expansion="favour-expansion"
        ):
            assert self.app(self.target) == success(
                stdout=self.file_differs(
                    "list_expansion: favour-expansion\nunsafe: true"
                ),
                stderr="",
            )

    def test_file_and_line_length_from_command_line(self):
        with create_dot_gersemirc(
            where=self.target, unsafe=True, list_expansion="favour-expansion"
        ):
            assert self.app("--line-length", 42, self.target) == success(
                stdout=self.file_differs(
                    "line_length: 42\nlist_expansion: favour-expansion\nunsafe: true"
                ),
                stderr="",
            )

    def test_file_provided_through_config_arg(self):
        with create_dot_gersemirc(
            where=self.elsewhere, line_length=314, disable_formatting=True
        ):
            assert self.app(self.target) == success(
                stdout=args_equivalent_to_defaults(), stderr=""
            )
            assert self.app("--config", self.dotfile_elsewhere, self.target) == success(
                stdout=self.file_differs(
                    "disable_formatting: true\nline_length: 314",
                    config_file=self.dotfile_elsewhere,
                ),
                stderr="",
            )


def test_print_config_minimal_with_multiple_configuration_files_at_play(app, testfiles):
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

    assert app("--print-config", "minimal", d) == success(
        stdout="".join(
            [
                file_differs("line_length: 40", config_file=d40_dotfile),
                file_differs("line_length: 60", config_file=d60_dotfile),
                file_equivalent_to_defaults(config_file=d80_dotfile),
            ]
        ),
        stderr="",
    )

    assert app("--print-config", "minimal", "--indent", "tabs", d) == success(
        stdout="".join(
            [
                file_differs("indent: tabs\nline_length: 40", config_file=d40_dotfile),
                file_differs("indent: tabs\nline_length: 60", config_file=d60_dotfile),
                file_differs("indent: tabs", config_file=d80_dotfile),
            ]
        ),
        stderr="",
    )


# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
def verbose_config(
    definitions=" []",
    disable_formatting="false",
    extensions=" []",
    indent=4,
    line_length=80,
    list_expansion="favour-inlining",
    unsafe="false",
    warn_about_unknown_commands="true",
):
    return f"""definitions:{definitions}
disable_formatting: {disable_formatting}
extensions:{extensions}
indent: {indent}
line_length: {line_length}
list_expansion: {list_expansion}
unsafe: {unsafe}
warn_about_unknown_commands: {warn_about_unknown_commands}"""


def ignore_schema(thing):
    def impl(other):
        filtered = [
            line for line in other.splitlines() if "yaml-language-server" not in line
        ]
        return "\n".join(filtered) == thing

    return Matcher(impl, f"ignore schema:\n{thing}")


def verbose_based_on_defaults(target_files, **kwargs):
    return ignore_schema(
        f"""## Outcome configuration based on defaults,
## it's applicable to these files:
{target_files}
##

{verbose_config(**kwargs)}
"""
    )


def verbose_based_on_file(config_file, target_files, **kwargs):
    return ignore_schema(
        f"""## Outcome configuration based on {config_file},
## it's applicable to these files:
{target_files}
##

{verbose_config(**kwargs)}
"""
    )


class TestPrintConfigVerboseWithoutConfigurationFile:
    @pytest.fixture(autouse=True)
    def _fixtures(self, app, testfiles):
        self.app = partial(app, "--print-config", "verbose")
        self.target = testfiles / "directory_with_formatted_files"
        self.target_files = f"""## - {(self.target / "file1.cmake").resolve()}
## - {(self.target / "file2.cmake").resolve()}
## - {(self.target / "file3.cmake").resolve()}"""

    def test_no_args(self):
        assert self.app(self.target) == success(
            stdout=verbose_based_on_defaults(self.target_files), stderr=""
        )

    def test_override_line_length(self):
        assert self.app("-l", 123, self.target) == success(
            stdout=verbose_based_on_defaults(self.target_files, line_length=123),
            stderr="",
        )

    def test_override_multiple_args(self):
        assert self.app("-l", 123, "--indent", "tabs", self.target) == success(
            stdout=verbose_based_on_defaults(
                self.target_files, indent="tabs", line_length=123
            ),
            stderr="",
        )


def verbose_file_equivalent_to_defaults(config_file, target_files):
    return verbose_based_on_file(config_file=config_file, target_files=target_files)


class TestPrintConfigVerboseWithConfigurationFile:
    @pytest.fixture(autouse=True)
    def _fixtures(self, app, testfiles):
        self.app = partial(app, "--print-config", "verbose")
        self.target = testfiles / "directory_with_formatted_files"
        self.elsewhere = testfiles / "directory_with_not_formatted_files"
        self.dotfile = (self.target / ".gersemirc").resolve()
        self.dotfile_elsewhere = (self.elsewhere / ".gersemirc").resolve()
        self.target_files = f"""## - {(self.target / "file1.cmake").resolve()}
## - {(self.target / "file2.cmake").resolve()}
## - {(self.target / "file3.cmake").resolve()}"""

    @property
    def file_equivalent_to_defaults(self):
        return verbose_based_on_file(
            config_file=self.dotfile, target_files=self.target_files
        )

    def based_on_file(self, config_file=None, **kwargs):
        if config_file is None:
            return verbose_based_on_file(self.dotfile, self.target_files, **kwargs)
        return verbose_based_on_file(config_file, self.target_files, **kwargs)

    def test_empty_file(self):
        with create_dot_gersemirc(where=self.target):
            assert self.app(self.target) == success(
                stdout=self.file_equivalent_to_defaults, stderr=""
            )

    def test_defaults_set_explicitly_in_file(self):
        with create_dot_gersemirc(
            where=self.target,
            line_length=80,
            indent=4,
            unsafe=False,
            disable_formatting=False,
        ):
            assert self.app(self.target) == success(
                stdout=self.file_equivalent_to_defaults, stderr=""
            )

    def test_file_with_line_length(self):
        with create_dot_gersemirc(where=self.target, line_length=345):
            assert self.app(self.target) == success(
                stdout=self.based_on_file(line_length=345), stderr=""
            )

    def test_file_with_definitions(self):
        with create_dot_gersemirc(
            where=self.target,
            definitions=[
                str(self.target),
                str(self.elsewhere),
            ],
        ):
            assert self.app(self.target) == success(
                stdout=self.based_on_file(
                    definitions=f"""
- {Path('.')}
- {Path('../directory_with_not_formatted_files')}"""
                ),
                stderr="",
            )

    def test_file_with_multiple_options(self):
        with create_dot_gersemirc(
            where=self.target, unsafe=True, list_expansion="favour-expansion"
        ):
            assert self.app(self.target) == success(
                stdout=self.based_on_file(
                    list_expansion="favour-expansion", unsafe="true"
                ),
                stderr="",
            )

    def test_file_and_line_length_from_command_line(self):
        with create_dot_gersemirc(
            where=self.target, unsafe=True, list_expansion="favour-expansion"
        ):
            assert self.app("--line-length", 42, self.target) == success(
                stdout=self.based_on_file(
                    line_length=42, list_expansion="favour-expansion", unsafe="true"
                ),
                stderr="",
            )

    def test_file_provided_through_config_arg(self):
        with create_dot_gersemirc(
            where=self.elsewhere, line_length=314, disable_formatting=True
        ):
            assert self.app(self.target) == success(
                stdout=verbose_based_on_defaults(self.target_files), stderr=""
            )
            assert self.app("--config", self.dotfile_elsewhere, self.target) == success(
                stdout=self.based_on_file(
                    self.dotfile_elsewhere,
                    disable_formatting="true",
                    line_length=314,
                ),
                stderr="",
            )


def test_print_config_default(app):
    assert app("--print-config", "default") == success(
        stdout=ignore_schema(f"\n{verbose_config()}\n"), stderr=""
    )


class TestPrintConfigForStdin:
    @pytest.fixture(autouse=True)
    def _fixtures(self, app, tmpdir):
        self.app = partial(app, "--print-config")
        self.tmpdir = tmpdir

    def test_minimal_with_defaults(self):
        assert self.app("minimal", "-") == success(
            stdout=args_equivalent_to_defaults(),
            stderr="",
        )

    def test_minimal_with_args(self):
        assert self.app("minimal", "-l", 2718, "-") == success(
            stdout=args_differ("line_length: 2718"),
            stderr="",
        )

    def test_minimal_with_configuration_file(self):
        with create_dot_gersemirc(where=self.tmpdir, line_length=30):
            dotfile = (Path(self.tmpdir) / ".gersemirc").resolve()
            assert self.app("minimal", "-", cwd=self.tmpdir) == success(
                stdout=file_differs("line_length: 30", config_file=dotfile),
                stderr="",
            )

    def test_verbose_with_defaults(self):
        assert self.app("verbose", "-") == success(
            stdout=ignore_schema(
                f"""## Outcome configuration based on defaults,
## it's applicable to stdin.

{verbose_config()}
"""
            ),
            stderr="",
        )

    def test_verbose_with_args(self):
        assert self.app("verbose", "-l", 2718, "-") == success(
            stdout=ignore_schema(
                f"""## Outcome configuration based on defaults,
## it's applicable to stdin.

{verbose_config(line_length=2718)}
"""
            ),
            stderr="",
        )

    def test_verbose_with_configuration_file(self):
        with create_dot_gersemirc(where=self.tmpdir, line_length=30):
            dotfile = (Path(self.tmpdir) / ".gersemirc").resolve()
            assert self.app("verbose", "-", cwd=self.tmpdir) == success(
                stdout=ignore_schema(
                    f"""## Outcome configuration based on {dotfile},
## it's applicable to stdin.

{verbose_config(line_length=30)}
"""
                ),
                stderr="",
            )
