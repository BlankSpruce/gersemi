# pylint: disable=too-many-lines
from .argument_aware_command_invocation_dumper import (
    ArgumentAwareCommandInvocationDumper,
)


class SetProperty(ArgumentAwareCommandInvocationDumper):
    options = ["GLOBAL", "APPEND", "APPEND_STRING"]
    multi_value_keywords = [
        "TARGET",
        "SOURCE",
        "INSTALL",
        "TEST",
        "CACHE",
        "PROPERTY",
        "TARGET_DIRECTORIES",
        "DIRECTORY",
    ]
    _keyword_formatters = {"PROPERTY": "_format_property"}

    def _format_property(self, args):
        result = self._try_to_format_into_single_line(args, prefix="", postfix="")
        if result is not None:
            return result

        name, *rest = args
        with self.indented():
            formatted_rest = "\n".join(map(self.visit, rest))
        return f"{self.visit(name)}\n{formatted_rest}"


set_property = {"set_property": SetProperty}
