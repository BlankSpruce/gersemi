from gersemi.argument_schema import Sections
from .argument_aware_command_invocation_dumper import (
    ArgumentAwareCommandInvocationDumper,
)


class SectionAwareCommandInvocationDumper(ArgumentAwareCommandInvocationDumper):
    sections: Sections = {}

    def section(self, tree):
        header, *rest = tree.children
        preprocessor = self._get_preprocessor(header)
        if preprocessor is not None:
            rest = getattr(self, preprocessor)(rest)

        result = self._try_to_format_into_single_line(tree.children)
        if result is not None:
            return result

        begin = self.visit(header)
        if len(rest) == 0:
            return begin

        with self.indented():
            formatted_values = "\n".join(map(self.visit, rest))
        return f"{begin}\n{formatted_values}"
