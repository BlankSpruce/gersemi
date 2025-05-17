### {list_expansion: favour-expansion, definitions: [tests/formatter/custom_command_with_unique_hint_favour_expansion.in.cmake]}
function(my_custom_function target_name)
# gersemi: hints { SOURCES: unique }
set(options "")
set(oneValueArgs KIND)
set(multiValueArgs SOURCES PROPERTIES)

cmake_parse_arguments(THIS_FUNCTION_PREFIX "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})
endfunction()

my_custom_function(
    already_unique
    KIND foo
    SOURCES a.cpp b.cpp c.cpp
    PROPERTIES foo bar baz
)

my_custom_function(
    not_unique
    KIND foo
    SOURCES c.cpp a.cpp c.cpp b.cpp a.cpp b.cpp c.cpp
    PROPERTIES foo bar baz
)

my_custom_function(
    not_unique_with_inline_comments
    KIND foo
    SOURCES
    c.cpp # this is c
    a.cpp # this is not c
    c.cpp # this is also c
    b.cpp
    a.cpp # this is not c
    c.cpp # this is c
    a.cpp # this is definitely not c
    PROPERTIES foo bar baz
)

my_custom_function(
    not_unique_with_bracket_and_line_comments
    KIND foo
    SOURCES
    x.cpp # this is line comment
    x.cpp #[[this is bracket comment]]
    x.cpp # this is line comment
    x.cpp #[====[this is bracket comment]====]
    x.cpp #[[this is bracket comment]]
    x.cpp #[====[this is bracket comment]====]
    PROPERTIES foo bar baz
)

my_custom_function(
    not_unique_with_comments_in_between_arguments
    KIND foo
    SOURCES
    # this is comment about c.cpp
    c.cpp
    b.cpp
    c.cpp
    # this is much longer
    # multiple lines long
    # comment about a.cpp
    a.cpp
    # this is comment about c.cpp
    c.cpp
    PROPERTIES foo bar baz
)

my_custom_function(
    not_unique_with_different_kinds_of_arguments
    KIND foo
    SOURCES
    x.cpp # unquoted argument
    "x.cpp" # quoted argument
    [===[x.cpp]===] # bracket argument
    [[x.cpp]] # bracket argument
    [===[x.cpp]===] # bracket argument
    (x.cpp) # complex argument
    [[x.cpp]] # bracket argument
    x.cpp # unquoted argument
    "x.cpp" # quoted argument
    PROPERTIES foo bar baz
)
