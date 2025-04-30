# pylint: disable=attribute-defined-outside-init,redefined-outer-name
from functools import partial
import json
import pytest
from tests.fixtures.app import success, fail
from tests.test_executable_print_config import ignore_schema


def extension(implementations):
    return {
        "implementation_present": True,
        "implementation_passes_verification": True,
        "implementations": implementations,
    }


BAD_EXTENSION = {"implementation_present": True}
GOOD_EXTENSION = extension(["add_constellation", "add_nebula"])


@pytest.fixture(scope="function")
def extensions_directory():
    return "extension_exists"


@pytest.fixture(scope="function")
def fake_extension():
    return {}


@pytest.fixture(scope="function")
def app(extensions_directory, fake_extension, testfiles, app):
    return lambda *args, **kwargs: app(
        *args,
        "--",
        testfiles / "extensions" / "there_are_spoilers_ahead",
        env={
            "PYTHONPATH": str(testfiles / "extensions" / extensions_directory),
            "GERSEMI_FAKE_EXTENSION_SETTINGS": json.dumps(fake_extension),
        },
        **kwargs,
    )


@pytest.mark.parametrize("extensions_directory", ["no_extensions_directory"])
def test_extensions_directory_dont_exist(app):
    assert app("--check", "--extensions", "foo") == fail(
        stderr="Missing extension foo\n"
    )

    assert app("--check", "--extensions", "baz", "foo", "bar") == fail(
        stderr="""Missing extension bar
Missing extension baz
Missing extension foo
"""
    )


@pytest.fixture(scope="function")
def kim_dokja_company_as_module():
    return {
        "name": "kim_dokja_company",
        "qualified_name": "gersemi_kim_dokja_company",
    }


@pytest.fixture(scope="function")
def kim_dokja_company_as_file(testfiles):
    value = str(testfiles / "extensions" / "kim_dokja_company_as_file.py")
    return {"name": value, "qualified_name": value}


@pytest.mark.parametrize(
    "extension_fixture",
    [
        "kim_dokja_company_as_module",
        "kim_dokja_company_as_file",
    ],
)
class TestExtensionExists:
    @pytest.fixture(autouse=True)
    def _fixtures(self, app, testfiles, request, extension_fixture):
        extension = request.getfixturevalue(extension_fixture)
        self.extension_name = extension["name"]
        self.extension_qualified_name = extension["qualified_name"]
        self.app = partial(app, "--check", "--extensions", self.extension_name)

        base_directory = (
            testfiles
            / "extensions"
            / "there_are_spoilers_ahead"
            / "you_have_been_warned"
            / "one_last_chance"
        )
        self.correct_formatting = base_directory / "correct_formatting.cmake"
        self.wrong_formatting = base_directory / "wrong_formatting.cmake"

    def test_doesnt_have_command_definitions(self):
        assert self.app() == fail(
            stderr=f"Extension {self.extension_name} doesn't implement command_definitions\n"
        )

    @pytest.mark.parametrize("fake_extension", [BAD_EXTENSION])
    def test_fails_verification(self):
        assert self.app() == fail(
            stderr=f"""Verification failed for extension {self.extension_name}:
{self.extension_qualified_name}:command_definitions: is not a mapping
"""
        )

    @pytest.mark.parametrize("fake_extension", [extension([])])
    def test_warn_about_unknown_commands(self):
        assert self.app() == success(
            stderr=f"""Warning: unknown command 'add_nebula' used at:
{self.correct_formatting}:1:1

Warning: unknown command 'add_constellation' used at:
{self.correct_formatting}:3:1
{self.correct_formatting}:12:1
{self.correct_formatting}:14:1

Warning: unknown command 'add_nebula' used at:
{self.wrong_formatting}:1:1

Warning: unknown command 'add_constellation' used at:
{self.wrong_formatting}:6:1
{self.wrong_formatting}:16:1
{self.wrong_formatting}:23:1

"""
        )

    @pytest.mark.parametrize("fake_extension", [extension(["add_constellation"])])
    def test_only_some_commands_are_implemented(self):
        assert self.app() == fail(
            stderr=f"""Warning: unknown command 'add_nebula' used at:
{self.correct_formatting}:1:1

Warning: unknown command 'add_nebula' used at:
{self.wrong_formatting}:1:1

{self.wrong_formatting} would be reformatted
""",
        )

    @pytest.mark.parametrize("fake_extension", [GOOD_EXTENSION])
    def test_all_commands_are_implemented(self):
        assert self.app() == fail(
            stderr=f"""{self.wrong_formatting} would be reformatted
""",
        )


@pytest.mark.parametrize(
    ["fake_extension", "outcome"],
    [
        (
            GOOD_EXTENSION,
            """## - [kim_dokja_company] additional recognized commands:
##   - add_constellation
##   - add_nebula
##""",
        ),
        (
            BAD_EXTENSION,
            """## - [kim_dokja_company] error:
##   Verification failed for extension kim_dokja_company:
##   gersemi_kim_dokja_company:command_definitions: is not a mapping
##""",
        ),
    ],
)
def test_print_config_verbose_with_extensions(app, testfiles, outcome):
    base = testfiles / "extensions" / "there_are_spoilers_ahead"
    applicable_files = [
        base / "CMakeLists.txt",
        base / "you_have_been_warned" / "CMakeLists.txt",
        base / "you_have_been_warned" / "one_last_chance" / "correct_formatting.cmake",
        base / "you_have_been_warned" / "one_last_chance" / "wrong_formatting.cmake",
    ]
    file_listing = "".join(f"\n## - {f.resolve()}" for f in applicable_files)

    expected_stdout = f"""## Outcome configuration based on defaults,
## it's applicable to these files:{file_listing}
##
## About extensions:
## - [yoo_joonghyuk_company] error:
##   Missing extension yoo_joonghyuk_company
##
{outcome}
## - [han_sooyoung_company] error:
##   Missing extension han_sooyoung_company
##

definitions: []
disable_formatting: false
extensions:
- yoo_joonghyuk_company
- kim_dokja_company
- han_sooyoung_company
indent: 4
line_length: 80
list_expansion: favour-inlining
unsafe: false
warn_about_unknown_commands: true
"""

    assert app(
        "--extensions",
        "yoo_joonghyuk_company",
        "kim_dokja_company",
        "han_sooyoung_company",
        "--print-config",
        "verbose",
    ) == success(stdout=ignore_schema(expected_stdout))
