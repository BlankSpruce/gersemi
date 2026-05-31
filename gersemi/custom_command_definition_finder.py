from typing import Optional, Sequence
import yaml
from gersemi.argument_schema import StandardCommand, argument_schema_from_dict
from gersemi.ast_helpers import get_value, is_keyword
from gersemi.immutable import make_immutable
from gersemi.keyword_kind import KeywordFormatter, KeywordPreprocessor
from gersemi.keywords import Hint, Keywords
from gersemi.transformer import Discard, Transformer_InPlace
from gersemi.types import Token, Tree

BLOCK_END = "gersemi: block_end "
HINTS = "gersemi: hints"
IGNORE = "gersemi: ignore"


class DropIrrelevantElements(Transformer_InPlace):
    def _discard(self, _):
        return Discard

    def non_command_element(self, children):
        if (
            (len(children) == 1)
            and isinstance(children[0], Token)
            and children[0].type
            in ["BLOCK_END_COMMAND", "IGNORE_THIS_DEFINITION", "USE_HINT"]
        ):
            return children[0]

        return Discard

    def line_comment(self, children):
        if len(children) > 1:
            comment = str(children[1]).strip()
            if comment == IGNORE:
                return Token("IGNORE_THIS_DEFINITION", "")

            if comment.startswith(HINTS):
                return Token("USE_HINT", comment[len(HINTS) :])

            if comment.startswith(BLOCK_END):
                return Token("BLOCK_END_COMMAND", comment[len(BLOCK_END) :])

        return Discard

    bracket_comment = _discard


class CMakeInterpreter:
    def __init__(self, filepath, stack=None):
        self.stack = {} if stack is None else stack
        self.found_commands = {}
        self.filepath = filepath

    @property
    def _inner_scope(self):
        return type(self)(filepath=self.filepath, stack=self.stack.copy())

    def _eval_variables(self, arg):
        for name, value in self.stack.items():
            arg = arg.replace(f"${{{name}}}", ";".join(value))
        return arg.split(";")

    def _set(self, arguments):
        name, *values = self.arguments(arguments)
        self.stack[name] = [
            item for value in values for item in self._eval_variables(str(value))
        ]

    def _new_command(self, arguments):
        if len(arguments.children) > 0:
            name = arguments.children[0]
            positional_arguments = arguments.children[1:]
            return self.argument(name), list(
                map(str, map(self.argument, positional_arguments))
            )
        raise RuntimeError

    def _cmake_parse_arguments(self, arguments):
        if is_keyword("PARSE_ARGV", arguments.children[0]):
            keywords = arguments.children[3:6]
        else:
            keywords = arguments.children[1:4]

        options, one_value_keywords, multi_value_keywords = [
            self._eval_variables(str(self.argument(item))) for item in keywords
        ]
        return Keywords(options, one_value_keywords, multi_value_keywords)

    def start(self, tree):
        for child in tree.children:
            if not isinstance(child, Tree):
                continue

            if child.data == "command_invocation":
                self.command_invocation(child)
            elif child.data == "command_element":
                first = child.children[0]
                self.command_invocation(first)
            elif child.data == "block":
                self.block(child)

        return self.found_commands

    def _should_definition_be_ignored(self, block):
        _, *maybe_body, _ = block.children
        if maybe_body:
            body, *_ = maybe_body
            return body.children and any(
                (isinstance(c, Token) and c.type == "IGNORE_THIS_DEFINITION")
                for c in body.children
            )
        return False

    def _add_command(self, name, arguments, block_end):
        key = str(name).lower()
        if key not in self.found_commands:
            self.found_commands[key] = []

        self.found_commands[key].append(
            (
                (str(name), arguments, block_end),
                f"{self.filepath}:{name.line}:{name.column}",
            )
        )

    def _get_hints(self, block):
        _, *maybe_body, _ = block.children
        result = []
        if maybe_body:
            body, *_ = maybe_body
            for child in body.children:
                if not (isinstance(child, Token) and child.type == "USE_HINT"):
                    continue

                result.append(child.value)

        return result

    def _get_block_end(self, block):
        _, *maybe_body, _ = block.children
        if maybe_body:
            body, *_ = maybe_body
            for child in body.children:
                if isinstance(child, Token) and child.type == "BLOCK_END_COMMAND":
                    return child.value
        return None

    def block_begin(self, tree):
        if tree.data == "command_element":
            children = tree.children[0].children
        else:
            children = tree.children

        identifier, arguments = children
        if identifier in ["function", "macro"]:
            return self._new_command(arguments)

        return None

    def block(self, tree):
        if self._should_definition_be_ignored(tree):
            return

        block_end = self._get_block_end(tree)
        subinterpreter = self._inner_scope
        command_node = subinterpreter.block_begin(tree.children[0])
        body = subinterpreter.block_body(tree.children[1])
        self.found_commands.update(subinterpreter.found_commands)

        if command_node is None:
            return
        name, positional_arguments = command_node

        if body:
            keywords = body
            keywords.hints = self._get_hints(tree)
        else:
            keywords = Keywords()

        self._add_command(name, (positional_arguments, keywords), block_end)

    def block_body(self, tree: Tree) -> Optional[Keywords]:
        result = None
        for child in tree.children:
            if not isinstance(child, Tree):
                continue

            item = None
            if child.data == "command_element":
                element = child.children[0]
                if element.data == "command_invocation":
                    item = self.command_invocation(element)
                else:
                    item = None
            elif child.data == "command_invocation":
                item = self.command_invocation(child)
            elif child.data == "block":
                self.block(child)
            else:
                continue

            if isinstance(item, Keywords):
                result = item

        return result

    def command_invocation(self, tree):
        identifier, arguments = tree.children
        command_interpreters = {
            "cmake_parse_arguments": self._cmake_parse_arguments,
            "set": self._set,
        }
        return command_interpreters.get(identifier, lambda *args: None)(arguments)

    def bracket_argument(self, tree: Tree) -> str:
        return "".join(map(str, tree.children))

    def complex_argument(self, tree: Tree) -> str:
        return "".join(map(str, self.arguments(tree.children[0])))

    def arguments(self, tree: Tree) -> Sequence[str]:
        return [self.argument(c) for c in tree.children]

    def argument(self, tree: Tree) -> str:
        if tree.data == "unquoted_argument":
            return tree.children[0]

        if tree.data == "quoted_argument":
            return get_value(tree, "")

        if tree.data == "bracket_argument":
            return self.bracket_argument(tree)

        if tree.data == "complex_argument":
            return self.complex_argument(tree)

        if tree.data == "commented_argument":
            return self.argument(tree.children[0])

        raise NotImplementedError


