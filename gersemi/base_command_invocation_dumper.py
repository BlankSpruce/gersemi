from contextlib import contextmanager
from itertools import filterfalse
from typing import Sequence, Tuple, Union
import gersemi_rust_backend
from gersemi.argument_schema import ArgumentSchema, Signatures, create_schema_patch
from gersemi.ast_helpers import is_comment, is_line_comment_in_any_of
from gersemi.base_dumper import BaseDumper
from gersemi.configuration import ListExpansion, Spaces
from gersemi.keywords import AnyMatcher
from gersemi.types import Nodes


class BaseCommandInvocationDumper(BaseDumper):
    schema: ArgumentSchema
    signatures: Signatures = {}

    _inhibit_favour_expansion: bool = False
    _two_words_keywords: Sequence[Tuple[str, Union[str, AnyMatcher]]] = []

    def format_command_with_short_name(self, begin, arguments, end):
        with self.indented():
            formatted_arguments = self.visit(arguments).lstrip()
        if (
            not is_line_comment_in_any_of(arguments.children)
            and "\n" not in formatted_arguments
        ):
            return "".join([self._indent(begin), formatted_arguments, end])

        return f"{self._indent(begin)}{formatted_arguments}\n{self._indent(end)}"

    def _format_command_with_long_name(self, begin, arguments, end):
        with self.indented():
            formatted_arguments = self.visit(arguments)
        return "\n".join([self._indent(begin), formatted_arguments, self._indent(end)])

    def _split_arguments(self, arguments: Nodes) -> Nodes:
        return gersemi_rust_backend.dumper_split_arguments(
            self.schema,
            arguments,
        )

    def group_size(self, group):
        return len(group)

    def _inlining_condition(self, arguments):
        groups = self._split_arguments(arguments.children)
        group_sizes = list(map(self.group_size, groups))
        if (
            self.list_expansion == ListExpansion.FavourExpansion
            and not self._inhibit_favour_expansion
        ):
            return all(size < 2 for size in group_sizes)
        return all(size <= 4 for size in group_sizes)

    def format_signature(self, tree):
        raw_identifier, arguments = tree.children
        identifier = self.format_command_name(raw_identifier)
        arguments = self._preprocess_arguments(arguments)
        begin = f"{identifier}("
        end = ")"

        result = self._try_to_format_into_single_line(
            arguments.children, prefix=begin, postfix=end
        )
        if result is not None and self._inlining_condition(arguments):
            return result

        with self.select_expansion_strategy():
            if isinstance(self.indent_type, Spaces) and len(begin) == self.indent_type:
                return self.format_command_with_short_name(begin, arguments, end)
            return self._format_command_with_long_name(begin, arguments, end)

    def arguments(self, tree):
        return "\n".join(self.visit_children(tree))

    def commented_argument(self, tree):
        argument, comment, *_ = tree.children
        formatted_argument = self.visit(argument)
        with self.not_indented():
            formatted_comment = self.visit(comment)
        return f"{formatted_argument} {formatted_comment}"

    def complex_argument(self, tree):
        arguments, *_ = tree.children
        if len(arguments.children) <= 4:
            result = self._try_to_format_into_single_line(
                arguments.children, prefix="(", postfix=")"
            )
            if result is not None:
                return result

        begin = self._indent("(\n")
        with self.indented():
            formatted_arguments = self.visit(arguments)
        end = self._indent(")")
        return f"{begin}{formatted_arguments}\n{end}"

    def bracket_comment(self, tree):
        return f"{self.indent_symbol}{''.join(map(str, tree.children))}"

    def bracket_argument(self, tree):
        return f"{self.indent_symbol}{tree.children[0]}"

    def quoted_argument(self, tree):
        return f"{self.indent_symbol}{tree.children[0]}"

    def unquoted_argument(self, tree):
        return f"{self.indent_symbol}{tree.children[0]}"

    def _preprocess_arguments(self, arguments):
        return gersemi_rust_backend.isolate_two_words_keywords(
            self._two_words_keywords, arguments
        )

    @contextmanager
    def _update_signature_characteristics(self, signature):
        if signature is None:
            yield
            return

        old_class = type(self)
        try:
            self.__class__ = create_schema_patch(signature, old_class)
            yield
        finally:
            self.__class__ = old_class

    def _get_signature(self, keyword):
        for item, signature in self.signatures.items():
            if item is None:
                continue

            if gersemi_rust_backend.is_one_of_keywords([item], keyword):
                return signature

        return self.signatures.get(None, None)

    def format_command(self, tree):
        _, arguments = tree.children
        arguments = self._preprocess_arguments(arguments)
        arguments_only = filterfalse(is_comment, arguments.children)
        signature = None
        for argument in arguments_only:
            signature = self._get_signature(argument)
            if signature is not None:
                break

        with self._update_signature_characteristics(signature):
            return self.format_signature(tree)
