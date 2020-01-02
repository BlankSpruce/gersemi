from itertools import filterfalse
from formatter.ast_helpers import is_space, is_newline
from lark import Discard, Tree, Token
from lark.visitors import TransformerChain, Transformer_InPlace, Interpreter


def remove_if_space(children, index):
    if len(children) > 0 and is_space(children[index]):
        children.pop(index)


def is_space_at_line_beginning(element):
    return is_space(element) and element.column == 1


class RemoveSuperfluousSpaces(Transformer_InPlace):
    def file_element(self, children):
        remove_if_space(children, index=0)
        remove_if_space(children, index=-1)
        return Tree("file_element", children)

    def command_element(self, children):
        _, command_invocation, trailing_space, *rest = children
        if len(rest) == 0:
            return Tree("command_invocation", command_invocation.children)
        return Tree("command_element", [command_invocation, trailing_space, *rest])

    def non_command_element(self, children):
        remove_if_space(children, index=0)
        if len(children) == 0:
            raise Discard()
        return Tree("non_command_element", children)

    def command_invocation(self, children):
        remove_if_space(children, index=1)
        return Tree("command_invocation", children)

    def arguments(self, children):
        remove_if_space(children, index=0)
        remove_if_space(children, index=-1)
        children = [*filterfalse(is_space_at_line_beginning, children)]

        return Tree("arguments", children)


class ReduceSpacesToOneCharacter(Transformer_InPlace):
    def SPACE(self, _):
        return Token("SPACE", " ")


def is_command(command_name):
    class IsCommandImpl(Interpreter):
        def command_element(self, tree):
            _, command_invocation, *_ = tree.children
            return self.visit(command_invocation)

        def command_invocation(self, tree):
            identifier, *_ = tree.children
            return self.visit(identifier)

        def identifier(self, tree):
            name, *_ = tree.children
            return name == command_name

        def __default__(self, tree):
            return False

    return lambda node: isinstance(node, Tree) and IsCommandImpl().visit(node)


class IsolateSingleBlockType(Transformer_InPlace):
    def __init__(self, begin_name, end_name):
        super().__init__()
        self.begin_name = begin_name
        self.end_name = end_name
        self.is_block_begin = is_command(begin_name)
        self.is_block_end = is_command(end_name)

    def unbalanced_end_message(self):
        return "Unbalanced {}(), missing opening {}() command".format(
            self.end_name, self.begin_name
        )

    def _restructure(self, node_stream, begin=None):
        children = []
        for node in node_stream:
            if self.is_block_begin(node):
                children.append(self._restructure(node_stream, begin=node))
            elif self.is_block_end(node):
                if begin is None:
                    raise RuntimeError(self.unbalanced_end_message())
                return Tree(
                    "block",
                    [
                        Tree("block_begin", [begin]),
                        Tree("block_body", children),
                        Tree("block_end", [node]),
                    ],
                )
            else:
                children.append(node)
        return children

    def restructure(self, children):
        children_as_stream = (child for child in children)
        return self._restructure(children_as_stream)

    def file(self, children):
        return Tree("file", self.restructure(children))

    def block_body(self, children):
        return Tree("block_body", self.restructure(children))


class RestructureIfBlock(Transformer_InPlace):
    def __init__(self):
        super().__init__()

    def is_alternative_clause(self, node):
        is_elseif = is_command("elseif")
        is_else = is_command("else")
        return is_elseif(node) or is_else(node)

    def _restructure(self, node_stream):
        children = []
        for node in node_stream:
            if self.is_alternative_clause(node):
                return [
                    Tree("block_body", children),
                    Tree("alternative_clause", [node]),
                    *self._restructure(node_stream),
                ]
            children.append(node)
        return [Tree("block_body", children)]

    def restructure(self, block_body):
        children_as_stream = (child for child in block_body.children)
        return self._restructure(children_as_stream)

    def block(self, children):
        if_, body, endif_ = children
        return Tree("block", [if_, *self.restructure(body), endif_,])


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

    def _merge(self, last_comment, new_comment):
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


class RemoveSuperfluousEmptyLines(Transformer_InPlace):
    def _filter_superfluous_empty_lines(self, children):
        consecutive_newlines = 0
        for child in children:
            if is_newline(child):
                if consecutive_newlines >= 2:
                    continue
                consecutive_newlines += 1
            else:
                consecutive_newlines = 0
            yield child

    def _remove_edge_empty_lines(self, children):
        if is_newline(children[0]) and is_newline(children[1]):
            children.pop(0)
        if is_newline(children[-1]) and is_newline(children[-2]):
            children.pop()
        return children

    def _remove_superfluous_empty_lines(self, children):
        return self._remove_edge_empty_lines(
            list(self._filter_superfluous_empty_lines(children))
        )

    def file(self, children):
        return Tree("file", self._remove_superfluous_empty_lines(children))

    def block_body(self, children):
        return Tree("block_body", self._remove_superfluous_empty_lines(children))


def PostProcessor(code):
    return TransformerChain(
        MergeConsecutiveLineComments(code),
        IsolateSingleBlockType("if", "endif"),
        RestructureIfBlock(),
        IsolateSingleBlockType("foreach", "endforeach"),
        IsolateSingleBlockType("function", "endfunction"),
        IsolateSingleBlockType("macro", "endmacro"),
        IsolateSingleBlockType("while", "endwhile"),
        RemoveNodesToDiscard(),
        RemoveSuperfluousSpaces(),
        RemoveSuperfluousEmptyLines(),
        ReduceSpacesToOneCharacter(visit_tokens=True),
    )
