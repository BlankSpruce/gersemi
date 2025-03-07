import pytest
from gersemi.configuration import OutcomeConfiguration
from gersemi.custom_command_definition_finder import (
    find_custom_command_definitions,
    get_just_definitions,
)
from gersemi.dumper import Dumper


def create_dumper(definitions):
    return Dumper(
        configuration=OutcomeConfiguration(line_length=80, indent=4),
        known_definitions=definitions,
    )


def test_custom_command_without_keyworded_arguments_formatting(
    parser_with_postprocessing,
):
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

    parsed = parser_with_postprocessing.parse(given)
    definitions = get_just_definitions(find_custom_command_definitions(parsed))
    dumper = create_dumper(definitions)

    parsed_again = parser_with_postprocessing.parse(given, definitions)
    formatted = dumper.visit(parsed_again)

    assert formatted == expected


def test_custom_command_without_keyworded_arguments_with_disabled_reformatting(
    parser_with_postprocessing,
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

    parsed = parser_with_postprocessing.parse(given)
    definitions = get_just_definitions(find_custom_command_definitions(parsed))
    dumper = create_dumper(definitions)

    parsed_again = parser_with_postprocessing.parse(given, definitions)
    formatted = dumper.visit(parsed_again)

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
def test_can_deal_with_empty_body_in_custom_command_definition(
    parser_with_postprocessing, given
):
    expected = """function(
    some_custom_command_without_keyworded_arguments
    only
    positional
    arguments
)
endfunction()
"""

    parsed = parser_with_postprocessing.parse(given)
    definitions = get_just_definitions(find_custom_command_definitions(parsed))
    dumper = create_dumper(definitions)

    parsed_again = parser_with_postprocessing.parse(given, definitions)
    formatted = dumper.visit(parsed_again)

    assert formatted == expected
