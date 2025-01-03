import json
import os


settings = json.loads(os.environ["GERSEMI_FAKE_EXTENSION_SETTINGS"])


class Frombulate:
    pass


def get_implementation(implementation):
    if implementation == "add_constellation":
        return {
            "one_value_keywords": ["TRUE_NAME"],
            "multi_value_keywords": ["MODIFIERS"],
        }

    if implementation == "add_nebula":
        return {"one_value_keywords": ["NAME"]}

    return {}


def command_definitions_impl():
    if settings.get("implementation_passes_validation", False):
        return {
            implementation: get_implementation(implementation)
            for implementation in settings.get("implementations", [])
        }
    else:
        return Frombulate()


if settings.get("implementation_present", False):
    command_definitions = command_definitions_impl()
