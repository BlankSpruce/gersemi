from lark.visitors import Transformer_InPlace


def indent_line(line):
    if line == "":
        return ""
    return "    " + line


def indent_child(child):
    return "\n".join(map(indent_line, child.split("\n")))


class DumpToString(Transformer_InPlace):
    def __default__(self, data, children, meta):
        return "".join(children)

    def block_body(self, children):
        return "".join(map(indent_child, children))
