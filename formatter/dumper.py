from lark.visitors import Transformer_InPlace


def indent_body(body):
    if body[-1] == '\n':
        return indent_body(body[:-1]) + "\n"

    if body[0] == '\n':
        return "\n" + indent_body(body[1:])

    indented_body = []
    for line in body.split('\n'):
        if line == "":
            indented_body.append("")
        else:
            indented_body.append("    " + line)
    return "\n".join(indented_body)


class DumpToString(Transformer_InPlace):
    def __default__(self, *args):
        _, children, _ = args
        return "".join(children)

    def block(self, children):
        begin, body, end = children
        return "{}{}{}".format(begin, indent_body(body), end)
