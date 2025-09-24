from lark import Discard, Tree
from lark.exceptions import VisitError


class Transformer_InPlace:
    def _transform_children(self, children):
        for c in children:
            if isinstance(c, Tree):
                res = self.transform(c)
            else:
                res = c

            if res is not Discard:
                yield res

    def transform(self, tree):
        tree.children = list(self._transform_children(tree.children))
        try:
            f = getattr(self, tree.data)
        except AttributeError:
            return tree

        try:
            return f(tree.children)
        except Exception as e:
            raise VisitError(tree.data, tree, e) from e


class TransformerChain:
    def __init__(self, *transformers):
        self.transformers = transformers

    def transform(self, tree: Tree):
        for t in self.transformers:
            tree = t.transform(tree)

        return tree
