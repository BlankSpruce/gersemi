from functools import lru_cache
from gersemi.command_line_formatter import CommandLineFormatter
from gersemi.keyword_with_pairs_formatter import KeywordWithPairsFormatter
from gersemi.keyword_preprocessor import KeywordPreprocessor
from .argument_aware_command_invocation_dumper import (
    ArgumentAwareCommandInvocationDumper,
)
from .multiple_signature_command_invocation_dumper import (
    MultipleSignatureCommandInvocationDumper,
)
from .section_aware_command_invocation_dumper import SectionAwareCommandInvocationDumper
from .two_word_keyword_isolator import TwoWordKeywordIsolator


@lru_cache(maxsize=None)
def create_standard_dumper(data):
    bases = [
        SectionAwareCommandInvocationDumper,
        TwoWordKeywordIsolator,
        CommandLineFormatter,
        KeywordWithPairsFormatter,
        KeywordPreprocessor,
        ArgumentAwareCommandInvocationDumper,
    ]

    data_signatures = data.get("signatures", None)
    if data_signatures is not None:
        bases = [MultipleSignatureCommandInvocationDumper, *bases]

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
        keyword_formatters = data.get("keyword_formatters", dict())
        keyword_preprocessors = data.get("keyword_preprocessors", dict())

        if data_signatures is not None:
            signatures = data_signatures

    return Impl
