# type: ignore
from gersemi.builtin_commands import builtin_commands

target_compile_definitions = builtin_commands["target_compile_definitions"]
target_compile_definitions["keyword_kinds"] = {
    "INTERFACE": "sort",
    "PRIVATE": "sort",
    "PUBLIC": "sort",
}

command_definitions = {
    "target_compile_definitions": target_compile_definitions,
}
