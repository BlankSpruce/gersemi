from itertools import dropwhile
from typing import Callable, Iterator, Optional
from lark import Discard, Tree, Token
from lark.tree import Meta
from lark.visitors import (
    Transformer,
    TransformerChain,
    Transformer_InPlace,
    Interpreter,
    v_args,
)
from gersemi.ast_helpers import is_newline, is_argument, is_comment
from gersemi.types import Node, Nodes
from gersemi.utils import pop_all


def is_command(command_name: str) -> Callable[[Node], bool]:
    class IsCommandImpl(Interpreter):
        def command_element(self, tree):
            command_invocation, *_ = tree.children
            return self.visit(command_invocation)

        def command_invocation(self, tree):
            name, *_ = tree.children
            return name.lower() == command_name

        def __default__(self, tree):
            return False

    return lambda node: isinstance(node, Tree) and IsCommandImpl().visit(node)


class IsolateSingleBlockType(Transformer_InPlace):
    is_block_begin = staticmethod(lambda _: False)
    is_block_end = staticmethod(lambda _: False)
    error_message = ""

    def _create_block_node(self, begin, body, end):
        return Tree(
            "block",
            [
                Tree("block_begin", [begin]),
                Tree("block_body", body),
                Tree("block_end", [end]),
            ],
        )

    def _build_block(self, node_stream: Iterator[Node], begin: Node) -> Tree:
        children: Nodes = []
        for node in node_stream:
            if self.is_block_begin(node):
                children.append(self._build_block(node_stream, node))
            elif self.is_block_end(node):
                return self._create_block_node(begin, children, node)
            else:
                children.append(node)
        raise RuntimeError(self.error_message)

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
        return Tree("block", [if_, *self.restructure(body), endif_])


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


class RestructureBracketTypeRules(Transformer_InPlace):
    def _split_bracket_argument(self, arg):
        bracket_length = arg.index("[", 1) + 1
        return (
            arg[:bracket_length],
            arg[bracket_length:-bracket_length],
            arg[-bracket_length:],
        )

    def bracket_argument(self, children):
        token, *_ = children
        bracket_open, content, bracket_close = self._split_bracket_argument(token)
        return Tree(
            "bracket_argument",
            [
                Token("bracket_argument_begin", bracket_open),
                Token("bracket_argument_body", content),
                Token("bracket_argument_end", bracket_close),
            ],
        )

    def bracket_comment(self, children) -> Tree:
        *_, bracket_argument = children
        bracket_open, content, bracket_close = bracket_argument.children
        return Tree(
            "bracket_comment",
            [
                Token("bracket_comment_begin", f"#{bracket_open}"),
                Token("bracket_comment_body", content),
                Token("bracket_comment_end", bracket_close),
            ],
        )


class SimplifyParseTree(Transformer_InPlace):
    def command_element(self, children) -> Tree:
        command_invocation, *rest = children
        if len(rest) == 0:
            return command_invocation
        return Tree("command_element", children)

    @v_args(meta=True)
    def non_command_element(self, children: Nodes, meta: Meta) -> Tree:
        if len(children) == 0:
            raise Discard
        return Tree("non_command_element", children, meta)

    def arguments(self, children: Nodes) -> Tree:
        return Tree("arguments", [child for child in children if not is_newline(child)])

    def argument(self, children: Nodes) -> Node:
        return children[0]

    def unquoted_argument(self, children) -> Tree:
        return Tree(
            "unquoted_argument", [Token("unquoted_argument_content", "".join(children))]
        )


class IsolateIfBlock(IsolateSingleBlockType):
    is_block_begin = staticmethod(is_command("if"))
    is_block_end = staticmethod(is_command("endif"))
    error_message = "Unbalanced if(), missing ending endif() command"


class IsolateForeachBlock(IsolateSingleBlockType):
    is_block_begin = staticmethod(is_command("foreach"))
    is_block_end = staticmethod(is_command("endforeach"))
    error_message = "Unbalanced foreach(), missing ending endforeach() command"


class IsolateFunctionBlock(IsolateSingleBlockType):
    is_block_begin = staticmethod(is_command("function"))
    is_block_end = staticmethod(is_command("endfunction"))
    error_message = "Unbalanced function(), missing ending endfunction() command"


class IsolateMacroBlock(IsolateSingleBlockType):
    is_block_begin = staticmethod(is_command("macro"))
    is_block_end = staticmethod(is_command("endmacro"))
    error_message = "Unbalanced macro(), missing ending endmacro() command"


class IsolateWhileBlock(IsolateSingleBlockType):
    is_block_begin = staticmethod(is_command("while"))
    is_block_end = staticmethod(is_command("endwhile"))
    error_message = "Unbalanced while(), missing ending endwhile() command"


def has_line_comment_with_given_content(node, expected_content):
    class Impl(Interpreter):
        def __default__(self, tree):
            return False

        def non_command_element(self, tree):
            return any(self.visit_children(tree))

        def line_comment(self, tree):
            if len(tree.children) == 0:
                return False
            return tree.children[0].strip() == expected_content

    return isinstance(node, Tree) and Impl().visit(node)


class IsolateDisabledFormattingBlock(IsolateSingleBlockType):
    error_message = "Unbalanced # gersemi: off, missing ending # gersemi: on comment"

    def __init__(self, code):
        super().__init__()
        self.lines_of_code = code.splitlines()

    def _create_block_node(self, begin, _, end):
        range_start, range_end = begin.meta.line, end.meta.line - 1
        return Tree(
            "disabled_formatting",
            [
                begin,
                Tree(
                    "disabled_formatting_body",
                    self.lines_of_code[range_start:range_end],
                ),
                end,
            ],
        )

    @staticmethod
    def is_block_begin(node):
        return has_line_comment_with_given_content(node, "gersemi: off")

    @staticmethod
    def is_block_end(node):
        return has_line_comment_with_given_content(node, "gersemi: on")


def PostProcessor(
    code: str, line_comment_reflower: Optional[Transformer] = None,
) -> Transformer:
    chain = TransformerChain(
        RestructureBracketTypeRules(),
        IsolateCommentedArguments(),
        SimplifyParseTree(),
        IsolateIfBlock(),
        RestructureIfBlock(),
        IsolateForeachBlock(),
        IsolateFunctionBlock(),
        IsolateMacroBlock(),
        IsolateWhileBlock(),
        IsolateDisabledFormattingBlock(code),
        RemoveSuperfluousEmptyLines(),
    )
    if line_comment_reflower is not None:
        return line_comment_reflower * chain
    return chain
