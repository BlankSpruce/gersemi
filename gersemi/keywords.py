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
    options: Tuple[str, ...] = ()
    one_value_keywords: Tuple[KeywordMatcher, ...] = ()
    multi_value_keywords: Tuple[KeywordMatcher, ...] = ()
    hints: Tuple[Hint, ...] = ()
