import re
from lark import Token, Tree

DROP = None, 0


def terminal(name, pattern):
    prog = re.compile(pattern)

    def parser(text, offset):
        m = prog.match(text, offset)
        if m is None or not m.group(0):
            return None

        return Token(name, m.group(0)), m.end()

    return parser


_SPACE = re.compile("[ \t]+")


def maybe(original_parser):
    def parser(text, offset):
        matched = original_parser(text, offset)
        if matched is None:
            return DROP

        return matched

    return parser


def flatten_helper_nodes(node):
    result = []
    for child in node.children:
        if not isinstance(child, Tree):
            if not child.type.startswith("_"):
                result.append(child)

            continue

        transformed = flatten_helper_nodes(child)
        if transformed.data.startswith("_"):
            result.extend(transformed.children)
        else:
            result.append(transformed)

    node.children = result
    return node


def tree(name, children):
    if name.startswith("?"):
        if len(children) == 1:
            return children[0]

        name = name[1:]

    return Tree(name, children)


def rule(name, *rules):
    def parser(text, offset):
        result = []
        for rule_parser in rules:
            matched = rule_parser(text, offset)
            if matched is None:
                matched_space = _SPACE.match(text, offset)
                if matched_space is None:
                    return None

                offset = matched_space.end()
                matched = rule_parser(text, offset)
                if matched is None:
                    return None

            if matched != DROP:
                node, offset = matched
                result.append(node)

        return tree(name, result), offset

    return parser


def choice(*parsers):
    def parser(text, offset):
        for p in parsers:
            matched = p(text, offset)
            if matched is not None:
                return matched

        return None

    return parser


def star(name, original_parser):
    def parser(text, offset):
        result = []
        while True:
            matched = original_parser(text, offset)
            if matched is None:
                break

            node, offset = matched
            result.append(node)

        return tree(name, result), offset

    return parser


def plus(name, original_parser):
    star_ = star(name, original_parser)

    def parser(text, offset):
        matched = star_(text, offset)
        if matched is None:
            return None

        node, _ = matched
        if not node.children:
            return None

        return matched

    return parser


BRACKET_ARGUMENT_START = re.compile(r"\[(=*?)\[")


def BRACKET_ARGUMENT(text, offset):
    m = BRACKET_ARGUMENT_START.match(text, offset)
    if m is None:
        return None

    bracket_width = len(m.group(1))
    equal_signs = "=" * bracket_width
    left_bracket = re.escape(f"[{equal_signs}[")
    right_bracket = re.escape(f"]{equal_signs}]")

    pattern = rf"{left_bracket}[\s\S]+?{right_bracket}"
    return terminal("BRACKET_ARGUMENT", pattern)(text, offset)


QUOTATION_MARK = terminal("QUOTATION_MARK", r"\"")
LEFT_PAREN = terminal("LEFT_PARENTHESIS", r"\(")
RIGHT_PAREN = terminal("RIGHT_PARENTHESIS", r"\)")
_LEFT_PAREN = terminal("_LEFT_PARENTHESIS", r"\(")
_RIGHT_PAREN = terminal("_RIGHT_PARENTHESIS", r"\)")
IDENTIFIER = terminal("IDENTIFIER", r"[A-Za-z_@][A-Za-z0-9_@]*")
NEWLINE = terminal("NEWLINE", r"\n+")
_NEWLINE = terminal("_NEWLINE", r"[\n \t]+")
POUND_SIGN = terminal("POUND_SIGN", r"#")
LINE_COMMENT_CONTENT = terminal("LINE_COMMENT_CONTENT", r"[^\n]*")
ESCAPE_SEQUENCE_R = r"\\([^A-Za-z0-9]|[nrt])"
MAKE_STYLE_REFERENCE_R = r"\$\([^\)\n\"#]+?\)"
UNQUOTED_ARGUMENT_R = (
    "("
    + "|".join(
        (
            MAKE_STYLE_REFERENCE_R,
            ESCAPE_SEQUENCE_R,
            r"[^\$\s\(\)#\"\\]+",
            r"[^\s\(\)#\"\\]",
        )
    )
    + ")+"
)
UNQUOTED_ARGUMENT = terminal("UNQUOTED_ARGUMENT", UNQUOTED_ARGUMENT_R)
QUOTED_CONTINUATION_R = r"\\\n"
QUOTED_ARGUMENT_R = (
    '"('
    + "|".join((r"([^\\\"]|\n)+", ESCAPE_SEQUENCE_R, QUOTED_CONTINUATION_R))
    + ')*"'
)
QUOTED_ARGUMENT = terminal("QUOTED_ARGUMENT", QUOTED_ARGUMENT_R)


