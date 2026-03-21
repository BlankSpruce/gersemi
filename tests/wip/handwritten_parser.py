from collections import ChainMap
from dataclasses import dataclass
from itertools import dropwhile
import re
from lark import Token, Tree
from gersemi.ast_helpers import is_newline
from gersemi.builtin_commands import _builtin_commands

DROP = None, 0


@dataclass
class ParsingContext:
    known_definitions: dict


def terminal(name, pattern, flags="", ignore=r"[ \t]*"):
    prog = re.compile(rf"{flags}({pattern}){ignore}")

    def parser(context, text, offset):
        m = prog.match(text, offset)
        if m is None or not m.group(1):
            return None

        return Token(name, m.group(1)), m.end()

    return parser


def maybe(original_parser):
    def parser(context, text, offset):
        matched = original_parser(context, text, offset)
        if matched is None:
            return DROP

        return matched

    return parser


def tree(name, children):
    if name.startswith("?"):
        if len(children) == 1:
            return children[0]

        name = name[1:]

    return Tree(name, children)


def rule(name, *rules):
    def parser(context, text, offset):
        result = []
        for rule_parser in rules:
            matched = rule_parser(context, text, offset)
            if matched is None:
                return None

            if matched != DROP:
                node, offset = matched
                result.append(node)

        return tree(name, result), offset

    return parser


def terminal_rule(name, token_name, pattern):
    ignore = r"[ \t]*"
    prog = re.compile(rf"({pattern}){ignore}")

    def parser(context, text, offset):
        m = prog.match(text, offset)
        if m is None or not m.group(1):
            return None

        return Tree(name, [Token(token_name, m.group(1))]), m.end()

    return parser


def choice(*parsers):
    def parser(context, text, offset):
        for p in parsers:
            matched = p(context, text, offset)
            if matched is not None:
                return matched

        return None

    return parser


def star(name, original_parser):
    def parser(context, text, offset):
        result = []
        while True:
            matched = original_parser(context, text, offset)
            if matched is None:
                break

            node, offset = matched
            result.append(node)

        return tree(name, result), offset

    return parser


def plus(name, original_parser):
    star_ = star(name, original_parser)

    def parser(context, text, offset):
        matched = star_(context, text, offset)
        if matched is None:
            return None

        node, _ = matched
        if not node.children:
            return None

        return matched

    return parser


BRACKET_ARGUMENT_START = re.compile(r"\[(=*?)\[")


def BRACKET_ARGUMENT(context, text, offset):
    m = BRACKET_ARGUMENT_START.match(text, offset)
    if m is None:
        return None

    bracket_width = len(m.group(1))
    equal_signs = "=" * bracket_width
    left_bracket = re.escape(f"[{equal_signs}[")
    right_bracket = re.escape(f"]{equal_signs}]")

    pattern = rf"{left_bracket}[\s\S]+?{right_bracket}"
    return terminal("BRACKET_ARGUMENT", pattern)(context, text, offset)


QUOTATION_MARK = terminal("QUOTATION_MARK", r"\"")
_LEFT_PAREN = terminal("_LEFT_PARENTHESIS", r"\(")
_RIGHT_PAREN = terminal("_RIGHT_PARENTHESIS", r"\)")
IDENTIFIER_R = r"[A-Za-z_@][A-Za-z0-9_@]*"
IDENTIFIER = terminal("IDENTIFIER", IDENTIFIER_R)
NEWLINE = terminal("NEWLINE", r"\n+")
_NEWLINE = terminal("_NEWLINE", r"[\n \t]+")
POUND_SIGN = terminal("POUND_SIGN", r"#", ignore="")
LINE_COMMENT_CONTENT = terminal("LINE_COMMENT_CONTENT", r"[^\n]*")
ESCAPE_SEQUENCE_R = r"\\([^A-Za-z0-9]|[nrt])"
MAKE_STYLE_REFERENCE_R = r"\$\([^\)\n\"#]+?\)"
QUOTED_CONTINUATION_R = r"\\\n"
QUOTED_ARGUMENT_R = (
    '"('
    + "|".join((r"([^\\\"]|\n)+", ESCAPE_SEQUENCE_R, QUOTED_CONTINUATION_R))
    + ')*"'
)
UNQUOTED_LEGACY_R = r"[^\s\(\)#\"\\]+" + QUOTED_ARGUMENT_R
UNQUOTED_ARGUMENT_R = (
    "("
    + "|".join(
        (
            UNQUOTED_LEGACY_R,
            MAKE_STYLE_REFERENCE_R,
            ESCAPE_SEQUENCE_R,
            r"[^\$\s\(\)#\"\\]+",
            r"[^\s\(\)#\"\\]",
        )
    )
    + ")+"
)


line_comment = rule("line_comment", POUND_SIGN, maybe(LINE_COMMENT_CONTENT))
bracket_comment = rule("bracket_comment", POUND_SIGN, BRACKET_ARGUMENT)
non_command_element = rule(
    "non_command_element",
    star("_atom_non_command_element", bracket_comment),
    maybe(line_comment),
)
unquoted_argument = terminal_rule(
    "unquoted_argument", "UNQUOTED_ARGUMENT", UNQUOTED_ARGUMENT_R
)
quoted_argument = terminal_rule("quoted_argument", "QUOTED_ARGUMENT", QUOTED_ARGUMENT_R)
bracket_argument = rule("bracket_argument", BRACKET_ARGUMENT)


