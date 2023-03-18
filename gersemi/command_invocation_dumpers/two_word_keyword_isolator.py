from typing import Sequence, Tuple
from lark import Tree
from lark.visitors import Transformer, Transformer_InPlace
from gersemi.ast_helpers import is_keyword
from gersemi.base_command_invocation_dumper import BaseCommandInvocationDumper
from gersemi.utils import advance


class PrependLhs(Transformer):
    def __init__(self, lhs):
        super().__init__()
        self.lhs = lhs

    def unquoted_argument(self, children):
        return Tree("unquoted_argument", [self.lhs + " " + "".join(children)])


class IsolateTwoWordKeywords(Transformer_InPlace):
    def __init__(self, lhs, rhs):
        super().__init__()
        self.lhs = lhs
        self.rhs = rhs

    def _is_lhs(self, node):
        return is_keyword(self.lhs)(node)

    def _is_rhs(self, node):
        return is_keyword(self.rhs)(node)

    def _prepend_lhs(self, node):
        return PrependLhs(self.lhs).transform(node)

    def arguments(self, children):
        new_children = []
        iterator = zip(children, children[1:])
        for one_behind, current in iterator:
            if self._is_lhs(one_behind) and self._is_rhs(current):
                new_children += [self._prepend_lhs(current)]
                _, current = advance(iterator, times=1, default=(None, None))
                if current is None:
                    break
            else:
                new_children += [one_behind]
        else:
            new_children += [item for item in [current] if item is not None]
        return Tree("arguments", new_children)


class TwoWordKeywordIsolator(BaseCommandInvocationDumper):
    two_words_keywords: Sequence[Tuple[str, str]] = []

    def _preprocess_arguments(self, arguments):
        preprocessed = arguments
        for lhs, rhs in self.two_words_keywords:
            preprocessed = IsolateTwoWordKeywords(lhs, rhs).transform(preprocessed)
        return preprocessed
