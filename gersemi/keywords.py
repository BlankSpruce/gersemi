from dataclasses import dataclass
from typing import Tuple


@dataclass
class Hint:
    keyword: str
    kind: str


@dataclass
class Keywords:
    options: Tuple[str, ...] = tuple()
    one_value_keywords: Tuple[str, ...] = tuple()
    multi_value_keywords: Tuple[str, ...] = tuple()
    hints: Tuple[Hint, ...] = tuple()
