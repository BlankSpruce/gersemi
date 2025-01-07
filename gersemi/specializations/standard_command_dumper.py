from lark import Tree
from gersemi.command_line_formatter import CommandLineFormatter
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
        _canonical_name = data.get("_canonical_name", None)
        _inhibit_favour_expansion = data.get("_inhibit_favour_expansion", False)
        _two_words_keywords = data.get("_two_words_keywords", tuple())

        front_positional_arguments = data.get("front_positional_arguments", tuple())
        back_positional_arguments = data.get("back_positional_arguments", tuple())
        options = data.get("options", tuple())
        one_value_keywords = data.get("one_value_keywords", tuple())
        multi_value_keywords = data.get("multi_value_keywords", tuple())
        sections = data.get("sections", dict())
        keyword_kinds = data.get("keyword_kinds", dict())

        if data_signatures is not None:
            signatures = data_signatures

    return Impl
