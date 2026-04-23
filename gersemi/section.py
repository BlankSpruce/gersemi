from dataclasses import dataclass, field
from typing import Iterable, Mapping, Sequence
from gersemi.keyword_kind import KeywordFormatter, KeywordPreprocessor
from gersemi.keywords import KeywordMatcher

Sections = Mapping[KeywordMatcher, "Section"]


@dataclass
class Section:  # pylint: disable=too-many-instance-attributes
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


def section_from_dict(section):
    return Section(
        front_positional_arguments=section.get("front_positional_arguments", ()),
        back_positional_arguments=section.get("back_positional_arguments", ()),
        options=section.get("options", ()),
        one_value_keywords=section.get("one_value_keywords", ()),
        multi_value_keywords=section.get("multi_value_keywords", ()),
        sections=sections_from_dict(section.get("sections", {})),
        keyword_formatters=section.get("keyword_formatters", {}),
        keyword_preprocessors=section.get("keyword_preprocessors", {}),
    )


def sections_from_dict(sections: Mapping) -> Sections:
    return {key: section_from_dict(section) for key, section in sections.items()}
