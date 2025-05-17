### {list_expansion: favour-expansion, definitions: [tests/formatter/custom_command_with_sort_and_unique_hint.in.cmake]}
function(my_custom_function target_name)
# gersemi: hints { SOURCES_JUST_SORTED: sort, SOURCES_JUST_UNIQUE: unique, SOURCES: sort+unique }
set(options "")
set(oneValueArgs KIND)
set(multiValueArgs SOURCES_JUST_SORTED SOURCES_JUST_UNIQUE SOURCES PROPERTIES)

cmake_parse_arguments(THIS_FUNCTION_PREFIX "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})
endfunction()

my_custom_function(
    example
    KIND foo
    SOURCES_JUST_SORTED c.cpp a.cpp c.cpp b.cpp a.cpp b.cpp c.cpp
    SOURCES_JUST_UNIQUE c.cpp a.cpp c.cpp b.cpp a.cpp b.cpp c.cpp
    SOURCES c.cpp a.cpp c.cpp b.cpp a.cpp b.cpp c.cpp
    PROPERTIES foo bar baz
)
