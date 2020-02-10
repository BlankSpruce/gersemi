from lark import Tree
from lark.visitors import Transformer_InPlace
from gersemi.utils import advance
from .argument_aware_command_invocation_dumper import (
    ArgumentAwareCommandInvocationDumper,
    is_one_of_keywords,
)


class IsolateConfigurationTypeAndItem(Transformer_InPlace):
    keywords = ["debug", "optimized", "general"]

    def arguments(self, children):
        new_children = []
        iterator = zip(children, children[1:])
        for one_behind, current in iterator:
            if is_one_of_keywords(one_behind, self.keywords):
                new_children += [Tree("specified_item", [one_behind, current])]
                _, current = advance(iterator, times=1, default=(None, None))
                if current is None:
                    break
            else:
                new_children += [one_behind]
        else:
            new_children += [item for item in [current] if item is not None]
        return Tree("arguments", new_children)


class TargetLinkLibrariesCommandDumper(ArgumentAwareCommandInvocationDumper):
    multi_value_keywords = [
        "INTERFACE",
        "PUBLIC",
        "PRIVATE",
        "LINK_PRIVATE",
        "LINK_PUBLIC",
        "LINK_INTERFACE_LIBRARIES",
    ]

    def specified_item(self, tree):
        specifier, item = tree.children
        return "{} {}".format(
            self.visit(specifier), self.with_no_indentation.visit(item)
        )

    def arguments(self, tree):
        preprocessed = IsolateConfigurationTypeAndItem().transform(tree)
        return super().arguments(preprocessed)
