from itertools import dropwhile, filterfalse
import re
from typing import Callable, Dict, Iterator, List, Optional
from lark import Discard, Tree, Token
from lark.visitors import (
    Transformer,
    TransformerChain,
    Transformer_InPlace,
    Interpreter,
)
from gersemi.ast_helpers import is_space, is_newline, is_argument, is_comment
from gersemi.types import Node, Nodes


def remove_if_space(children: Nodes, index) -> None:
    if len(children) > 0 and is_space(children[index]):
        children.pop(index)


def is_space_at_line_beginning(element: Node) -> bool:
    return is_space(element) and element.column == 1


class RemoveSuperfluousSpaces(Transformer_InPlace):
    def command_element(self, children) -> Tree:
        _, command_invocation, trailing_space, *rest = children
        if len(rest) == 0:
            return command_invocation
        return Tree("command_element", [command_invocation, trailing_space, *rest])

    def non_command_element(self, children: Nodes) -> Tree:
        remove_if_space(children, index=0)
        if len(children) == 0:
            raise Discard
        return Tree("non_command_element", children)

    def command_invocation(self, children: Nodes) -> Tree:
        remove_if_space(children, index=1)
        return Tree("command_invocation", children)

    def arguments(self, children: Nodes) -> Tree:
        remove_if_space(children, index=0)
        remove_if_space(children, index=-1)
        children = [*filterfalse(is_space_at_line_beginning, children)]

        return Tree("arguments", children)


def is_command(command_name: str) -> Callable[[Node], bool]:
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
    def __init__(self, begin_name: str, end_name: str):
        super().__init__()
        self.begin_name = begin_name
        self.end_name = end_name
        self.is_block_begin = is_command(begin_name)
        self.is_block_end = is_command(end_name)

    def unbalanced_end_message(self) -> str:
        return "Unbalanced {}(), missing ending {}() command".format(
            self.begin_name, self.end_name
        )

    def _build_block(self, node_stream: Iterator[Node], begin: Node) -> Tree:
        children: Nodes = []
        for node in node_stream:
            if self.is_block_begin(node):
                children.append(self._build_block(node_stream, node))
            elif self.is_block_end(node):
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
        raise RuntimeError(self.unbalanced_end_message())

    def _restructure(self, children: Nodes) -> Nodes:
        children_as_stream = (child for child in children)
        new_children: Nodes = []
        for node in children_as_stream:
            if self.is_block_begin(node):
                new_children.append(self._build_block(children_as_stream, begin=node))
            else:
                new_children.append(node)
        return new_children

    def file(self, children: Nodes) -> Tree:
        return Tree("file", self._restructure(children))

    def block_body(self, children: Nodes) -> Tree:
        return Tree("block_body", self._restructure(children))


class RestructureIfBlock(Transformer_InPlace):
    def __init__(self):
        super().__init__()

    def is_alternative_clause(self, node: Node) -> bool:
        is_elseif = is_command("elseif")
        is_else = is_command("else")
        return is_elseif(node) or is_else(node)

    def _restructure(self, node_stream: Iterator) -> Nodes:
        children: Nodes = []
        for node in node_stream:
            if self.is_alternative_clause(node):
                return [
                    Tree("block_body", children),
                    Tree("alternative_clause", [node]),
                    *self._restructure(node_stream),
                ]
            children.append(node)
        return [Tree("block_body", children)]

    def restructure(self, block_body: Tree) -> Nodes:
        children_as_stream = (child for child in block_body.children)
        return self._restructure(children_as_stream)

    def block(self, children) -> Tree:
        if_, body, endif_ = children
        return Tree("block", [if_, *self.restructure(body), endif_,])


class RemoveSuperfluousEmptyLines(Transformer_InPlace):
    def _filter_superfluous_empty_lines(self, children) -> Iterator:
        consecutive_newlines = 0
        for child in children:
            if is_newline(child):
                if consecutive_newlines >= 2:
                    continue
                consecutive_newlines += 1
            else:
                consecutive_newlines = 0
            yield child

    def _drop_edge_empty_lines(self, children) -> Iterator:
        while len(children) > 0 and is_newline(children[-1]):
            children.pop()
        return dropwhile(is_newline, children)

    def _make_node(self, node_type, children) -> Tree:
        new_children = self._filter_superfluous_empty_lines(
            self._drop_edge_empty_lines(children)
        )
        return Tree(node_type, list(new_children))

    def file(self, children) -> Tree:
        return self._make_node("file", children)

    def block_body(self, children) -> Tree:
        return self._make_node("block_body", children)


def pop_all(in_list: List) -> List:
    popped, in_list[:] = in_list[:], []
    return popped


class IsolateCommentedArguments(Transformer_InPlace):
    def arguments(self, children) -> Tree:
        new_children: Nodes = []
        accumulator: Nodes = []
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
    def bracket_comment(self, children) -> Tree:
        *_, bracket_argument = children
        begin, body, end = bracket_argument.children
        return Tree(
            "bracket_comment",
            [
                Tree(
                    "bracket_comment_begin",
                    [Token("bracket_open", f"#{begin.children[0]}")],
                ),
                Tree("bracket_comment_body", body.children),
                Tree("bracket_comment_end", end.children),
            ],
        )


def PostProcessor(
    terminal_patterns: Dict[str, str],
    line_comment_reflower: Optional[Transformer] = None,
) -> Transformer:
    chain = TransformerChain(
        IsolateSingleBlockType("if", "endif"),
        RestructureIfBlock(),
        IsolateSingleBlockType("foreach", "endforeach"),
        IsolateSingleBlockType("function", "endfunction"),
        IsolateSingleBlockType("macro", "endmacro"),
        IsolateSingleBlockType("while", "endwhile"),
        IsolateCommentedArguments(),
        RestructureBracketArgument(terminal_patterns["BRACKET_ARGUMENT"]),
        RestructureBracketComment(),
        RemoveSuperfluousSpaces(),
        RemoveSuperfluousEmptyLines(),
    )
    if line_comment_reflower is not None:
        return line_comment_reflower * chain
    return chain
