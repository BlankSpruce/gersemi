from itertools import zip_longest
from typing import Iterable, List
from gersemi.types import Nodes
from .argument_aware_command_invocation_dumper import (
    ArgumentAwareCommandInvocationDumper,
)


def split_into_chunks(iterable: Iterable) -> Iterable:
    chunk_size = 2
    args = [iter(iterable)] * chunk_size
    return zip_longest(*args, fillvalue="")


class SetDirectoryPropertiesCommandDumper(ArgumentAwareCommandInvocationDumper):
    def _split_arguments(self, arguments: Nodes) -> List[Nodes]:
        head, *rest = arguments
        return [[head], *split_into_chunks(rest)]
