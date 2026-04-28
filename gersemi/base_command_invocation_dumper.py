from collections import defaultdict
from contextlib import contextmanager
from itertools import filterfalse
import re
from textwrap import indent
from typing import Dict, List, Optional, Sequence, Tuple, Union
import gersemi_rust_backend
from gersemi.argument_schema import ArgumentSchema, Signatures, create_schema_patch
from gersemi.ast_helpers import (
    get_value,
    is_comment,
    is_commented_argument,
    is_line_comment,
    is_line_comment_in,
    is_line_comment_in_any_of,
    is_multi_value_argument,
    is_one_value_argument,
    is_option_argument,
    is_pair,
    is_positional_arguments,
    is_section,
)
from gersemi.configuration import (
    Indent,
    ListExpansion,
    OutcomeConfiguration,
    SortOrder,
    Spaces,
    Tabs,
)
from gersemi.keyword_kind import kind_to_formatter
from gersemi.keywords import AnyMatcher
from gersemi.types import Nodes, Tree
from gersemi.warnings import FormatterWarnings, UnknownCommandWarning

BRACKET_ARGUMENT_REGEX = r"(\[(?P<equal_signs>(=*))\[(?:[\s\S]+?)\](?P=equal_signs)\])"
QUOTED_ARGUMENT_REGEX = r'("(?:[^\\\"]|\n|(?:\\(?:[^A-Za-z0-9]|[nrt]))|\\\n)*")'
LINE_COMMENT_BEGIN = "#"
BRACKET_COMMENT_BEGIN = "#["


def flat_split(pattern, string):
    m = re.search(pattern, string)
    if m is None:
        return (string,)

    begin, end = m.span()
    return string[:begin], string[begin:end], string[end:]


def split_by_line_comment(string):
    return flat_split(r"\s*" + LINE_COMMENT_BEGIN, string)


def split_by_bracket_arguments(string):
    return flat_split(BRACKET_ARGUMENT_REGEX, string)


def split_by_quoted_arguments(string):
    return re.split(QUOTED_ARGUMENT_REGEX, string)


def split_into_segments(string):
    head, *comment = split_by_line_comment(string)
    line_comment = "".join(comment)
    if '"' in head:
        head += line_comment
        line_comment = ""
    segments = split_by_bracket_arguments(head)
    result = [split_by_quoted_arguments(segment) for segment in segments]
    result += [[line_comment]]
    return [item for segment in result for item in segment if item != ""]


def indent_segment(segment, indent_symbol):
    if segment[:1] in ["[", '"']:
        return segment

    if segment.startswith(" ") or segment.startswith("\t"):
        return segment

    return indent(segment, indent_symbol, lambda s: not s.startswith("\n"))


def safe_indent(string, indent_symbol):
    segments = split_into_segments(string)
    return "".join(indent_segment(segment, indent_symbol) for segment in segments)


def strip_empty_lines_from_edges(s):
    lines = s.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines)


def find_line_comment_begin(s):
    start = 0
    while True:
        index = s.rfind(LINE_COMMENT_BEGIN, start)
        if index == -1:
            return index

        if index == s.rfind(BRACKET_COMMENT_BEGIN, start):
            start = index + 1
        else:
            return index


def ends_with_line_comment(s):
    return find_line_comment_begin(s) != -1


def remove_common_beginning(s, other):
    index = 0
    for left, right in zip(s, other):
        if left != right:
            break
        index += 1

    return s[index:]


def get_indent(indent_type: Indent) -> str:
    if isinstance(indent_type, Tabs):
        return "\t"
    return " " * indent_type


class WontFit(Exception):
    pass


