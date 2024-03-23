# mypy: disable-error-code="no-redef"
import json
import os
import sys
import pytest
from gersemi.configuration import (
    Configuration,
    ListExpansion,
    make_configuration_file,
    Tabs,
)

try:
    from pydantic.json_schema import GenerateJsonSchema
    from pydantic import TypeAdapter
except ImportError:

    class GenerateJsonSchema:
        pass

    class TypeAdapter:
        pass


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

        del result["properties"]["workers"]["default"]
        result["properties"]["workers"]["minimum"] = 1

        return result


@pytest.mark.skipif(sys.version_info < (3, 7), reason="At least Python 3.7 is required")
def test_schema_in_repository_is_consistent_with_configuration_definition():
    this_file_dir = os.path.dirname(os.path.realpath(__file__))
    schema_path = os.path.join(this_file_dir, "configuration.schema.json")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    assert schema == TypeAdapter(Configuration).json_schema(
        schema_generator=CustomizedGenerateJsonSchema,
    )


def test_example_file_in_repository_is_consistent_with_configuration_definition():
    this_file_dir = os.path.dirname(os.path.realpath(__file__))
    example_path = os.path.join(this_file_dir, ".gersemirc.example")
    with open(example_path, "r", encoding="utf-8") as f:
        example = f.read().strip()

    configuration = Configuration()
    configuration.workers = 8
    assert example == make_configuration_file(configuration)
