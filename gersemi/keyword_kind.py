from enum import Enum
from typing import Union


class KeywordFormatter(Enum):
    CommandLine = "command_line"
    Pairs = "pairs"


class KeywordPreprocessor(Enum):
    Sort = "sort"
    Unique = "unique"
    SortAndUnique = "sort+unique"


KeywordKind = Union[KeywordFormatter, KeywordPreprocessor]
