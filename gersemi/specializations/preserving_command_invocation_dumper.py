import re
from textwrap import indent
from gersemi.base_dumper import BaseDumper


BRACKET_ARGUMENT_REGEX = r"(\[(?P<equal_signs>(=*))\[(?:[\s\S]+?)\](?P=equal_signs)\])"
QUOTED_ARGUMENT_REGEX = r'("(?:[^\\\"]|\n|(?:\\(?:[^A-Za-z0-9]|[nrt]))|\\\n)*")'
LINE_COMMENT_BEGIN = "#"
BRACKET_COMMENT_BEGIN = "#["


def flat_split(pattern, string):
    m = re.search(pattern, string)
    if m is None:
        return (string,)

    begin, end = m.span()
    return string[:begin], string[begin:end], string[end:]


def split_by_line_comment(string):
    return flat_split(r"\s*" + LINE_COMMENT_BEGIN, string)


def split_by_bracket_arguments(string):
    return flat_split(BRACKET_ARGUMENT_REGEX, string)


def split_by_quoted_arguments(string):
    return re.split(QUOTED_ARGUMENT_REGEX, string)


def split_into_segments(string):
    head, *comment = split_by_line_comment(string)
    line_comment = "".join(comment)
    if '"' in head:
        head += line_comment
        line_comment = ""
    segments = split_by_bracket_arguments(head)
    result = [split_by_quoted_arguments(segment) for segment in segments]
    result += [[line_comment]]
    return [item for segment in result for item in segment if item != ""]


def indent_segment(segment, indent_symbol):
    if segment[:1] in ["[", '"']:
        return segment

    if segment.startswith(" ") or segment.startswith("\t"):
        return segment

    return indent(segment, indent_symbol, lambda s: not s.startswith("\n"))


def safe_indent(string, indent_symbol):
    segments = split_into_segments(string)
    return "".join(
        map(lambda segment: indent_segment(segment, indent_symbol), segments)
    )


def strip_empty_lines_from_edges(s):
    lines = s.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines)


def find_line_comment_begin(s):
    start = 0
    while True:
        index = s.rfind(LINE_COMMENT_BEGIN, start)
        if index == -1:
            return index

        if index == s.rfind(BRACKET_COMMENT_BEGIN, start):
            start = index + 1
        else:
            return index


def ends_with_line_comment(s):
    return find_line_comment_begin(s) != -1


def remove_common_beginning(s, other):
    index = 0
    for left, right in zip(s, other):
        if left != right:
            break
        index += 1

    return s[index:]


class PreservingCommandInvocationDumper(BaseDumper):
    def _preprocess_content(self, content):
        if content.strip() == "":
            return ""

        begin = "\n" if content.startswith("\n") else ""
        stripped_content = strip_empty_lines_from_edges(content)
        if ends_with_line_comment(stripped_content):
            end = "\n"
            return f"{begin}{stripped_content}{end}"

        end = "\n" if content.endswith("\n") else ""
        return f"{begin}{stripped_content.rstrip()}{end}"

    def custom_command(self, tree):
        indentation, raw_identifier, _, formatted_arguments = tree.children
        identifier = self.format_command_name(raw_identifier)
        begin = self._indent(f"{identifier}(")
        content = formatted_arguments.children[0]
        if content == "":
            return f"{begin})"

        with self.not_indented():
            result = self._try_to_format_into_single_line(
                formatted_arguments.children, prefix=begin, postfix=")"
            )
        if result is not None:
            return result

        indent_symbol = remove_common_beginning(self.indent_symbol, indentation)
        body = safe_indent(
            self._preprocess_content(content),
            indent_symbol,
        )
        if not content.startswith("\n"):
            body = body.lstrip(indent_symbol)

        if "\n" not in body:
            end = ")"
        elif body.endswith("\n"):
            end = self._indent(")")
        else:
            end = "\n" + self._indent(")")

        return f"{begin}{body}{end}"
