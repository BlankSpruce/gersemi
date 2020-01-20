from typing import Iterator, List, Optional, Sized, Tuple
from gersemi.ast_helpers import contains_line_comment, is_keyword
from gersemi.base_command_invocation_dumper import BaseCommandInvocationDumper
from gersemi.types import Node, Nodes
from gersemi.utils import pop_all


def is_one_of_keywords(argument: Node, keywords: List[str]) -> bool:
    predicates = map(is_keyword, keywords)
    invoke = lambda predicate: predicate(argument)
    return any(map(invoke, predicates))


def split_by_positional_arguments(
    arguments: Nodes, N: int
) -> Tuple[List[Nodes], Nodes]:
    return [[argument] for argument in arguments[:N]], arguments[N:]


def is_non_empty(l: Sized) -> bool:
    return len(l) != 0


class ArgumentAwareCommandInvocationDumper(BaseCommandInvocationDumper):
    front_positional_args: int = 0
    options: List[str] = []
    one_value_keywords: List[str] = []
    multi_value_keywords: List[str] = []
    back_optional_args: int = 0

    def _format_group(self, group: Nodes) -> str:
        result = self._try_to_format_into_single_line(group, separator=" ")
        if result is not None:
            return result

        keyword, *values = group
        begin = self.visit(keyword)
        if len(values) == 0:
            return begin

        dumper = type(self)(self.alignment + self.indent_size)
        formatted_keys = "\n".join(dumper.visit(value) for value in values)
        return f"{begin}\n{formatted_keys}"

    def _split_by_keywords(self, arguments: Nodes) -> Tuple[Iterator[Nodes], Nodes]:
        groups: List[Nodes] = []
        accumulator: Nodes = []
        tail: Optional[Nodes] = None
        iterator = iter(arguments)
        for argument in iterator:
            if is_one_of_keywords(argument, self.options):
                groups += [pop_all(accumulator)]
                groups += [[argument]]
            elif is_one_of_keywords(argument, self.one_value_keywords):
                groups += [pop_all(accumulator)]
                groups += [[argument, next(iterator)]]
            elif is_one_of_keywords(argument, self.multi_value_keywords):
                groups += [pop_all(accumulator)]
                accumulator = [argument]
            elif is_non_empty(accumulator):
                accumulator += [argument]
            else:
                tail = [argument, *iterator]
                break

        groups += [pop_all(accumulator)]
        if tail is None:
            tail = [*iterator]
        return filter(is_non_empty, groups), tail

    def _split_arguments(self, arguments: Nodes) -> List[Nodes]:
        front, tail = split_by_positional_arguments(
            arguments, self.front_positional_args
        )
        keyworded_arguments, tail = self._split_by_keywords(tail)
        back, tail = split_by_positional_arguments(tail, self.back_optional_args)
        if is_non_empty(tail):
            return [*front, *keyworded_arguments, *back, *[[item] for item in tail]]
        return [*front, *keyworded_arguments, *back]

    def format_command(self, tree):
        identifier, arguments = tree.children
        if not contains_line_comment(tree.children):
            formatted_arguments = " ".join(
                type(self)(alignment=0).visit_children(arguments)
            )
            result = self._try_to_format_into_single_line(
                [identifier, "(", formatted_arguments, ")"]
            )
            if result is not None:
                return result

        begin = self._indent(f"{identifier}(")
        dumper = type(self)(self.alignment + self.indent_size)
        formatted_arguments = dumper.visit(arguments)
        end = self._indent(")")
        return f"{begin}\n{formatted_arguments}\n{end}"

    def arguments(self, tree):
        groups = self._split_arguments(tree.children)
        return "\n".join(map(self._format_group, groups))
