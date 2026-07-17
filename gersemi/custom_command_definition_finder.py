import yaml
from gersemi.keyword_kind import KeywordFormatter, KeywordPreprocessor
from gersemi.keywords import Hint


def get_keyword_transformers(raw_hints):
    hints = {}
    for raw_hint in raw_hints:
        hints.update(yaml.safe_load(raw_hint) or {})

    hints = tuple(Hint(keyword, kind) for keyword, kind in hints.items())

    return (
        {
            hint.keyword: hint.kind
            for hint in hints
            if hint.kind in [e.value for e in KeywordFormatter]
        },
        {
            hint.keyword: hint.kind
            for hint in hints
            if hint.kind in [e.value for e in KeywordPreprocessor]
        },
    )
