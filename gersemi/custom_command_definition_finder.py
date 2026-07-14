import yaml
from gersemi.argument_schema import Command, StandardCommand, argument_schema_from_dict
from gersemi.immutable import make_immutable
from gersemi.keyword_kind import KeywordFormatter, KeywordPreprocessor
from gersemi.keywords import Hint, Keywords


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
    return Command(
        canonical_name=canonical_name,
        block_end=block_end,
        details=StandardCommand(
            schema=argument_schema_from_dict(schema),
        ),
    )


def get_just_definitions(definitions):
    result = {}
    for name, info in definitions:
        sorted_info = sorted(info, key=lambda item: item[1])
        content, _ = sorted_info[0]
        result[name] = create_command(**content)
    return make_immutable(result)
