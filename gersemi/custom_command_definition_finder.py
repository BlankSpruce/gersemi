import yaml
from lark import Discard
from lark.visitors import Interpreter
from gersemi.ast_helpers import get_value, is_keyword
from gersemi.immutable import make_immutable
from gersemi.keywords import Hint, Keywords
from gersemi.keyword_kind import KeywordFormatter, KeywordPreprocessor
from gersemi.transformer import Transformer_InPlace


class IgnoreThisDefinition:
    pass


BLOCK_END = "gersemi: block_end "
HINTS = "gersemi: hints"
IGNORE = "gersemi: ignore"


class UseHint:
    def __init__(self, value):
        self.value = yaml.safe_load(value) or {}

    def merge(self, other):
        self.value.update(other.value)


class BlockEnd(str):
    pass


class DropIrrelevantElements(Transformer_InPlace):
    def _discard(self, _):
        return Discard

    def non_command_element(self, children):
        if (len(children) == 1) and any(
            isinstance(children[0], helper_type)
            for helper_type in [IgnoreThisDefinition, UseHint, BlockEnd]
        ):
            return children[0]
        return Discard

    def line_comment(self, children):
        if len(children) > 1:
            comment = children[1].strip()
            if comment == IGNORE:
                return IgnoreThisDefinition()

            if comment.startswith(HINTS):
                return UseHint(value=comment[len(HINTS) :])

            if comment.startswith(BLOCK_END):
                return BlockEnd(comment[len(BLOCK_END) :])

        return Discard

    bracket_comment = _discard


class CMakeInterpreter(Interpreter):
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
        name, *values = self.visit_children(arguments)
        self.stack[name] = [
            item for value in values for item in self._eval_variables(value)
        ]

    def _new_command(self, arguments):
        if len(arguments.children) > 0:
            name = arguments.children[0]
            positional_arguments = arguments.children[1:]
            return self.visit(name), list(
                map(str, map(self.visit, positional_arguments))
            )
        raise RuntimeError

    def _cmake_parse_arguments(self, arguments):
        if is_keyword("PARSE_ARGV", arguments.children[0]):
            keywords = arguments.children[3:6]
        else:
            keywords = arguments.children[1:4]

        options, one_value_keywords, multi_value_keywords = [
            self._eval_variables(self.visit(item)) for item in keywords
        ]
        return Keywords(options, one_value_keywords, multi_value_keywords)

    def start(self, tree):
        self.visit_children(tree)
        return self.found_commands

    def _should_definition_be_ignored(self, block):
        _, *maybe_body, _ = block.children
        if maybe_body:
            body, *_ = maybe_body
            return body.children and any(
                isinstance(c, IgnoreThisDefinition) for c in body.children
            )
        return False

    def _add_command(self, name, arguments, block_end):
        key = name.lower()
        if key not in self.found_commands:
            self.found_commands[key] = []

        self.found_commands[key].append(
            (
                (name, arguments, block_end),
                f"{self.filepath}:{name.line}:{name.column}",
            )
        )

    def _get_hint(self, block):
        _, *maybe_body, _ = block.children
        result = None
        if maybe_body:
            body, *_ = maybe_body
            for child in body.children:
                if not isinstance(child, UseHint):
                    continue

                if result:
                    result.merge(child)
                else:
                    result = child

        return result

    def _get_block_end(self, block):
        _, *maybe_body, _ = block.children
        if maybe_body:
            body, *_ = maybe_body
            for child in body.children:
                if isinstance(child, BlockEnd):
                    return child
        return None

    def _add_hint(self, keywords, hint):
        if hint is None:
            return keywords

        keywords.hints = tuple(
            Hint(keyword, kind) for keyword, kind in hint.value.items()
        )
        return keywords

    def block(self, tree):
        if self._should_definition_be_ignored(tree):
            return

        hint = self._get_hint(tree)
        block_end = self._get_block_end(tree)
        subinterpreter = self._inner_scope
        block_begin, *body, _ = subinterpreter.visit_children(tree)
        self.found_commands.update(subinterpreter.found_commands)

        command_node, *_ = block_begin
        if command_node is None:
            return
        name, positional_arguments = command_node

        keywords, *_ = body
        if len(keywords) > 0:
            self._add_command(
                name,
                (positional_arguments, self._add_hint(keywords[0], hint)),
                block_end,
            )
        else:
            self._add_command(name, (positional_arguments, Keywords()), block_end)

    def block_body(self, tree):
        return [
            item for item in self.visit_children(tree) if isinstance(item, Keywords)
        ][:1]

    def command_invocation(self, tree):
        identifier, _, arguments, _ = tree.children
        command_interpreters = {
            "cmake_parse_arguments": self._cmake_parse_arguments,
            "function": self._new_command,
            "macro": self._new_command,
            "set": self._set,
        }
        return command_interpreters.get(identifier, lambda *args: None)(arguments)

    def _join(self, tree):
        return "".join(self.visit_children(tree))

    def complex_argument(self, tree):
        return f"({self.visit_children(tree)})"

    def _extract_first(self, tree):
        return tree.children[0]

    def quoted_argument(self, tree):
        return get_value(tree, "")

    bracket_argument = _join
    commented_argument = _join
    unquoted_argument = _extract_first


def find_custom_command_definitions(tree, filepath="---"):
    tree = DropIrrelevantElements().transform(tree)
    return CMakeInterpreter(filepath).visit(tree)


def create_command(canonical_name, positional_arguments, keywords, block_end):
    return {
        "_canonical_name": canonical_name,
        "front_positional_arguments": positional_arguments,
        "options": keywords.options,
        "one_value_keywords": keywords.one_value_keywords,
        "multi_value_keywords": keywords.multi_value_keywords,
        "keyword_formatters": {
            hint.keyword: hint.kind
            for hint in keywords.hints
            if hint.kind in [e.value for e in KeywordFormatter]
        },
        "keyword_preprocessors": {
            hint.keyword: hint.kind
            for hint in keywords.hints
            if hint.kind in [e.value for e in KeywordPreprocessor]
        },
        "block_end": block_end,
    }


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
