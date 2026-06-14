import gersemi_rust_backend
import yaml
from gersemi.argument_schema import StandardCommand, argument_schema_from_dict
from gersemi.builtin_commands import _builtin_commands
from gersemi.immutable import make_immutable
from gersemi.keyword_kind import KeywordFormatter, KeywordPreprocessor
from gersemi.keywords import Hint, Keywords


def find_custom_command_definitions(code, filepath="---"):
    return gersemi_rust_backend.find_custom_command_definitions(
        code, dict(_builtin_commands), str(filepath)
    )


def create_command(canonical_name, positional_arguments, keywords, block_end):
    keywords = Keywords(**keywords)
    hints = {}
    for raw_hint in keywords.hints:
        hints.update(yaml.safe_load(raw_hint) or {})

    hints = tuple(Hint(keyword, kind) for keyword, kind in hints.items())

    schema = {
        "front_positional_arguments": positional_arguments,
        "options": keywords.options,
        "one_value_keywords": keywords.one_value_keywords,
        "multi_value_keywords": keywords.multi_value_keywords,
        "keyword_formatters": make_immutable(
            {
                hint.keyword: hint.kind
                for hint in hints
                if hint.kind in [e.value for e in KeywordFormatter]
            }
        ),
        "keyword_preprocessors": make_immutable(
            {
                hint.keyword: hint.kind
                for hint in hints
                if hint.kind in [e.value for e in KeywordPreprocessor]
            }
        ),
    }
    return StandardCommand(
        canonical_name=canonical_name,
        schema=argument_schema_from_dict(schema),
        block_end=block_end,
    )


def get_just_definitions(definitions):
    result = {}
    for name, info in definitions.items():
        sorted_info = sorted(info, key=lambda item: item[1])
        content, _ = sorted_info[0]
        result[name] = create_command(**content)
    return make_immutable(result)
