from typing import Sequence, Tuple, Union
from lark import Tree
from lark.visitors import Transformer_InPlace
from gersemi.ast_helpers import is_keyword, is_comment
from gersemi.base_command_invocation_dumper import BaseCommandInvocationDumper
from gersemi.keywords import AnyMatcher


class IsolateTwoWordKeywords(Transformer_InPlace):
    def __init__(self, lhs, rhs):
        super().__init__()
        self.lhs = lhs
        self.rhs = rhs

    def _is_lhs(self, node):
        return is_keyword(self.lhs)(node)

    def _is_rhs(self, node):
        return is_keyword(self.rhs)(node)

    def arguments(self, children):
        if len(children) <= 1:
            return Tree("arguments", children)

        new_children = []
        accumulator = []
        iterator = iter(children)
        for child in iterator:
            if len(accumulator) > 0:
                if is_comment(child):
                    accumulator.append(child)
                elif self._is_rhs(child):
                    new_children.append(Tree("keyword_argument", [*accumulator, child]))
                    accumulator = []
                else:
                    new_children.extend(accumulator)
                    accumulator = [child]
            else:
                if self._is_lhs(child):
                    accumulator = [child]
                else:
                    new_children.append(child)

        if len(accumulator) > 0:
            new_children.extend(accumulator)

        return Tree("arguments", new_children)


class TwoWordKeywordIsolator(BaseCommandInvocationDumper):
    two_words_keywords: Sequence[Tuple[str, Union[str, AnyMatcher]]] = []

    def _preprocess_arguments(self, arguments):
        preprocessed = arguments
        for lhs, rhs in self.two_words_keywords:
            preprocessed = IsolateTwoWordKeywords(lhs, rhs).transform(preprocessed)
        return preprocessed

    def keyword_argument(self, tree):
        result = self._try_to_format_into_single_line(tree.children, separator=" ")
        if result is not None:
            return result

        return "\n".join(map(self.visit, tree.children))