def find_custom_command_definitions(tree, filepath="---"):
    tree = DropIrrelevantElements().transform(tree)
    return CMakeInterpreter(filepath).start(tree)


def create_command(canonical_name, positional_arguments, keywords, block_end):
    hints = {}
    for raw_hint in keywords.hints:
        hints.update(yaml.safe_load(raw_hint) or {})

    hints = tuple(Hint(keyword, kind) for keyword, kind in hints.items())

    schema = {
        "front_positional_arguments": positional_arguments,
        "options": keywords.options,
        "one_value_keywords": keywords.one_value_keywords,
        "multi_value_keywords": keywords.multi_value_keywords,
        "keyword_formatters": make_immutable(
            {
                hint.keyword: hint.kind
                for hint in hints
                if hint.kind in [e.value for e in KeywordFormatter]
            }
        ),
        "keyword_preprocessors": make_immutable(
            {
                hint.keyword: hint.kind
                for hint in hints
                if hint.kind in [e.value for e in KeywordPreprocessor]
            }
        ),
    }
    return StandardCommand(
        canonical_name=canonical_name,
        schema=argument_schema_from_dict(schema),
        block_end=block_end,
    )


def get_just_definitions(definitions):
    result = {}
    for name, info in definitions.items():
        sorted_info = sorted(info, key=lambda item: item[1])
        (canonical_name, (positional_arguments, keywords), block_end), _ = sorted_info[
            0
        ]
        result[name] = create_command(
            canonical_name, positional_arguments, keywords, block_end
        )
    return make_immutable(result)
