from gersemi.command_line_formatter import CommandLineFormatter
from gersemi.keyword_with_pairs_formatter import KeywordWithPairsFormatter
from .argument_aware_command_invocation_dumper import (
    ArgumentAwareCommandInvocationDumper,
)
from .two_word_keyword_isolator import TwoWordKeywordIsolator


def create_standard_dumper(data):
    class Impl(
        TwoWordKeywordIsolator,
        CommandLineFormatter,
        KeywordWithPairsFormatter,
        ArgumentAwareCommandInvocationDumper,
    ):
        inhibit_favour_expansion = data.get("inhibit_favour_expansion", False)
        two_words_keywords = data.get("two_words_keywords", tuple())
        front_positional_arguments = data.get("front_positional_arguments", tuple())
        options = data.get("options", tuple())
        one_value_keywords = data.get("one_value_keywords", tuple())
        multi_value_keywords = data.get("multi_value_keywords", tuple())
        keyword_formatters = data.get("keyword_formatters", dict())

    return Impl
