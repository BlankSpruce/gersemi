from enum import Enum
from typing import Sequence
from lark import Tree
from gersemi.command_invocation_dumpers.argument_aware_command_invocation_dumper import (
    ArgumentAwareCommandInvocationDumper,
)
from gersemi.command_line_formatter import CommandLineFormatter
from gersemi.keyword_with_pairs_formatter import KeywordWithPairsFormatter
from gersemi.keywords import Keywords


class HintKind(Enum):
    CommandLine = "command_line"
    Pairs = "pairs"


def kind_to_function(kind: str) -> str:
    kind_enum = HintKind(kind) if kind in [e.value for e in HintKind] else None
    return {
        HintKind.Pairs: "_format_keyword_with_pairs",
        HintKind.CommandLine: "_format_command_line",
        None: "_default_format_values",
    }[kind_enum]


def create_specialized_dumper(
    raw_command_name: str, positional_arguments: Sequence[str], keywords: Keywords
):
    class Impl(
        ArgumentAwareCommandInvocationDumper,
        KeywordWithPairsFormatter,
        CommandLineFormatter,
    ):
        canonical_name = raw_command_name
        front_positional_arguments = positional_arguments
        options = keywords.options
        one_value_keywords = keywords.one_value_keywords
        multi_value_keywords = keywords.multi_value_keywords
        keyword_formatters = {
            hint.keyword: kind_to_function(hint.kind) for hint in keywords.hints
        }

        def custom_command(self, tree):
            _, command_name, arguments, *_ = tree.children
            return self.visit(Tree("command_invocation", [command_name, arguments]))

    return Impl
