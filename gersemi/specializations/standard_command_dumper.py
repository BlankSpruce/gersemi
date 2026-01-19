from functools import lru_cache
from gersemi.command_line_formatter import CommandLineFormatter
from gersemi.keyword_preprocessor import KeywordPreprocessor
from gersemi.keyword_with_pairs_formatter import KeywordWithPairsFormatter
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
        _two_words_keywords = data.get("_two_words_keywords", ())

        front_positional_arguments = data.get("front_positional_arguments", ())
        back_positional_arguments = data.get("back_positional_arguments", ())
        options = data.get("options", ())
        one_value_keywords = data.get("one_value_keywords", ())
        multi_value_keywords = data.get("multi_value_keywords", ())
        sections = data.get("sections", {})
        keyword_formatters = data.get("keyword_formatters", {})
        keyword_preprocessors = data.get("keyword_preprocessors", {})
        inlining_heuristic = data.get("inlining_heuristic", None)

        if data_signatures is not None:
            signatures = data_signatures

    return Impl


@lru_cache(maxsize=None)
def create_specialized_dumper(data):
    class Impl(data["__impl"]):
        _canonical_name = data.get("_canonical_name", None)

    return Impl
