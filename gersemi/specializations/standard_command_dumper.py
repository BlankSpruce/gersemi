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

    if data.signatures:
        bases = [MultipleSignatureCommandInvocationDumper, *bases]

    class Impl(*bases):
        _canonical_name = data.canonical_name
        _inhibit_favour_expansion = data.inhibit_favour_expansion
        _two_words_keywords = data.two_words_keywords

        front_positional_arguments = data.schema.front_positional_arguments
        back_positional_arguments = data.schema.back_positional_arguments
        options = data.schema.options
        one_value_keywords = data.schema.one_value_keywords
        multi_value_keywords = data.schema.multi_value_keywords
        sections = data.schema.sections
        keyword_formatters = data.schema.keyword_formatters
        keyword_preprocessors = data.schema.keyword_preprocessors

        if data.signatures:
            signatures = data.signatures

    return Impl


@lru_cache(maxsize=None)
def create_specialized_dumper(data):
    class Impl(data.impl):
        _canonical_name = data.canonical_name

    return Impl
