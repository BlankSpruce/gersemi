import pytest
from tests.utils import Formatter


def test_custom_command_without_keyworded_arguments_formatting(tmp_path):
    given = """function(some_custom_command_without_keyworded_arguments only positional arguments)
    message(STATUS "some_custom_command_without_keyworded_arguments")
endfunction()

some_custom_command_without_keyworded_arguments(short positional arguments)

some_custom_command_without_keyworded_arguments(long__________________________________________________ positional__________________________________________________ arguments__________________________________________________)
"""

    expected = """function(
    some_custom_command_without_keyworded_arguments
    only
    positional
    arguments
)
    message(STATUS "some_custom_command_without_keyworded_arguments")
endfunction()

some_custom_command_without_keyworded_arguments(short positional arguments)

some_custom_command_without_keyworded_arguments(
    long__________________________________________________
    positional__________________________________________________
    arguments__________________________________________________
)
"""
    definition_file = tmp_path / "definition.cmake"
    definition_file.write_text(given)
    formatter = Formatter(definitions=[definition_file])
    formatted, _ = formatter.format(given)

    assert formatted == expected


def test_custom_command_without_keyworded_arguments_with_disabled_reformatting(
    tmp_path,
):
    given = """function(some_custom_command_without_keyworded_arguments only positional arguments)
    # gersemi: ignore
    message(STATUS "some_custom_command_without_keyworded_arguments")
endfunction()

some_custom_command_without_keyworded_arguments(short positional arguments)

some_custom_command_without_keyworded_arguments(long__________________________________________________ positional__________________________________________________ arguments__________________________________________________)
"""

    expected = """function(
    some_custom_command_without_keyworded_arguments
    only
    positional
    arguments
)
    # gersemi: ignore
    message(STATUS "some_custom_command_without_keyworded_arguments")
endfunction()

some_custom_command_without_keyworded_arguments(short positional arguments)

some_custom_command_without_keyworded_arguments(long__________________________________________________ positional__________________________________________________ arguments__________________________________________________)
"""

    definition_file = tmp_path / "definition.cmake"
    definition_file.write_text(given)
    formatter = Formatter(definitions=[definition_file])
    formatted, _ = formatter.format(given)

    assert formatted == expected


@pytest.mark.parametrize(
    "given",
    [
        """function(some_custom_command_without_keyworded_arguments only positional arguments)
endfunction()
""",
        """function(some_custom_command_without_keyworded_arguments only positional arguments)

endfunction()
""",
    ],
)
def test_can_deal_with_empty_body_in_custom_command_definition(given, tmp_path):
    expected = """function(
    some_custom_command_without_keyworded_arguments
    only
    positional
    arguments
)
endfunction()
"""
    definition_file = tmp_path / "definition.cmake"
    definition_file.write_text(given)
    formatter = Formatter(definitions=[definition_file])
    formatted, _ = formatter.format(given)

    assert formatted == expected
