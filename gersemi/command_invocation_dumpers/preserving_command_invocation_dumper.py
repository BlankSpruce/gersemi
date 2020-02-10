import re
from gersemi.base_dumper import BaseDumper
from gersemi.indenter import indent


BRACKET_ARGUMENT_REGEX = r"(\[(?P<equal_signs>(=*))\[(?:[\s\S]+?)\](?P=equal_signs)\])"
QUOTED_ARGUMENT_REGEX = r'("(?:[^\\\"]|\n|(?:\\(?:[^A-Za-z0-9]|[nrt]))|\\\n)*")'


def split_by_bracket_arguments(string):
    return re.split(BRACKET_ARGUMENT_REGEX, string)


def split_by_quoted_arguments(string):
    return re.split(QUOTED_ARGUMENT_REGEX, string)


def split_into_segments(string):
    segments = split_by_bracket_arguments(string)
    result = [split_by_quoted_arguments(segment) for segment in segments]
    return [item for segment in result for item in segment if item != ""]


def indent_segment(segment, indent_size):
    if segment[:1] in ["[", '"']:
        return segment
    return indent(segment, indent_size)


def safe_indent(string, indent_size):
    segments = split_into_segments(string)
    segment_indenter = lambda segment: indent_segment(segment, indent_size)
    return "".join(map(segment_indenter, segments))


class PreservingCommandInvocationDumper(BaseDumper):
    def formatted_command_element(self, tree):
        content, *_ = tree.children
        if content[: self.alignment] != " " * self.alignment:
            return safe_indent(content, self.alignment)
        return content
