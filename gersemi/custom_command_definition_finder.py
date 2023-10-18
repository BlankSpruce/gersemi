from lark import Discard
from lark.visitors import Interpreter, Transformer
from gersemi.ast_helpers import is_keyword
from gersemi.keywords import Keywords


class IgnoreThisDefinition:
    pass


class DropIrrelevantElements(Transformer):
    def _discard(self, _):
        return Discard

    def non_command_element(self, children):
        if len(children) == 1 and isinstance(children[0], IgnoreThisDefinition):
            return children[0]
        return Discard

    def line_comment(self, children):
        if len(children) > 0 and children[0].strip() == "gersemi: ignore":
            return IgnoreThisDefinition()
        return Discard

    NEWLINE = _discard
    bracket_comment = _discard


is_parse_argv = is_keyword("PARSE_ARGV")


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
        if is_parse_argv(arguments.children[0]):
            keywords = arguments.children[3:6]
        else:
            keywords = arguments.children[1:4]

        options, one_value_keywords, multi_value_keywords = [
            self._eval_variables(self.visit(item)) for item in keywords
        ]
        return Keywords(options, one_value_keywords, multi_value_keywords)

    def start(self, tree):
        return self.visit(tree.children[0])

    def file(self, tree):
        self.visit_children(tree)
        return self.found_commands

    def _should_definition_be_ignored(self, block):
        _, *maybe_body, _ = block.children
        if maybe_body:
            body, *_ = maybe_body
            return len(body.children) > 0 and isinstance(
                body.children[0], IgnoreThisDefinition
            )
        return False

    def _add_command(self, name, arguments):
        key = name.lower()
        if key not in self.found_commands:
            self.found_commands[key] = []

        self.found_commands[key].append(
            (arguments, f"{self.filepath}:{name.line}:{name.column}")
        )

    def block(self, tree):
        if self._should_definition_be_ignored(tree):
            return

        subinterpreter = self._inner_scope
        block_begin, *body, _ = subinterpreter.visit_children(tree)
        command_node, *_ = block_begin
        if command_node is None:
            return
        name, positional_arguments = command_node

        keywords, *_ = body
        if len(keywords) > 0:
            self._add_command(name, (positional_arguments, keywords[0]))
        else:
            self._add_command(name, (positional_arguments, Keywords()))

    def block_body(self, tree):
        return [
            item for item in self.visit_children(tree) if isinstance(item, Keywords)
        ][:1]

    def command_invocation(self, tree):
        identifier, arguments = tree.children
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
        return tree.children[0] if tree.children else ""

    bracket_argument = _join
    commented_argument = _join
    unquoted_argument = _extract_first


def find_custom_command_definitions(tree, filepath="---"):
    tree = DropIrrelevantElements(visit_tokens=True).transform(tree)
    return CMakeInterpreter(filepath).visit(tree)


def get_just_definitions(definitions):
    result = {}
    for name, info in definitions.items():
        sorted_info = list(sorted(info, key=lambda item: item[1]))
        arguments, _ = sorted_info[0]
        result[name] = arguments
    return result