line_comment = rule("line_comment", POUND_SIGN, maybe(LINE_COMMENT_CONTENT))
bracket_comment = rule("bracket_comment", POUND_SIGN, BRACKET_ARGUMENT)
non_command_element = rule(
    "non_command_element",
    star("_atom_non_command_element", bracket_comment),
    maybe(line_comment),
)
unquoted_argument = rule("unquoted_argument", UNQUOTED_ARGUMENT)
quoted_argument = rule("quoted_argument", QUOTED_ARGUMENT)
bracket_argument = rule("bracket_argument", BRACKET_ARGUMENT)


def arguments(text, offset):
    return arguments_impl(text, offset)


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


def _commented_argument_atom(text, offset):
    matched = POUND_SIGN_RE.match(text, offset)
    if matched is None:
        return None

    parser = choice(
        bracket_comment,
        rule("_atom_commented_argument_atom", line_comment, NEWLINE),
    )
    return parser(text, offset)


commented_argument = rule(
    "?commented_argument", argument, maybe(_commented_argument_atom)
)
_arguments_atom = choice(commented_argument, _separation)
arguments_impl = star("arguments", _arguments_atom)
_invocation_part = rule("_invocation_part", LEFT_PAREN, arguments, RIGHT_PAREN)
command_invocation = rule("command_invocation", IDENTIFIER, _invocation_part)
command_element = rule("?command_element", command_invocation, maybe(line_comment))


def _file_element_until(until_rule):
    def parser(text, offset):
        matched = until_rule(text, offset)
        if matched is not None:
            return None

        return _file_element(text, offset)

    return parser


_newline = rule("_newline", NEWLINE)
_newline_or_gap = plus("_newline_or_gap", _newline)


def newline_or_gap(text, offset):
    matched = _newline_or_gap(text, offset)
    if matched is None:
        return None

    node, offset = matched
    node = flatten_helper_nodes(node)
    return Token("NEWLINE", "".join(node.children)[:2]), offset


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


def command_template(t):
    return rule("command_invocation", t, _invocation_part)


def element_template(name, pattern):
    t = terminal(name, pattern)
    return rule("command_element", command_template(t), maybe(line_comment))


def block_template(start_rule, end_rule):
    return rule("block", start_rule, block_body(end_rule), end_rule)


FOREACH = element_template("FOREACH", "(?i)foreach")
ENDFOREACH = element_template("ENDFOREACH", "(?i)endforeach")
_foreach_block = block_template(FOREACH, ENDFOREACH)

FUNCTION = element_template("FUNCTION", "(?i)function")
ENDFUNCTION = element_template("ENDFUNCTION", "(?i)endfunction")
_function_block = block_template(FUNCTION, ENDFUNCTION)

MACRO = element_template("MACRO", "(?i)macro")
ENDMACRO = element_template("ENDMACRO", "(?i)endmacro")
_macro_block = block_template(MACRO, ENDMACRO)

WHILE = element_template("WHILE", "(?i)while")
ENDWHILE = element_template("ENDWHILE", "(?i)endwhile")
_while_block = block_template(WHILE, ENDWHILE)

BLOCK = element_template("BLOCK", "(?i)block")
ENDBLOCK = element_template("ENDBLOCK", "(?i)endblock")
_block_block = block_template(BLOCK, ENDBLOCK)

IF = element_template("IF", "(?i)if")
ENDIF = element_template("ENDIF", "(?i)endif")


def split_if_body(original_parser):
    def parser(text, offset):
        matched = original_parser(text, offset)
        if matched is None:
            return None

        node, offset = matched
        if_k, body, endif = flatten_helper_nodes(node).children

        children = [if_k]
        new_body = []
        for child in body.children:
            if not isinstance(child, Tree):
                new_body.append(child)
                continue

            if child.data != "command_invocation":
                new_body.append(child)
                continue

            if child.children[0] not in ["elseif", "else"]:
                new_body.append(child)
                continue

            children.append(tree("block_body", new_body[:]))
            if child.children[0].lower() == "elseif":
                child.children[0] = Token("ELSEIF", "elseif")

            if child.children[0].lower() == "else":
                child.children[0] = Token("ELSE", "else")

            children.append(tree("command_element", [child]))
            new_body = []

        if new_body:
            children.append(tree("block_body", new_body[:]))

        children.append(endif)

        return tree("block", children), offset

    return parser


_if_block = split_if_body(rule("block", IF, block_body(ENDIF), ENDIF))


block = choice(
    _foreach_block,
    _function_block,
    _if_block,
    _macro_block,
    _while_block,
    _block_block,
)
standalone_identifier = rule("standalone_identifier", IDENTIFIER)
_file_element = choice(
    block, command_element, standalone_identifier, non_command_element
)


_start_atom = rule("_atom_start_atom", _file_element, newline_or_gap)
start = rule("start", star("_atom_start", _start_atom), _file_element)


def parse(text):
    result, _ = start(text, 0)
    return flatten_helper_nodes(result)
