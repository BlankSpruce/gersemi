from lark import Discard, Tree
from lark.exceptions import VisitError


class Transformer_InPlace:
    def _transform_children(self, children):
        for c in children:
            res = self.transform(c) if isinstance(c, Tree) else c

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