class BaseCommandInvocationDumper:  # pylint: disable=too-many-instance-attributes,too-many-public-methods
    schema: ArgumentSchema
    signatures: Signatures = {}

    _inhibit_favour_expansion: bool = False
    _two_words_keywords: Sequence[Tuple[str, Union[str, AnyMatcher]]] = []
    _keyword_formatters: Dict[str, str] = {}
    _canonical_name: Optional[str] = None

    def __init__(self, configuration: OutcomeConfiguration):
        self.width = configuration.line_length
        self.indent_type = configuration.indent
        self._indent_symbol = get_indent(self.indent_type)
        self.indent_level = 0
        self.favour_expansion = False
        self.unknown_commands_used: Dict[str, List[Tuple[int, int]]] = defaultdict(list)
        self.list_expansion = configuration.list_expansion
        self.sort_order = configuration.sort_order

    def __default__(self, tree: Tree):
        return "".join(self.visit_children(tree))

    def visit(self, tree):
        f = getattr(self, tree.data, self.__default__)
        return f(tree)

    def visit_children(self, tree):
        yield from (
            self.visit(child) if isinstance(child, Tree) else str(child)
            for child in tree.children
        )

    @property
    def indent_symbol(self):
        return self._indent_symbol * self.indent_level

    def _indent(self, text: str):
        return indent(text, self.indent_symbol)

    def _single_line_helper(self, children, offset):
        width = offset
        for c in children:
            if isinstance(c, Tree):
                if is_line_comment_in(c):
                    raise WontFit()

                result = self.visit(c)
            else:
                result = str(c)

            if "\n" in result:
                raise WontFit()

            width += len(result)
            if width > self.width:
                raise WontFit()

            yield result
            width += 1

    def _try_to_format_into_single_line(
        self, children: Nodes, prefix: str = "", postfix: str = ""
    ) -> Optional[str]:
        if self.favour_expansion:
            return None

        try:
            reserved_space = len(prefix) + len(postfix) + len(self.indent_symbol)
            with self.not_indented():
                formatted = " ".join(self._single_line_helper(children, reserved_space))
            return f"{self.indent_symbol}{prefix}{formatted}{postfix}"
        except WontFit:
            return None

    @contextmanager
    def with_indent_level(self, indent_level):
        old_indent_level = self.indent_level
        try:
            self.indent_level = indent_level
            yield self
        finally:
            self.indent_level = old_indent_level

    def dedented(self):
        return self.with_indent_level(self.indent_level - 1)

    def indented(self):
        return self.with_indent_level(self.indent_level + 1)

    def not_indented(self):
        return self.with_indent_level(0)

    @contextmanager
    def select_expansion_strategy(self):
        old = self.favour_expansion
        try:
            self.favour_expansion = self.list_expansion == ListExpansion.FavourExpansion
            yield self
        finally:
            self.favour_expansion = old

    @contextmanager
    def select_inlining_strategy(self):
        old = self.favour_expansion
        try:
            self.favour_expansion = False
            yield self
        finally:
            self.favour_expansion = old

    def _record_unknown_command(self, command):
        self.unknown_commands_used[str(command)].append((command.line, command.column))

    def get_warnings(self) -> FormatterWarnings:
        if len(self.unknown_commands_used) == 0:
            return []

        return [
            UnknownCommandWarning(command_name=name, positions=positions)
            for name, positions in self.unknown_commands_used.items()
        ]

    def _format_keyword_with_pairs(self, args):
        return "\n".join(map(self.visit, gersemi_rust_backend.pair_arguments(args)))

    def start(self, tree):
        result = self.__default__(tree)
        if result.endswith("\n"):
            return result
        return result + "\n"

    def block(self, tree):
        return "\n".join(filter(None, map(self.visit, tree.children)))

    def block_body(self, tree):
        with self.indented():
            return "".join(self.visit_children(tree))

    def command_element(self, tree):
        invocation, *comment = tree.children
        formatted_invocation = self.visit(invocation)
        if len(comment) == 0:
            return formatted_invocation

        with self.not_indented():
            formatted_comment = self.visit(comment[0])

        return f"{formatted_invocation} {formatted_comment}"

    def non_command_element(self, tree):
        return " ".join(self.visit(child) for child in tree.children)

    def line_comment(self, tree):
        return self._indent("".join(map(str, tree.children))).rstrip()

    def standalone_identifier(self, tree):
        return f"{self.indent_symbol}{tree.children[0]}"

    def _default_format_values(self, values) -> str:
        return "\n".join(map(self.visit, values))

    def positional_arguments(self, tree) -> str:
        return "\n".join(map(self.visit, tree.children))

    def _format_non_option(self, tree):
        result = self._try_to_format_into_single_line(tree.children)
        if result is not None:
            return result

        keyword, *values = tree.children
        keyword_as_value = get_value(keyword, None)

        can_be_inlined = (not self.favour_expansion) or (
            keyword is not None
            and (not is_pair(tree))
            and (not is_multi_value_argument(tree))
        )
        if can_be_inlined:
            with self.select_inlining_strategy():
                result = self._try_to_format_into_single_line(tree.children)
                if result is not None:
                    return result

        begin = self.visit(keyword)
        if len(values) == 0:
            return begin

        formatter_kind = self._get_formatter(keyword_as_value)
        if formatter_kind is None:
            formatter_kind = self._keyword_formatters.get(
                keyword_as_value, "_default_format_values"
            )

        with self.indented():
            formatter = getattr(self, formatter_kind)
            formatted_values = formatter(values)
        return f"{begin}\n{formatted_values}"

    def option_argument(self, tree):
        return self.visit(tree.children[0])

    def one_value_argument(self, tree):
        return self._format_non_option(tree)

    def pair(self, tree):
        return self._format_non_option(tree)

    def _get_formatter(self, tree):
        return kind_to_formatter(
            self.schema.keyword_formatters.get(get_value(tree, None), None)
        )

    def _get_preprocessor(self, tree):
        return self.schema.keyword_preprocessors.get(get_value(tree, None), None)

    def _preprocess_keyword_values(self, nodes, preprocessor):
        return gersemi_rust_backend.preprocess_keyword_values(
            nodes=nodes,
            preprocessor=preprocessor,
            case_insensitive=self.sort_order == SortOrder.CaseInsensitive,
        )

    def multi_value_argument(self, tree):
        keyword, *values = tree.children
        preprocessor = self._get_preprocessor(keyword)
        if preprocessor is not None:
            tree.children = [
                keyword,
                *self._preprocess_keyword_values(values, preprocessor),
            ]

        return self._format_non_option(tree)

    def section(self, tree):
        header, *rest = tree.children
        preprocessor = self._get_preprocessor(header)
        if preprocessor is not None:
            rest = self._preprocess_keyword_values(rest, preprocessor)

        result = self._try_to_format_into_single_line(tree.children)
        if result is not None:
            return result

        begin = self.visit(header)
        if len(rest) == 0:
            return begin

        with self.indented():
            formatted_values = "\n".join(map(self.visit, rest))
        return f"{begin}\n{formatted_values}"

    def keyword_argument(self, tree):
        return self._format_non_option(tree)

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
        if is_positional_arguments(group):
            return len(group.children)
        if is_option_argument(group):
            return 0
        if is_one_value_argument(group):
            return len(group.children) - 1
        if is_multi_value_argument(group):
            return len(group.children) - 1
        if is_section(group):
            section_size = len(group.children) - 1
            subarguments_size = max(map(self.group_size, group.children))
            return max(section_size, subarguments_size)

        return 0

    def _inlining_condition(self, arguments):
        groups = self._split_arguments(arguments.children)
        group_sizes = list(map(self.group_size, groups))
        if (
            self.list_expansion == ListExpansion.FavourExpansion
            and not self._inhibit_favour_expansion
        ):
            return all(size < 2 for size in group_sizes)
        return all(size <= 4 for size in group_sizes)

    def format_command_name(self, identifier):
        identifier = str(identifier)
        if self._canonical_name is not None:
            canonical_name = self._canonical_name
        else:
            if "@" in identifier:
                return identifier

            return identifier.lower()

        if canonical_name.strip().lower() != identifier.strip().lower():
            raise RuntimeError

        return canonical_name

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
        groups = self._split_arguments(tree.children)
        return "\n".join(map(self.visit, filter(None, groups)))

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

    def _preprocess_content(self, content):
        if content.strip() == "":
            return ""

        begin = "\n" if content.startswith("\n") else ""
        stripped_content = strip_empty_lines_from_edges(content)
        if ends_with_line_comment(stripped_content):
            end = "\n"
            return f"{begin}{stripped_content}{end}"

        end = "\n" if content.endswith("\n") else ""
        return f"{begin}{stripped_content.rstrip()}{end}"

    def custom_command(self, tree):
        indentation, raw_identifier, _, formatted_arguments = tree.children
        identifier = self.format_command_name(raw_identifier)
        begin = self._indent(f"{identifier}(")
        content = formatted_arguments.children[0]
        if content == "":
            return f"{begin})"

        with self.not_indented():
            result = self._try_to_format_into_single_line(
                formatted_arguments.children, prefix=begin, postfix=")"
            )
        if result is not None:
            return result

        indent_symbol = remove_common_beginning(self.indent_symbol, indentation)
        body = safe_indent(
            self._preprocess_content(content),
            indent_symbol,
        )
        if not content.startswith("\n"):
            body = body.lstrip(indent_symbol)

        if "\n" not in body:
            end = ")"
        elif body.endswith("\n"):
            end = self._indent(")")
        else:
            end = "\n" + self._indent(")")

        return f"{begin}{body}{end}"

    def _should_start_new_line(self, updated_line, last_line):
        return (
            len(updated_line) > self.width
            or "\n" in updated_line
            or last_line.strip().startswith("#")
        )

    def _format_command_line(self, args):
        head, *tail = args
        lines = [self.visit(head)]
        force_next_line = is_commented_argument(head)
        for arg in tail:
            if is_line_comment(arg):
                lines += [self.visit(arg)]
                continue

            with self.not_indented():
                formatted_arg = self.visit(arg)
            updated_line = f"{lines[-1]} {formatted_arg}"
            if force_next_line or self._should_start_new_line(updated_line, lines[-1]):
                force_next_line = is_commented_argument(arg)
                lines += [self.visit(arg)]
            else:
                lines[-1] = updated_line
                if is_commented_argument(arg):
                    force_next_line = True

        return "\n".join(lines)
