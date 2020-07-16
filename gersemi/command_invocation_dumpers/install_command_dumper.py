from lark import Tree
from lark.visitors import Transformer, Transformer_InPlace
from gersemi.ast_helpers import is_keyword, is_unquoted_argument
from gersemi.utils import advance
from .multiple_signature_command_invocation_dumper import (
    MultipleSignatureCommandInvocationDumper,
)


def is_includes(node) -> bool:
    return is_unquoted_argument(node) and node.children[0] == "INCLUDES"


is_destination = is_keyword("DESTINATION")


class PrependIncludes(Transformer):
    def unquoted_argument(self, children):
        return Tree("unquoted_argument", ["INCLUDES " + "".join(children)])


def prepend_includes(node):
    return PrependIncludes().transform(node)


class IsolateIncludeDestinationsKeyword(Transformer_InPlace):
    def arguments(self, children):
        new_children = []
        iterator = zip(children, children[1:])
        for one_behind, current in iterator:
            if is_includes(one_behind) and is_destination(current):
                new_children += [prepend_includes(current)]
                _, current = advance(iterator, times=1, default=(None, None))
                if current is None:
                    break
            else:
                new_children += [one_behind]
        else:
            new_children += [item for item in [current] if item is not None]
        return Tree("arguments", new_children)


class Install(MultipleSignatureCommandInvocationDumper):
    customized_signatures = {
        "TARGETS": dict(
            options=[
                "ARCHIVE",
                "LIBRARY",
                "RUNTIME",
                "OBJECTS",
                "FRAMEWORK",
                "BUNDLE",
                "PRIVATE_HEADER",
                "PUBLIC_HEADER",
                "RESOURCE",
                "OPTIONAL",
                "EXCLUDE_FROM_ALL",
                "NAMELINK_ONLY",
                "NAMELINK_SKIP",
            ],
            one_value_keywords=[
                "EXPORT",
                "DESTINATION",
                "COMPONENT",
                "NAMELINK_COMPONENT",
            ],
            multi_value_keywords=[
                "TARGETS",
                "PERMISSIONS",
                "CONFIGURATIONS",
                "INCLUDES DESTINATION",
            ],
        ),
        "FILES": dict(
            options=["OPTIONAL", "EXCLUDE_FROM_ALL"],
            one_value_keywords=["TYPE", "DESTINATION", "COMPONENT", "RENAME"],
            multi_value_keywords=["FILES", "PERMISSIONS", "CONFIGURATIONS"],
        ),
        "PROGRAMS": dict(
            options=["OPTIONAL", "EXCLUDE_FROM_ALL"],
            one_value_keywords=["TYPE", "DESTINATION", "COMPONENT", "RENAME"],
            multi_value_keywords=["PROGRAMS", "PERMISSIONS", "CONFIGURATIONS"],
        ),
        "DIRECTORY": dict(
            options=[
                "USE_SOURCE_PERMISSIONS",
                "OPTIONAL",
                "MESSAGE_NEVER",
                "EXCLUDE_FROM_ALL",
                "FILES_MATCHING",
                "EXCLUDE",
            ],
            one_value_keywords=["TYPE", "DESTINATION", "COMPONENT", "PATTERN", "REGEX"],
            multi_value_keywords=[
                "DIRECTORY",
                "FILE_PERMISSIONS",
                "DIRECTORY_PERMISSIONS",
                "CONFIGURATIONS",
                "PERMISSIONS",
            ],
        ),
        "SCRIPT": dict(
            options=["EXCLUDE_FROM_ALL"], one_value_keywords=["SCRIPT", "COMPONENT"]
        ),
        "CODE": dict(
            options=["EXCLUDE_FROM_ALL"], one_value_keywords=["CODE", "COMPONENT"]
        ),
        "EXPORT": dict(
            options=["EXPORT_LINK_INTERFACE_LIBRARIES", "EXCLUDE_FROM_ALL"],
            one_value_keywords=[
                "EXPORT",
                "DESTINATION",
                "NAMESPACE",
                "FILE",
                "COMPONENT",
            ],
            multi_value_keywords=["PERMISSIONS", "CONFIGURATIONS"],
        ),
        "EXPORT_ANDROID_MK": dict(
            options=["EXPORT_LINK_INTERFACE_LIBRARIES", "EXCLUDE_FROM_ALL"],
            one_value_keywords=[
                "EXPORT_ANDROID_MK",
                "DESTINATION",
                "NAMESPACE",
                "FILE",
                "COMPONENT",
            ],
            multi_value_keywords=["PERMISSIONS", "CONFIGURATIONS"],
        ),
    }

    def arguments(self, tree):
        preprocessed = IsolateIncludeDestinationsKeyword().transform(tree)
        return super().arguments(preprocessed)
