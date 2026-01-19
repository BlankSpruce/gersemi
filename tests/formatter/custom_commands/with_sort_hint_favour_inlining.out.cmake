function(my_custom_function target_name)
    # gersemi: hints { SOURCES: sort }
    set(options "")
    set(oneValueArgs KIND)
    set(multiValueArgs SOURCES PROPERTIES)

    cmake_parse_arguments(
        THIS_FUNCTION_PREFIX
        "${options}"
        "${oneValueArgs}"
        "${multiValueArgs}"
        ${ARGN}
    )
endfunction()

my_custom_function(
    already_sorted
    KIND foo
    SOURCES a.cpp b.cpp c.cpp
    PROPERTIES foo bar baz
)

my_custom_function(
    not_sorted
    KIND foo
    SOURCES a.cpp b.cpp c.cpp
    PROPERTIES foo bar baz
)

my_custom_function(
    not_sorted_with_duplicates
    KIND foo
    SOURCES
        a.cpp
        a.cpp
        b.cpp
        b.cpp
        c.cpp
        c.cpp
        c.cpp
    PROPERTIES foo bar baz
)

my_custom_function(
    not_sorted_with_inline_comments_and_duplicates
    KIND foo
    SOURCES
        a.cpp # this is definitely not c
        a.cpp # this is not c
        b.cpp
        c.cpp # this is also c
        c.cpp # this is c
    PROPERTIES foo bar baz
)

my_custom_function(
    not_sorted_with_bracket_and_line_comments
    KIND foo
    SOURCES
        x.cpp # this is line comment
        x.cpp #[====[this is bracket comment]====]
        x.cpp #[[this is bracket comment]]
    PROPERTIES foo bar baz
)

my_custom_function(
    not_sorted_with_comments_in_between_arguments
    KIND foo
    SOURCES
        # this is much longer
        # multiple lines long
        # comment about a.cpp
        a.cpp
        b.cpp
        # this is comment about c.cpp
        c.cpp
    PROPERTIES foo bar baz
)

my_custom_function(
    not_sorted_with_duplicates_differing_by_preceding_comments
    KIND foo
    SOURCES
        # this is A comment
        x.cpp
        # this is B comment
        x.cpp
        # this is C comment
        x.cpp
    PROPERTIES foo bar baz
)

my_custom_function(
    not_sorted_with_duplicates_differing_by_preceding_comments_of_different_lengths
    KIND foo
    SOURCES
        # this is
        # 2 line long comment
        x.cpp
        # this is
        # 3 line
        # long comment
        x.cpp
        # this is 1 line long comment
        x.cpp
    PROPERTIES foo bar baz
)

my_custom_function(
    not_sorted_with_different_kinds_of_arguments
    KIND foo
    SOURCES
        "x.cpp" # quoted argument
        (x.cpp) # complex argument
        [===[x.cpp]===] # bracket argument
        [[x.cpp]] # bracket argument
        x.cpp # unquoted argument
    PROPERTIES foo bar baz
)
