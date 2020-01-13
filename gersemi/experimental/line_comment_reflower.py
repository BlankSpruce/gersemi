from lark import Discard, Tree, Token
from lark.tree import Meta
from lark.visitors import Transformer, TransformerChain, Transformer_InPlace, v_args


class NormalizeEmptyLineComments(Transformer_InPlace):
    @v_args(meta=True)
    def line_comment(self, children, meta: Meta) -> Tree:
        if len(children) == 0:
            line_comment_content = Token(type_="LINE_COMMENT_CONTENT", value="")
            return Tree("line_comment", [line_comment_content], meta)
        return Tree("line_comment", children, meta)


class RstripLineComments(Transformer_InPlace):
    @v_args(meta=True)
    def line_comment(self, children, meta: Meta) -> Tree:
        *_, content = children
        return Tree("line_comment", [content.strip()], meta)


class MergeConsecutiveLineComments(Transformer_InPlace):
    def __init__(self, code: str):
        super().__init__()
        self.code_lines = code.split("\n")
        self.expected_line = 0
        self.expected_column = 0

    def _is_nothing_but_space_before_comment(self, line: int, column: int) -> bool:
        return set(self.code_lines[line - 1][: column - 1]).issubset(set(" \t"))

    def _is_expected_location(self, line: int, column: int) -> bool:
        return (line, column) == (self.expected_line, self.expected_column)

    def _should_be_merged(self, comment_node: Tree) -> bool:
        line, column = comment_node.meta.line, comment_node.meta.column
        conditions = [
            self._is_expected_location(line, column),
            self._is_nothing_but_space_before_comment(line, column),
        ]
        return all(conditions)

    def _is_line_comment_empty(self, comment: Tree) -> bool:
        return comment.children[0] != ""

    def _merge(self, last_comment, new_comment):
        if self._is_line_comment_empty(new_comment):
            last_comment.children[0] += " " + new_comment.children[0].lstrip()
        new_comment.data = "node_to_discard"

    def start(self, children) -> Tree:
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
        *_, content = children
        if content == "":
            raise Discard()
        return Tree("line_comment", children)


def LineCommentReflower(code: str) -> Transformer:
    return TransformerChain(
        NormalizeEmptyLineComments(),
        RstripLineComments(),
        MergeConsecutiveLineComments(code),
        RemoveNodesToDiscard(),
        RemoveSuperfluousEmptyComments(),
    )
