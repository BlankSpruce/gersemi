from typing import Iterable, List, Tuple
from gersemi.ast_helpers import is_keyword, is_comment
from gersemi.types import Nodes
from .argument_aware_command_invocation_dumper import (
    ArgumentAwareCommandInvocationDumper,
    to_list_of_single_item_lists,
)


def split_into_chunks(iterable: Iterable) -> Iterable:
    iterator = iter(iterable)
    for item in iterator:
        if is_comment(item):
            yield [item]
        else:
            following_item = next(iterator, None)
            if following_item is None:
                yield [item]
            else:
                yield [item, following_item]


is_properties_keyword = is_keyword("PROPERTIES")


class CommandWithPropertyValuePairsDumper(ArgumentAwareCommandInvocationDumper):
    def _separate_front(self, arguments: Nodes) -> Tuple[List[Nodes], Nodes]:
        for index, argument in enumerate(arguments, start=1):
            if is_properties_keyword(argument):
                pivot = index
                break
        else:
            return to_list_of_single_item_lists(arguments), []
        return to_list_of_single_item_lists(arguments[:pivot]), arguments[pivot:]

    def _split_arguments(self, arguments: Nodes) -> List[Nodes]:
        head, tail = self._separate_front(arguments)
        return [*head, *split_into_chunks(tail)]
