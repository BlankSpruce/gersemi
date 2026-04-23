from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Optional, Sequence
from gersemi.immutable import ImmutableDict, make_immutable
from gersemi.keyword_kind import KeywordFormatter, KeywordPreprocessor
from gersemi.keywords import KeywordMatcher, TwoWordKeywordMatcher

Sections = Mapping[KeywordMatcher, "ArgumentSchema"]
Signatures = Mapping[Optional[KeywordMatcher], "ArgumentSchema"]


@dataclass(eq=True, frozen=True)
class ArgumentSchema:  # pylint: disable=too-many-instance-attributes
    front_positional_arguments: Sequence[str] = ()
    back_positional_arguments: Sequence[str] = ()
    options: Iterable[KeywordMatcher] = ()
    one_value_keywords: Iterable[KeywordMatcher] = ()
    multi_value_keywords: Iterable[KeywordMatcher] = ()
    sections: Sections = ImmutableDict()
    keyword_formatters: Mapping[str, KeywordFormatter] = ImmutableDict()
    keyword_preprocessors: Mapping[str, KeywordPreprocessor] = ImmutableDict()


def argument_schema_from_dict(schema: Mapping) -> ArgumentSchema:
    return ArgumentSchema(
        front_positional_arguments=tuple(schema.get("front_positional_arguments", ())),
        back_positional_arguments=tuple(schema.get("back_positional_arguments", ())),
        options=tuple(schema.get("options", ())),
        one_value_keywords=tuple(schema.get("one_value_keywords", ())),
        multi_value_keywords=tuple(schema.get("multi_value_keywords", ())),
        sections=argument_schemas_from_dict(schema.get("sections", {})),
        keyword_formatters=make_immutable(schema.get("keyword_formatters", {})),
        keyword_preprocessors=make_immutable(schema.get("keyword_preprocessors", {})),
    )


def argument_schemas_from_dict(schemas: Mapping) -> Mapping[Any, ArgumentSchema]:
    return make_immutable(
        {key: argument_schema_from_dict(schema) for key, schema in schemas.items()}
    )


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


@dataclass(eq=True, frozen=True)
class StandardCommand:
    schema: ArgumentSchema
    signatures: Signatures = ImmutableDict()
    block_end: Optional[str] = None
    canonical_name: Optional[str] = None
    inhibit_favour_expansion: bool = False
    two_words_keywords: Iterable[TwoWordKeywordMatcher] = ()


@dataclass(eq=True, frozen=True)
class SpecializedCommand:
    impl: object
    canonical_name: Optional[str] = None
