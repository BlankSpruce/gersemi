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


def create_standard_dumper(data):
    bases = [
        SectionAwareCommandInvocationDumper,
        TwoWordKeywordIsolator,
        CommandLineFormatter,
        KeywordWithPairsFormatter,
        ArgumentAwareCommandInvocationDumper,
    ]

    data_customized_signatures = data.get("customized_signatures", None)
    if data_customized_signatures is not None:
        bases = [MultipleSignatureCommandInvocationDumper, *bases]

    class Impl(*bases):
        canonical_name = data.get("canonical_name", None)
        inhibit_favour_expansion = data.get("inhibit_favour_expansion", False)
        two_words_keywords = data.get("two_words_keywords", tuple())
        front_positional_arguments = data.get("front_positional_arguments", tuple())
        options = data.get("options", tuple())
        one_value_keywords = data.get("one_value_keywords", tuple())
        multi_value_keywords = data.get("multi_value_keywords", tuple())
        keyword_formatters = data.get("keyword_formatters", dict())
        sections = data.get("sections", dict())

        if data_customized_signatures is not None:
            customized_signatures = data_customized_signatures

    return Impl
