from gersemi.base_dumper import BaseDumper
from gersemi.command_invocation_dumper import CommandInvocationDumper


class Dumper(CommandInvocationDumper, BaseDumper):
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
        return self._indent("".join(tree.children)).rstrip()
