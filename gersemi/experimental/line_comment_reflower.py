from lark import Discard, Tree, Token
from lark.visitors import TransformerChain, Transformer_InPlace, v_args


class NormalizeEmptyLineComments(Transformer_InPlace):
    @v_args(meta=True)
    def line_comment(self, children, meta):
        if len(children) == 1:
            pound_sign, *_ = children
            line_comment_content = Token(
                type_="LINE_COMMENT_CONTENT",
                value="",
                line=pound_sign.line,
                column=pound_sign.end_column,
                end_line=pound_sign.line,
                end_column=pound_sign.end_column,
            )
            return Tree("line_comment", [pound_sign, line_comment_content], meta)
        return Tree("line_comment", children, meta)


class RstripLineComments(Transformer_InPlace):
    def _strip(self, comment):
        comment.children[1] = comment.children[1].rstrip()

    @v_args(meta=True)
    def line_comment(self, children, meta):
        pound_sign, content = children
        return Tree("line_comment", [pound_sign, content.strip()], meta)


class MergeConsecutiveLineComments(Transformer_InPlace):
    def __init__(self, code):
        super().__init__()
        self.code_lines = code.split("\n")
        self.expected_line = 0
        self.expected_column = 0

    def _is_nothing_but_space_before_comment(self, line, column):
        return set(self.code_lines[line - 1][: column - 1]).issubset(set(" \t"))

    def _is_expected_location(self, line, column):
        return (line, column) == (self.expected_line, self.expected_column)

    def _should_be_merged(self, comment_node):
        line, column = comment_node.meta.line, comment_node.meta.column
        conditions = [
            self._is_expected_location(line, column),
            self._is_nothing_but_space_before_comment(line, column),
        ]
        return all(conditions)

    def _is_line_comment_empty(self, comment):
        return comment.children[1] != ""

    def _merge(self, last_comment, new_comment):
        if self._is_line_comment_empty(new_comment):
            last_comment.children[1] += " " + new_comment.children[1].lstrip()
        new_comment.data = "node_to_discard"

    def start(self, children):
        file, *_ = children

        last_comment = None
        for node in file.find_data("line_comment"):
            if last_comment is None or not self._should_be_merged(node):
                last_comment = node
                self.expected_line = node.meta.line + 1
                self.expected_column = node.meta.column
                continue

            self._merge(last_comment, node)
            self.expected_line += 1

        return Tree("start", [file])


class RemoveNodesToDiscard(Transformer_InPlace):
    def node_to_discard(self, _):
        raise Discard()


class RemoveSuperfluousEmptyComments(Transformer_InPlace):
    def line_comment(self, children):
        _, content = children
        if content == "":
            raise Discard()
        return Tree("line_comment", children)


def LineCommentReflower(code):
    return TransformerChain(
        NormalizeEmptyLineComments(),
        RstripLineComments(),
        MergeConsecutiveLineComments(code),
        RemoveNodesToDiscard(),
        RemoveSuperfluousEmptyComments(),
    )
