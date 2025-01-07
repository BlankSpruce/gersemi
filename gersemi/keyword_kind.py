from enum import Enum
from typing import Optional, Union


class KeywordKind(Enum):
    CommandLine = "command_line"
    Pairs = "pairs"


def get_kind(kind: Union[None, str, KeywordKind]) -> Optional[KeywordKind]:
    if isinstance(kind, KeywordKind):
        return kind

    return KeywordKind(kind) if kind in [e.value for e in KeywordKind] else None


def kind_to_formatter(kind: KeywordKind) -> Optional[str]:
    proper_kind = get_kind(kind)
    return {
        KeywordKind.CommandLine: "_format_command_line",
        KeywordKind.Pairs: "_format_keyword_with_pairs",
    }.get(proper_kind, None)
