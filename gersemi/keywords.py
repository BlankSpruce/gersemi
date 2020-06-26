from dataclasses import dataclass
from typing import Tuple


@dataclass
class Keywords:
    options: Tuple[str]
    one_value_keywords: Tuple[str]
    multi_value_keywords: Tuple[str]
