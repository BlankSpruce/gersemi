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


@lru_cache(maxsize=None)
def create_standard_dumper(data):
    bases = [
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

        schema = data.schema

        if data.signatures:
            signatures = data.signatures

    return Impl


@lru_cache(maxsize=None)
def create_specialized_dumper(data):
    class Impl(data.impl):
        _canonical_name = data.canonical_name

    return Impl
