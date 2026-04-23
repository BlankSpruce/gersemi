from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Optional, Sequence
from gersemi.keyword_kind import KeywordFormatter, KeywordPreprocessor
from gersemi.keywords import KeywordMatcher

Sections = Mapping[KeywordMatcher, "ArgumentSchema"]
Signatures = Mapping[Optional[KeywordMatcher], "ArgumentSchema"]


@dataclass
class ArgumentSchema:  # pylint: disable=too-many-instance-attributes
    front_positional_arguments: Sequence[str] = ()
    back_positional_arguments: Sequence[str] = ()
    options: Iterable[KeywordMatcher] = ()
    one_value_keywords: Iterable[KeywordMatcher] = ()
    multi_value_keywords: Iterable[KeywordMatcher] = ()
    sections: Sections = field(default_factory=dict)
    keyword_formatters: Mapping[str, KeywordFormatter] = field(default_factory=dict)
    keyword_preprocessors: Mapping[str, KeywordPreprocessor] = field(
        default_factory=dict
    )


def argument_schemas_from_dict(schemas: Mapping) -> Mapping[Any, ArgumentSchema]:
    return {
        key: ArgumentSchema(
            front_positional_arguments=schema.get("front_positional_arguments", ()),
            back_positional_arguments=schema.get("back_positional_arguments", ()),
            options=schema.get("options", ()),
            one_value_keywords=schema.get("one_value_keywords", ()),
            multi_value_keywords=schema.get("multi_value_keywords", ()),
            sections=argument_schemas_from_dict(schema.get("sections", {})),
            keyword_formatters=schema.get("keyword_formatters", {}),
            keyword_preprocessors=schema.get("keyword_preprocessors", {}),
        )
        for key, schema in schemas.items()
    }


def create_schema_patch(schema, old_class):
    class Impl(old_class):
        front_positional_arguments = schema.front_positional_arguments
        back_positional_arguments = schema.back_positional_arguments
        options = schema.options
        one_value_keywords = schema.one_value_keywords
        multi_value_keywords = schema.multi_value_keywords
        sections = schema.sections
        keyword_formatters = schema.keyword_formatters
        keyword_preprocessors = schema.keyword_preprocessors

    return Impl
