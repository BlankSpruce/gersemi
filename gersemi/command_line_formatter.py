from gersemi.ast_helpers import is_line_comment, is_commented_argument
from gersemi.base_dumper import BaseDumper


class CommandLineFormatter(BaseDumper):
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
