import pytest
from gersemi.custom_command_definition_finder import (
    find_custom_command_definitions,
    get_just_definitions,
)
from tests.utils import Formatter


def test_custom_command_without_keyworded_arguments_formatting():
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

    definitions = get_just_definitions(find_custom_command_definitions(given))
    formatter = Formatter(known_definitions=definitions)
    formatted, _ = formatter.format(given)

    assert formatted == expected


def test_custom_command_without_keyworded_arguments_with_disabled_reformatting():
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

    definitions = get_just_definitions(find_custom_command_definitions(given))
    formatter = Formatter(known_definitions=definitions)
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
def test_can_deal_with_empty_body_in_custom_command_definition(given):
    expected = """function(
    some_custom_command_without_keyworded_arguments
    only
    positional
    arguments
)
endfunction()
"""

    definitions = get_just_definitions(find_custom_command_definitions(given))
    formatter = Formatter(known_definitions=definitions)
    formatted, _ = formatter.format(given)

    assert formatted == expected
