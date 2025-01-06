from typing import Optional, Union
from lark import Tree
from gersemi.command_line_formatter import CommandLineFormatter
from gersemi.keyword_kind import KeywordKind
from gersemi.keyword_with_pairs_formatter import KeywordWithPairsFormatter
from .argument_aware_command_invocation_dumper import (
    ArgumentAwareCommandInvocationDumper,
)
from .multiple_signature_command_invocation_dumper import (
    MultipleSignatureCommandInvocationDumper,
)
from .section_aware_command_invocation_dumper import SectionAwareCommandInvocationDumper
from .two_word_keyword_isolator import TwoWordKeywordIsolator


class CustomCommandDumper(ArgumentAwareCommandInvocationDumper):
    def custom_command(self, tree):
        _, command_name, arguments, *_ = tree.children
        return self.visit(Tree("command_invocation", [command_name, arguments]))


def kind_to_formatter(kind: KeywordKind) -> str:
    return {
        KeywordKind.CommandLine: "_format_command_line",
        KeywordKind.Pairs: "_format_keyword_with_pairs",
    }.get(kind, "_default_format_values")


def string_to_kind(kind: Union[str, KeywordKind]) -> Optional[KeywordKind]:
    if isinstance(kind, KeywordKind):
        return kind

    return KeywordKind(kind) if kind in [e.value for e in KeywordKind] else None


def create_standard_dumper(data, custom_command=False):
    bases = [
        SectionAwareCommandInvocationDumper,
        TwoWordKeywordIsolator,
        CommandLineFormatter,
        KeywordWithPairsFormatter,
        ArgumentAwareCommandInvocationDumper,
    ]

    data_signatures = data.get("signatures", None)
    if data_signatures is not None:
        bases = [MultipleSignatureCommandInvocationDumper, *bases]

    if custom_command:
        bases = [CustomCommandDumper, *bases]

    class Impl(*bases):
        canonical_name = data.get("canonical_name", None)
        inhibit_favour_expansion = data.get("inhibit_favour_expansion", False)
        two_words_keywords = data.get("two_words_keywords", tuple())
        front_positional_arguments = data.get("front_positional_arguments", tuple())
        back_positional_arguments = data.get("back_positional_arguments", tuple())
        options = data.get("options", tuple())
        one_value_keywords = data.get("one_value_keywords", tuple())
        multi_value_keywords = data.get("multi_value_keywords", tuple())
        sections = data.get("sections", dict())

        if data_signatures is not None:
            signatures = data_signatures

        keyword_formatters = {
            keyword: kind_to_formatter(string_to_kind(kind))
            for keyword, kind in data.get("keyword_kinds", dict()).items()
        }

    return Impl
