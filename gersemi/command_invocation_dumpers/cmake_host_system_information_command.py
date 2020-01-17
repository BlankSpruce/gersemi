from gersemi.ast_helpers import contains_line_comment, is_keyword
from gersemi.base_command_invocation_dumper import BaseCommandInvocationDumper


def is_one_of_keywords(argument, keywords):
    predicates = map(is_keyword, keywords)
    invoke = lambda predicate: predicate(argument)
    return any(map(invoke, predicates))


def split_by_keywords(arguments, keywords):
    groups = []
    last_group = []
    for argument in arguments:
        if is_one_of_keywords(argument, keywords):
            groups.append(last_group)
            last_group = []
        last_group.append(argument)
    groups.append(last_group)
    return groups


class CMakeHostSysteInformationCommandDumper(BaseCommandInvocationDumper):
    def _format_group(self, group):
        result = self._try_to_format_into_single_line(group, separator=" ")
        if result is not None:
            return result
        query, *keys = group
        begin = self.visit(query)
        formatted_keys = self._indent("\n".join(self.visit(key) for key in keys))

        return f"{begin}\n{formatted_keys}"

    def format_command(self, tree):
        identifier, arguments = tree.children
        if not contains_line_comment(tree.children):
            result = self._try_to_format_into_single_line(
                [identifier, "(", " ".join(self.visit_children(arguments)), ")"]
            )
            if result is not None:
                return result

        begin = self._indent(f"{identifier}(")
        dumper = type(self)(self.alignment + self.indent_size)
        formatted_arguments = dumper.visit(arguments)
        end = self._indent(")")
        return f"{begin}{formatted_arguments}\n{end}"

    def arguments(self, tree):
        groups = split_by_keywords(tree.children, ["RESULT", "QUERY"])
        return "\n".join(map(self._format_group, groups))
