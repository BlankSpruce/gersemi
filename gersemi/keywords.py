from dataclasses import dataclass
from typing import Tuple, Union


@dataclass
class Hint:
    keyword: str
    kind: str


class AnyMatcher:
    def __eq__(self, other):
        return True

    def __hash__(self):
        return hash(str(self))


KeywordMatcher = Union[str, Tuple[str, Union[str, AnyMatcher]]]


@dataclass
class Keywords:
    options: Tuple[str, ...] = tuple()
    one_value_keywords: Tuple[KeywordMatcher, ...] = tuple()
    multi_value_keywords: Tuple[KeywordMatcher, ...] = tuple()
    hints: Tuple[Hint, ...] = tuple()
