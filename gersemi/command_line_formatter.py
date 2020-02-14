from gersemi.base_dumper import BaseDumper


class CommandLineFormatter(BaseDumper):
    def _format_command_line(self, args):
        head, *tail = args
        lines = [self.visit(head)]
        for arg in tail:
            formatted_arg = self.with_no_indentation.visit(arg)
            updated_line = f"{lines[-1]} {formatted_arg}"
            if len(updated_line) > self.width or "\n" in updated_line:
                lines += [self.visit(arg)]
            else:
                lines[-1] = updated_line
        return "\n".join(lines)
