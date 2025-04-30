import re
import pytest
from gersemi.extensions import verify, VerificationFailure
from gersemi.extension_type import ModuleExtension


defs = "gersemi_foo:command_definitions"
ab = f"{defs}['ab']"
ab_sections = f"{ab}['sections']"
ab_signatures = f"{ab}['signatures']"


@pytest.mark.parametrize(
    "definition",
    [
        dict(),
        {"ab": {}},
        {"ab": {"options": set()}},
        {"ab": {"options": tuple()}},
        {"ab": {"options": []}},
        {"ab": {"options": ("ONE", "TWO", "THREE")}},
        {"ab": {"unsupported_entry": {}, "foobar": {}}},
        {"ab": {"unsupported_entry": {}, "options": [], "foobar": {}}},
        {"ab": {"signatures": {"OK": {}}}},
        {"ab": {"signatures": {"OK": {"multi_value_keywords": "VALUES"}}}},
    ],
)
def test_extension_passes_verification(definition):
    try:
        verify(ModuleExtension("foo"), definition)
    except VerificationFailure as e:
        pytest.fail(f"{repr(definition)} should pass verification but doesn't: {e}")


@pytest.mark.parametrize(
    ["definition", "outcome"],
    [
        (tuple(), f"{defs}: is not a mapping"),
        ({12: 34}, f"{defs}: command name (12) has to be a string"),
        (
            {"": 34},
            f"{defs}: command name ('') has to start with a letter or underscore",
        ),
        (
            {"12": 34},
            f"{defs}: command name ('12') has to start with a letter or underscore",
        ),
        ({"ab": 34}, f"{defs}['ab']: is not a mapping"),
        (
            {"ab": {"options": {1: 2}}},
            f"{ab}['options']: keyword (1) has to be a string",
        ),
        (
            {"ab": {"options": ("ONE", 2, "THREE")}},
            f"{ab}['options']: keyword (2) has to be a string",
        ),
        (
            {"ab": {"options": ("ONE", "22", "THREE")}},
            f"{ab}['options']: keyword ('22') has to start with a letter or underscore",
        ),
        (
            {"ab": {"one_value_keywords": ("ONE", "234", "THREE")}},
            f"{ab}['one_value_keywords']: keyword ('234') has to start with a letter or underscore",
        ),
        (
            {"ab": {"front_positional_arguments": 34}},
            f"{ab}['front_positional_arguments']: is not a collection of strings (34)",
        ),
        (
            {"ab": {"front_positional_arguments": [34]}},
            f"{ab}['front_positional_arguments'][0]: argument (34) has to be a string",
        ),
        (
            {"ab": {"front_positional_arguments": ["abc", "", 34]}},
            f"{ab}['front_positional_arguments'][2]: argument (34) has to be a string",
        ),
        (
            {"ab": {"sections": tuple()}},
            f"{ab_sections}: is not a mapping",
        ),
        (
            {"ab": {"sections": {12: 34}}},
            f"{ab_sections}: keyword (12) has to be a string",
        ),
        (
            {"ab": {"sections": {"12": 34}}},
            f"{ab_sections}: keyword ('12') has to start with a letter or underscore",
        ),
        (
            {"ab": {"sections": {"ABC": 34}}},
            f"{ab_sections}['ABC']: is not a mapping",
        ),
        (
            {"ab": {"sections": {"ABC": {"sections": tuple()}}}},
            f"{ab_sections}['ABC']['sections']: is not a mapping",
        ),
        ({"ab": {"signatures": tuple()}}, f"{ab_signatures}: is not a mapping"),
        (
            {"ab": {"signatures": {12: 34}}},
            f"{ab_signatures}: signature (12) has to be a string",
        ),
        (
            {"ab": {"signatures": {"12": 34}}},
            f"{ab_signatures}: signature ('12') has to start with a letter or underscore",
        ),
        (
            {"ab": {"signatures": {"CD": 34}}},
            f"{ab_signatures}['CD']: is not a mapping",
        ),
    ],
)
def test_extension_fails_verification(definition, outcome):
    with pytest.raises(VerificationFailure, match=re.escape(outcome)):
        verify(ModuleExtension("foo"), definition)
