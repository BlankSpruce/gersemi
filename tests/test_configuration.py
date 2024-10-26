# mypy: disable-error-code="no-redef"
from dataclasses import asdict
import json
import os
import pytest
from gersemi.configuration import (
    OutcomeConfiguration,
    ListExpansion,
    make_configuration_file,
    Tabs,
)

try:
    from pydantic.json_schema import GenerateJsonSchema
    from pydantic.version import version_short
    from pydantic import TypeAdapter
except ImportError:

    class GenerateJsonSchema:
        pass

    class TypeAdapter:
        pass

    def version_short() -> str:
        return "0.0"


def pydantic_version_as_tuple():
    return tuple(map(int, version_short().split(".")))


def get_representation(represented_type):
    return {
        "oneOf": [
            {
                "description": item.description,
                "enum": [item.value],
                "title": item.title,
            }
            for item in represented_type
        ],
        "type": "string",
    }


class CustomizedGenerateJsonSchema(GenerateJsonSchema):
    def generate(self, schema, mode=None):
        result = super().generate(schema, mode=mode)
        result["$schema"] = "https://json-schema.org/draft-07/schema"
        result["$defs"]["ListExpansion"] = get_representation(ListExpansion)
        result["$defs"]["Tabs"] = get_representation(Tabs)

        result["properties"]["indent"]["anyOf"][0]["minimum"] = 1

        return result


@pytest.mark.skipif(
    pydantic_version_as_tuple() < (2, 9), reason="At least pydantic 2.9 is required"
)
def test_schema_in_repository_is_consistent_with_configuration_definition():
    this_file_dir = os.path.dirname(os.path.realpath(__file__))
    schema_path = os.path.join(this_file_dir, "configuration.schema.json")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    assert schema == TypeAdapter(OutcomeConfiguration).json_schema(
        schema_generator=CustomizedGenerateJsonSchema,
    )


def test_example_file_in_repository_is_consistent_with_configuration_definition():
    this_file_dir = os.path.dirname(os.path.realpath(__file__))
    example_path = os.path.join(this_file_dir, ".gersemirc.example")
    with open(example_path, "r", encoding="utf-8") as f:
        example = f.read()

    configuration = OutcomeConfiguration()
    assert example == make_configuration_file(
        asdict(configuration), add_schema_link=True
    )
