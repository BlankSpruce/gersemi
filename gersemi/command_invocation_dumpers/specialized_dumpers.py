from typing import Sequence
from lark import Tree
from gersemi.command_invocation_dumpers.argument_aware_command_invocation_dumper import (
    ArgumentAwareCommandInvocationDumper,
)
from gersemi.keywords import Keywords


def create_specialized_dumper(positional_arguments: Sequence[str], keywords: Keywords):
    class Impl(ArgumentAwareCommandInvocationDumper):
        front_positional_arguments = positional_arguments
        options = keywords.options
        one_value_keywords = keywords.one_value_keywords
        multi_value_keywords = keywords.multi_value_keywords

        def custom_command(self, tree):
            _, command_name, arguments, *_ = tree.children
            return self.visit(Tree("command_invocation", [command_name, arguments]))

    return Impl
