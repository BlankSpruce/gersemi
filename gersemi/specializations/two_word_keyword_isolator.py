from typing import Sequence, Tuple, Union
import gersemi_rust_backend
from gersemi.keywords import AnyMatcher
from gersemi.specializations.argument_aware_command_invocation_dumper import (
    ArgumentAwareCommandInvocationDumper,
)


class TwoWordKeywordIsolator(ArgumentAwareCommandInvocationDumper):
    _two_words_keywords: Sequence[Tuple[str, Union[str, AnyMatcher]]] = []

    def _preprocess_arguments(self, arguments):
        return gersemi_rust_backend.two_words_keyword_isolator_preprocess_arguments(
            self._two_words_keywords, arguments
        )

    def keyword_argument(self, tree):
        return self._format_non_option(tree)
