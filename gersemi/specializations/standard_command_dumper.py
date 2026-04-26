from functools import lru_cache
from gersemi.command_line_formatter import CommandLineFormatter
from .argument_aware_command_invocation_dumper import (
    ArgumentAwareCommandInvocationDumper,
)


@lru_cache(maxsize=None)
def create_standard_dumper(data):
    class Impl(CommandLineFormatter, ArgumentAwareCommandInvocationDumper):
        _canonical_name = data.canonical_name
        _inhibit_favour_expansion = data.inhibit_favour_expansion
        _two_words_keywords = data.two_words_keywords
        schema = data.schema
        signatures = data.signatures

    return Impl


@lru_cache(maxsize=None)
def create_specialized_dumper(data):
    class Impl(data.impl):
        _canonical_name = data.canonical_name

    return Impl
