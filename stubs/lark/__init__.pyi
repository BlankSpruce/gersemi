from typing import Any, List, Optional, Union
from lark.tree import Meta
from gersemi.types import Nodes

Discard: Exception

class Token(str):
    type: str
    column: int
    line: int
    end_column: int
    def __init__(
        self,
        type_: str,
        value: str,
        line: int = ...,
        column: int = ...,
        end_line: int = ...,
        end_column: int = ...,
    ): ...

class Tree:
    children: Nodes
    column: int
    data: str
    meta: Meta
    def __init__(self, name: str, children: Nodes, meta: Optional[Meta] = ...): ...

class Lark: ...
