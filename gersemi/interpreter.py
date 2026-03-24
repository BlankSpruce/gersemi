from lark import Tree


class Interpreter:
    def visit_children(self, tree):
        return [
            self.visit(child) if isinstance(child, Tree) else child
            for child in tree.children
        ]

    def __default__(self, tree):
        return self.visit_children(tree)

    def visit(self, tree):
        f = getattr(self, tree.data, self.__default__)
        return f(tree)
