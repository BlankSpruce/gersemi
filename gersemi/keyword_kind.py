from enum import Enum
from typing import Optional, Union


class KeywordFormatter(Enum):
    CommandLine = "command_line"
    Pairs = "pairs"


class KeywordPreprocessor(Enum):
    Sort = "sort"
    Unique = "unique"
    SortAndUnique = "sort+unique"


KeywordKind = Union[KeywordFormatter, KeywordPreprocessor]


def get_formatter_kind(
    kind: Union[None, str, KeywordFormatter],
) -> Optional[KeywordFormatter]:
    if isinstance(kind, KeywordFormatter):
        return kind

    return (
        KeywordFormatter(kind) if kind in [e.value for e in KeywordFormatter] else None
    )


def kind_to_formatter(kind: Union[None, str, KeywordFormatter]) -> Optional[str]:
    proper_kind = get_formatter_kind(kind)
    if proper_kind is None:
        return None

    return {
        KeywordFormatter.CommandLine: "_format_command_line",
        KeywordFormatter.Pairs: "_format_keyword_with_pairs",
    }.get(proper_kind, None)


def get_preprocessor_kind(
    kind: Union[None, str, KeywordPreprocessor],
) -> Optional[KeywordPreprocessor]:
    if isinstance(kind, KeywordPreprocessor):
        return kind

    return (
        KeywordPreprocessor(kind)
        if kind in [e.value for e in KeywordPreprocessor]
        else None
    )


def kind_to_preprocessor(kind: Union[None, str, KeywordPreprocessor]) -> Optional[str]:
    proper_kind = get_preprocessor_kind(kind)
    if proper_kind is None:
        return None

    return {
        KeywordPreprocessor.Sort: "_sort_arguments",
        KeywordPreprocessor.Unique: "_keep_unique_arguments",
        KeywordPreprocessor.SortAndUnique: "_sort_and_keep_unique_arguments",
    }.get(proper_kind, None)
