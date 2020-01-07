from itertools import dropwhile, filterfalse
import re
from lark import Discard, Tree, Token
from lark.visitors import TransformerChain, Transformer_InPlace, Interpreter, v_args
from gersemi.ast_helpers import is_space, is_newline, is_argument, is_comment


def remove_if_space(children, index):
    if len(children) > 0 and is_space(children[index]):
        children.pop(index)


def is_space_at_line_beginning(element):
    return is_space(element) and element.column == 1


class RemoveSuperfluousSpaces(Transformer_InPlace):
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

    def _drop_edge_empty_lines(self, children):
        while is_newline(children[-1]):
            children.pop()
        return dropwhile(is_newline, children)

    def _make_node(self, node_type, children):
        new_children = self._filter_superfluous_empty_lines(
            self._drop_edge_empty_lines(children)
        )
        return Tree(node_type, list(new_children))

    def file(self, children):
        return self._make_node("file", children)

    def block_body(self, children):
        return self._make_node("block_body", children)


def pop_all(in_list):
    popped, in_list[:] = in_list[:], []
    return popped


class IsolateCommentedArguments(Transformer_InPlace):
    def arguments(self, children):
        new_children = []
        accumulator = []
        for child in children:
            if is_argument(child):
                new_children += pop_all(accumulator)

            accumulator += [child]
            if is_comment(child) and is_argument(accumulator[0]):
                new_children += [Tree("commented_argument", pop_all(accumulator))]
            if is_newline(child):
                new_children += pop_all(accumulator)
        new_children += accumulator
        return Tree("arguments", new_children)


class RestructureBracketArgument(Transformer_InPlace):
    def __init__(self, pattern):
        super().__init__()
        self.pattern = pattern

    def bracket_argument(self, children):
        token, *_ = children
        equal_signs, _, content = re.match(self.pattern, token).groups()
        return Tree(
            "bracket_argument",
            [
                Tree("bracket_argument_begin", ["[{}[".format(equal_signs)]),
                Tree("bracket_argument_body", [content]),
                Tree("bracket_argument_end", ["]{}]".format(equal_signs)]),
            ],
        )


class RestructureBracketComment(Transformer_InPlace):
    def bracket_comment(self, children):
        pound_sign, bracket_argument = children
        begin, body, end = bracket_argument.children
        return Tree(
            "bracket_comment",
            [
                Tree("bracket_comment_begin", [pound_sign + begin.children[0]]),
                Tree("bracket_comment_body", body.children),
                Tree("bracket_comment_end", end.children),
            ],
        )


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


class RemoveSuperfluousEmptyComments(Transformer_InPlace):
    def line_comment(self, children):
        _, content = children
        if content == "":
            raise Discard()
        return Tree("line_comment", children)


def PostProcessor(code, terminal_patterns):
    return TransformerChain(
        NormalizeEmptyLineComments(),
        MergeConsecutiveLineComments(code),
        IsolateSingleBlockType("if", "endif"),
        RestructureIfBlock(),
        IsolateSingleBlockType("foreach", "endforeach"),
        IsolateSingleBlockType("function", "endfunction"),
        IsolateSingleBlockType("macro", "endmacro"),
        IsolateSingleBlockType("while", "endwhile"),
        IsolateCommentedArguments(),
        RestructureBracketArgument(terminal_patterns["BRACKET_ARGUMENT"]),
        RestructureBracketComment(),
        RemoveNodesToDiscard(),
        RemoveSuperfluousEmptyComments(),
        RemoveSuperfluousSpaces(),
        RemoveSuperfluousEmptyLines(),
        ReduceSpacesToOneCharacter(visit_tokens=True),
    )
