from dataclasses import dataclass
from typing import List, Optional, Union


@dataclass
class Tree:
    data: str
    children: list

    def __hash__(self):
        return hash((self.data, tuple(self.children)))


@dataclass
class Token:
    type: str
    value: str
    line: Optional[int] = None
    column: Optional[int] = None
    start_pos: Optional[int] = None
    end_pos: Optional[int] = None

    def __eq__(self, other):
        if isinstance(other, Token):
            return self.type == other.type and self.value == other.value

        return self.value == other

    def __str__(self):
        return self.value

    def __hash__(self):
        return hash(self.value)

    def __iter__(self):
        return iter(self.value)

    def __deepcopy__(self, _memo):
        return Token(
            self.type, self.value, self.line, self.column, self.start_pos, self.end_pos
        )

    def __getattr__(self, attr):
        return getattr(self.value, attr)


Node = Union[Token, Tree]
Nodes = List[Node]
