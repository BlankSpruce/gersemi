# pylint: disable=attribute-defined-outside-init,redefined-outer-name
from functools import partial
import json
import pytest
from tests.fixtures.app import success, fail


@pytest.fixture(scope="function")
def extensions_directory():
    return "extension_exists"


@pytest.fixture(scope="function")
def fake_extension():
    return {}


@pytest.fixture(scope="function")
def app(extensions_directory, fake_extension, testfiles, app):
    return partial(
        app,
        "--check",
        testfiles / "extensions" / "there_are_spoilers_ahead",
        env={
            "PYTHONPATH": testfiles / "extensions" / extensions_directory,
            "GERSEMI_FAKE_EXTENSION_SETTINGS": json.dumps(fake_extension),
        },
    )


@pytest.mark.parametrize("extensions_directory", ["no_extensions_directory"])
def test_extensions_directory_dont_exist(app):
    assert app("--extensions", "foo") == fail(stderr="Missing extension foo\n")

    assert app("--extensions", "baz", "foo", "bar") == fail(
        stderr="""Missing extension bar
Missing extension baz
Missing extension foo
"""
    )


class TestExtensionExists:
    @pytest.fixture(autouse=True)
    def _fixtures(self, app, testfiles):
        self.app = partial(app, "--extensions", "kim_dokja_company")

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
            stderr="Extension kim_dokja_company doesn't implement command_definitions\n"
        )

    @pytest.mark.parametrize(
        "fake_extension",
        [{"implementation_present": True}],
    )
    def test_fails_verification(self):
        assert self.app() == fail(
            stderr="""Verification failed for extension kim_dokja_company:
gersemi_kim_dokja_company.command_definitions: is not a mapping
"""
        )

    @pytest.mark.parametrize(
        "fake_extension",
        [{"implementation_present": True, "implementation_passes_verification": True}],
    )
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

    @pytest.mark.parametrize(
        "fake_extension",
        [
            {
                "implementation_present": True,
                "implementation_passes_verification": True,
                "implementations": ["add_constellation"],
            }
        ],
    )
    def test_only_some_commands_are_implemented(self):
        assert self.app() == fail(
            stderr=f"""Warning: unknown command 'add_nebula' used at:
{self.correct_formatting}:1:1

Warning: unknown command 'add_nebula' used at:
{self.wrong_formatting}:1:1

{self.wrong_formatting} would be reformatted
""",
        )

    @pytest.mark.parametrize(
        "fake_extension",
        [
            {
                "implementation_present": True,
                "implementation_passes_verification": True,
                "implementations": ["add_constellation", "add_nebula"],
            }
        ],
    )
    def test_all_commands_are_implemented(self):
        assert self.app() == fail(
            stderr=f"""{self.wrong_formatting} would be reformatted
""",
        )
