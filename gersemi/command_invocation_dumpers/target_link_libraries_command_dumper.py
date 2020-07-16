from lark import Tree
from lark.visitors import Transformer_InPlace
from gersemi.ast_helpers import is_one_of_keywords
from gersemi.utils import advance
from .argument_aware_command_invocation_dumper import (
    ArgumentAwareCommandInvocationDumper,
)


class IsolateConfigurationTypeAndItem(Transformer_InPlace):
    keywords = ["debug", "optimized", "general"]

    def arguments(self, children):
        new_children = []
        iterator = zip(children, children[1:])
        is_one_of_defined_keywords = is_one_of_keywords(self.keywords)
        for one_behind, current in iterator:
            if is_one_of_defined_keywords(one_behind):
                new_children += [Tree("specified_item", [one_behind, current])]
                _, current = advance(iterator, times=1, default=(None, None))
                if current is None:
                    break
            else:
                new_children += [one_behind]
        else:
            new_children += [item for item in [current] if item is not None]
        return Tree("arguments", new_children)


class TargetLinkLibraries(ArgumentAwareCommandInvocationDumper):
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
        formatted_specifier = self.visit(specifier)
        with self.not_indented():
            formatted_item = self.visit(item)
        return f"{formatted_specifier} {formatted_item}"

    def arguments(self, tree):
        preprocessed = IsolateConfigurationTypeAndItem().transform(tree)
        return super().arguments(preprocessed)