def arguments(context, text, offset):
    return arguments_impl(context, text, offset)


complex_argument = rule("complex_argument", _LEFT_PAREN, arguments, _RIGHT_PAREN)
argument = choice(
    bracket_argument, quoted_argument, unquoted_argument, complex_argument
)
_separation_atom = choice(
    bracket_comment,
    line_comment,
    _NEWLINE,
)
_separation = plus("_separation", _separation_atom)


POUND_SIGN_RE = re.compile(r"[ \t]*#")


def _commented_argument_atom(context, text, offset):
    matched = POUND_SIGN_RE.match(text, offset)
    if matched is None:
        return None

    parser = choice(
        bracket_comment,
        rule("_atom_commented_argument_atom", line_comment, NEWLINE),
    )
    return parser(context, text, offset)


commented_argument = rule(
    "?commented_argument", argument, maybe(_commented_argument_atom)
)
_arguments_atom = choice(commented_argument, _separation)
arguments_impl = star("arguments", _arguments_atom)


def command_invocation(identifier_rule):
    def parser(context, text, offset):
        command_start = offset
        matched_identifier = identifier_rule(context, text, offset)
        if matched_identifier is None:
            return None

        identifier, offset = matched_identifier
        matched_left_paren = _LEFT_PAREN(context, text, offset)
        if matched_left_paren is None:
            return None

        left_paren_offset = offset
        _, offset = matched_left_paren
        matched_arguments = arguments(context, text, offset)
        if matched_arguments is None:
            return None

        arguments_node, offset = matched_arguments
        matched_right_paren = _RIGHT_PAREN(context, text, offset)
        if matched_right_paren is None:
            return None

        right_paren_offset = offset
        _, offset = matched_right_paren
        if identifier.lower() not in context.known_definitions:
            start = text[:command_start].rfind("\n") + 1
            indentation = text[start:command_start]
            node = tree(
                "custom_command",
                [
                    indentation,
                    identifier,
                    arguments_node,
                    tree(
                        "formatted_node",
                        [text[left_paren_offset + 1 : right_paren_offset]],
                    ),
                ],
            )
        else:
            node = tree("command_invocation", [identifier, arguments_node])

        return node, offset

    return parser


command_element = rule(
    "?command_element", command_invocation(IDENTIFIER), maybe(line_comment)
)


def _file_element_until(until_rule):
    def parser(context, text, offset):
        matched = until_rule(context, text, offset)
        if matched is not None:
            return None

        return _file_element(context, text, offset)

    return parser


GAP = re.compile(r"(\n[ \t]*)(\n[ \t]*)*")


def newline_or_gap(context, text, offset):
    matched = GAP.match(text, offset)
    if matched is None:
        return None

    if matched.group(2) is None:
        return Token("NEWLINE", "\n"), matched.end()

    return Token("NEWLINE", "\n\n"), matched.end()


def _block_body_atom(until_rule):
    return rule(
        "_atom_block_body_atom", newline_or_gap, _file_element_until(until_rule)
    )


def block_body(until_rule):
    return rule(
        "block_body",
        star("_atom_block_body", _block_body_atom(until_rule)),
        newline_or_gap,
    )


def element_template(pattern):
    t = terminal(pattern.upper(), pattern, flags="(?i)")
    return rule("command_element", command_invocation(t), maybe(line_comment))


def block_template(start, end):
    end_rule = element_template(end)
    return rule("block", element_template(start), block_body(end_rule), end_rule)


block = choice(
    block_template("if", "endif"),
    block_template("foreach", "endforeach"),
    block_template("function", "endfunction"),
    block_template("macro", "endmacro"),
    block_template("while", "endwhile"),
    block_template("block", "endblock"),
)
standalone_identifier = terminal_rule(
    "standalone_identifier", "IDENTIFIER", IDENTIFIER_R
)
_file_element = choice(
    block, command_element, standalone_identifier, non_command_element
)


_start_atom = rule("_atom_start_atom", _file_element, newline_or_gap)
start = rule("start", star("_atom_start", _start_atom), _file_element)


def _drop_edge_empty_lines(children):
    while len(children) > 0 and is_newline(children[-1]):
        children.pop()
    return list(dropwhile(is_newline, children))


def postprocess(node):
    result = []
    for child in node.children:
        if not isinstance(child, Tree):
            if not getattr(child, "type", "").startswith("_"):
                result.append(child)

            continue

        transformed = postprocess(child)
        if transformed.data.startswith("_"):
            result.extend(transformed.children)
        elif (transformed.data == "non_command_element") and (not transformed.children):
            pass
        else:
            result.append(transformed)

    node.children = (
        _drop_edge_empty_lines(result)
        if node.data in ("block_body", "start")
        else result
    )
    return node


def parse(text, known_definitions=None):
    context = ParsingContext(
        known_definitions=(
            _builtin_commands
            if known_definitions is None
            else ChainMap(known_definitions, _builtin_commands)
        )
    )
    result, _ = start(context, text, 0)
    return postprocess(postprocess(result))
