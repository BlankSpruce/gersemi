import gersemi_rust_backend
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


@pytest.mark.parametrize("indent", [2, 4, "tabs"])
@pytest.mark.parametrize("original_indent", ["", "  ", "\t", " \t", "\t "])
@pytest.mark.parametrize("depth", [0, 1, 2])
@pytest.mark.parametrize("first_argument", ["", "inline"])
def test_unknown_command_preserves_relative_indentation(
    formatter_creator, indent, original_indent, depth, first_argument
):
    given_body = (
        f"{original_indent}unknown({first_argument}\n"
        f"{original_indent}\tfirst  second\n"
        f"{original_indent}\t\tthird\n"
        f'{original_indent}\t# A comment with "quotes" ending in [\n'
        f'{original_indent}\t"quoted\n'
        " \t literal whitespace\n"
        '  text"\n'
        f"{original_indent}\t[=[bracket\n"
        "\t  literal whitespace\n"
        "  text]=]\n"
        f'{original_indent}\t#[==[Comment with "quotes" and [=[markers]=]\n'
        " \t preserve comment content\n"
        "  ]==]\n"
        f"{original_indent}\t[[second bracket\n"
        " \t literal whitespace]]\n"
        f'{original_indent}\tescaped\\#hash escaped\\"quote\n'
        f"{original_indent})\n"
    )
    indent_symbol = "\t" if indent == "tabs" else " " * indent
    output_indent = indent_symbol * depth
    expected_body = (
        f"{output_indent}unknown({first_argument}\n"
        f"{output_indent}\tfirst  second\n"
        f"{output_indent}\t\tthird\n"
        f'{output_indent}\t# A comment with "quotes" ending in [\n'
        f'{output_indent}\t"quoted\n'
        " \t literal whitespace\n"
        '  text"\n'
        f"{output_indent}\t[=[bracket\n"
        "\t  literal whitespace\n"
        "  text]=]\n"
        f'{output_indent}\t#[==[Comment with "quotes" and [=[markers]=]\n'
        " \t preserve comment content\n"
        "  ]==]\n"
        f"{output_indent}\t[[second bracket\n"
        " \t literal whitespace]]\n"
        f'{output_indent}\tescaped\\#hash escaped\\"quote\n'
        f"{output_indent})\n"
    )
    given = "if(TRUE)\n" * depth + given_body + "endif()\n" * depth
    expected = (
        "".join(indent_symbol * level + "if(TRUE)\n" for level in range(depth))
        + expected_body
        + "".join(
            indent_symbol * level + "endif()\n" for level in reversed(range(depth))
        )
    )
    formatter = formatter_creator({"indent": indent})

    formatted, _ = formatter.format(given)

    assert formatted == expected
    assert formatter.format(formatted)[0] == formatted
    assert gersemi_rust_backend.check_code_equivalence(given, formatted)


def test_switching_indentation_does_not_accumulate_whitespace(formatter_creator):
    given = (
        "function(example)\n"
        "\tif(TRUE)\n"
        "\t\tunknown(\n"
        "\t\t\tfirst\n"
        "\t\t\tsecond\n"
        "\t\t)\n"
        "\tendif()\n"
        "endfunction()\n"
    )
    with_spaces = formatter_creator({"indent": 4})
    with_tabs = formatter_creator({"indent": "tabs"})

    formatted = given
    for _ in range(3):
        formatted, _ = with_spaces.format(formatted)
        formatted, _ = with_tabs.format(formatted)
        assert formatted == given


def test_unknown_command_reindent_respects_argument_boundaries(formatter_creator):
    given = (
        "if(TRUE)\n"
        "  unknown(\n"
        "    first[[unquoted\n"
        "    second]]\n"
        '    legacy"quoted\n'
        "  \t literal whitespace\n"
        '    text"\n'
        "    [[bracket\n"
        "  \t literal whitespace]]\n"
        "  )\n"
        "endif()\n"
    )
    expected = (
        "if(TRUE)\n"
        "\tunknown(\n"
        "\t  first[[unquoted\n"
        "\t  second]]\n"
        '\t  legacy"quoted\n'
        "  \t literal whitespace\n"
        '    text"\n'
        "\t  [[bracket\n"
        "  \t literal whitespace]]\n"
        "\t)\n"
        "endif()\n"
    )
    formatter = formatter_creator({"indent": "tabs"})

    formatted, _ = formatter.format(given)

    assert formatted == expected
    assert formatter.format(formatted)[0] == formatted
    assert gersemi_rust_backend.check_code_equivalence(given, formatted)


def test_unknown_command_preserves_nonmatching_indentation(formatter_creator):
    given = "if(TRUE)\n    unknown(\n  outdented\n        indented\n    )\nendif()\n"
    expected = "if(TRUE)\n\tunknown(\n\t  outdented\n\t    indented\n\t)\nendif()\n"
    formatter = formatter_creator({"indent": "tabs"})

    formatted, _ = formatter.format(given)

    assert formatted == expected
    assert formatter.format(formatted)[0] == formatted
    assert gersemi_rust_backend.check_code_equivalence(given, formatted)
