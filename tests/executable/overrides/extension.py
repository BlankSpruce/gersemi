# type: ignore
from gersemi.builtin_commands import builtin_commands

target_compile_definitions = builtin_commands["target_compile_definitions"]
target_compile_definitions["keyword_kinds"] = {
    "INTERFACE": "sort",
    "PRIVATE": "sort",
    "PUBLIC": "sort",
}

target_link_libraries = builtin_commands["target_link_libraries"]
target_link_libraries["keyword_kinds"] = {
    "INTERFACE": "sort",
    "PRIVATE": "sort",
    "PUBLIC": "sort",
}

target_sources = builtin_commands["target_sources"]
target_sources["keyword_kinds"] = {
    key: "sort"
    for key in ["INTERFACE", "PRIVATE", "PUBLIC", "TYPE", "BASE_DIRS", "FILES"]
}

command_definitions = {
    "target_compile_definitions": target_compile_definitions,
    "target_link_libraries": target_link_libraries,
    "target_sources": target_sources,
}
