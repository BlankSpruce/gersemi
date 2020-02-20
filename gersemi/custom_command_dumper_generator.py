from typing import Dict, List
from lark import Discard, Tree
from lark.visitors import Interpreter, Transformer
from gersemi.ast_helpers import is_keyword
from gersemi.command_invocation_dumpers.argument_aware_command_invocation_dumper import (
    ArgumentAwareCommandInvocationDumper,
)


class DropIrrelevantElements(Transformer):  # pylint: disable=too-few-public-methods
    def _discard(self, _):
        raise Discard

    NEWLINE = _discard
    line_comment = _discard
    bracket_comment = _discard
    non_command_element = _discard


class GetCommandName(Interpreter):
    def unquoted_argument(self, tree):
        return tree.children[0].lower()

    def __default__(self, tree):
        for child in tree.children:
            if not isinstance(child, Tree):
                continue

            visitted = self.visit(child)
            if visitted is not None:
                return visitted
        return None


class FindCMakeParseArguments(Interpreter):
    def command_invocation(self, tree):
        identifier, *_ = tree.children
        if identifier == "cmake_parse_arguments":
            return tree
        return None

    def __default__(self, tree):
        for child in tree.children:
            if not isinstance(child, Tree):
                continue

            visitted = self.visit(child)
            if visitted is not None:
                return visitted
        return None


class ExtractVariableFromSetCommand(Interpreter):
    def arguments(self, tree):
        result = self.visit_children(tree)
        return result[0], result[1:]

    def _join(self, tree):
        return "".join(self.visit_children(tree))

    bracket_argument = _join
    unquoted_argument = _join
    quoted_argument = _join
    quoted_element = _join


def find_set_variables(tree):
    class Impl(Interpreter):
        def __init__(self):
            self.result = []

        def command_invocation(self, tree):
            identifier, arguments = tree.children
            if identifier != "set":
                return

            self.result += [ExtractVariableFromSetCommand().visit(arguments)]

    impl = Impl()
    impl.visit(tree)
    return dict(impl.result)


def create_specialized_dumper(options_, one_value_keywords_, multi_value_keywords_):
    class Impl(ArgumentAwareCommandInvocationDumper):
        options = options_[:]
        one_value_keywords = one_value_keywords_[:]
        multi_value_keywords = multi_value_keywords_[:]

    return Impl


def evaluate_variables(argument, variables):
    class Impl(Interpreter):
        def quoted_element(self, tree):
            return "".join(self.visit_children(tree))

        def quoted_argument(self, tree):
            content = "".join(self.visit_children(tree))
            for name, value in variables.items():
                content = content.replace(f"${{{name}}}", ";".join(value))

            values = content.split(";")
            return values

    return Impl().visit(argument)


def extract_keywords(cmake_parse_arguments, known_variables):
    _, arguments = cmake_parse_arguments.children
    evaluate = lambda arg: evaluate_variables(arg, known_variables)
    if is_keyword("PARSE_ARGV")(arguments.children[0]):
        return map(evaluate, arguments.children[3:6])

    return map(evaluate, arguments.children[1:4])


class GenerateCustomCommandDumpers(Interpreter):
    known_variables: Dict[str, List[str]]

    def start(self, tree):
        return self.visit_children(tree)[0]

    def file(self, tree):
        tree = DropIrrelevantElements(visit_tokens=True).transform(tree)
        self.known_variables = find_set_variables(tree)
        is_not_none = lambda item: item is not None
        return dict(filter(is_not_none, self.visit_children(tree)))

    def block(self, tree):
        begin, *body, _ = tree.children
        if len(body) == 0:
            return None

        cmake_parse_arguments = FindCMakeParseArguments().visit(body[0])
        if cmake_parse_arguments is None:
            return None

        keywords = extract_keywords(cmake_parse_arguments, self.known_variables)
        command_name = GetCommandName().visit(begin)
        return command_name, create_specialized_dumper(*keywords)

    def __default__(self, tree):
        return None


def generate_custom_command_dumpers(tree):
    return GenerateCustomCommandDumpers().visit(tree)
