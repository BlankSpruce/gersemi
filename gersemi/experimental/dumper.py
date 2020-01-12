from itertools import repeat
import gersemi.dumper
from gersemi.indenter import prefix
from gersemi.width_limiting_buffer import WidthLimitingBuffer


def format_comment_content(content, width):
    buffer = WidthLimitingBuffer(width)
    content = " ".join(map(str.lstrip, content.split("\n")))
    first_item, *rest = content.lstrip().split(" ")
    buffer += first_item
    for item in rest:
        buffer += " "
        buffer += item
    return str(buffer)


class Dumper(gersemi.dumper.Dumper):
    def non_command_element(self, tree):
        return self.__default__(tree)

    def line_comment(self, tree):
        _, content = tree.children
        comment_start = "# "
        formatted_content = format_comment_content(
            content, self.width - self.alignment - len(comment_start)
        )
        return self._indent(prefix(formatted_content, repeat(comment_start)))

    def bracket_comment(self, tree):
        result = self._try_to_format_into_single_line(tree)
        if result is not None:
            return result
        return self._indent("\n".join(self.visit_children(tree)))

    def bracket_comment_body(self, tree):
        content, *_ = tree.children
        return format_comment_content(content, self.width - self.alignment)
