from typing import Sequence, Tuple, Union
from lark import Tree
from gersemi.ast_helpers import is_comment, is_keyword
from gersemi.keywords import AnyMatcher
from gersemi.specializations.argument_aware_command_invocation_dumper import (
    ArgumentAwareCommandInvocationDumper,
)


def isolate_two_word_keywords(lhs, rhs, children):
    accumulator = []
    for child in children:
        if accumulator:
            if is_comment(child):
                accumulator.append(child)
            elif is_keyword(rhs, child):
                yield Tree("keyword_argument", [*accumulator, child])
                accumulator = []
            else:
                yield from accumulator
                accumulator = [child]
        else:
            if is_keyword(lhs, child):
                accumulator = [child]
            else:
                yield child

    yield from accumulator


class TwoWordKeywordIsolator(ArgumentAwareCommandInvocationDumper):
    _two_words_keywords: Sequence[Tuple[str, Union[str, AnyMatcher]]] = []

    def _preprocess_arguments(self, arguments):
        preprocessed = arguments.children
        for lhs, rhs in self._two_words_keywords:
            preprocessed = isolate_two_word_keywords(lhs, rhs, preprocessed)
        arguments.children = list(preprocessed)
        return arguments

    def keyword_argument(self, tree):
        return self._format_non_option(tree)
