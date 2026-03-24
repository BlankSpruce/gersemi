from dataclasses import dataclass
from typing import List, Union
import lark


@dataclass
class Tree:
    data: str
    children: list

    def __hash__(self):
        return hash((self.data, tuple(self.children)))


Token = lark.Token


Node = Union[Token, Tree]
Nodes = List[Node]
