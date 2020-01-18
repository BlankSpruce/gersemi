from .keyword_aware_command_invocation_dumper import KeywordAwareCommandInvocationDumper


class ConfigureFileCommandDumper(KeywordAwareCommandInvocationDumper):
    def arguments(self, tree):
        input_file, output_file, *flags = tree.children
        groups = [[input_file], [output_file], flags]
        return "\n".join(map(self._format_group, groups))
