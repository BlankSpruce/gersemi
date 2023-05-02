add_library(foo SHARED)

add_library(foo SHARED EXCLUDE_FROM_ALL)

add_library(
    foo
    SHARED
    a.cpp
    b.cpp
    c.cpp
)

target_link_libraries(foo PUBLIC bar)

target_link_libraries(
    foo
    PUBLIC
        bar
        baz
)

target_link_libraries(foo PUBLIC bar PRIVATE baz)

target_link_libraries(
    foo
    PUBLIC
        bar
        baz
    PRIVATE
        dependency_with_very_long_name
        another_dependency
)

if(TRUE)
    target_link_libraries(
        foo
        PUBLIC
            bar
            baz
    )

    target_link_libraries(
        foo
        PUBLIC
            bar
            baz
        PRIVATE
            dependency_with_very_long_name
            another_dependency
    )
endif()

if(TRUE)
    if(TRUE)
        target_link_libraries(
            foo
            PUBLIC
                bar
                baz
        )

        target_link_libraries(
            foo
            PUBLIC
                bar
                baz
            PRIVATE
                dependency_with_very_long_name
                another_dependency
        )
    endif()
endif()

if(
    long_arg__________________________________________________
    AND long_arg__________________________________________________
    AND long_arg__________________________________________________
)
    target_link_libraries(
        foo
        PUBLIC
            bar
            baz
    )

    target_link_libraries(
        foo
        PUBLIC
            bar
            baz
        PRIVATE
            dependency_with_very_long_name
            another_dependency
    )
endif()

if(
    long_arg__________________________________________________
    AND (
        FOO
        AND BAR
        AND BAZ
    )
    AND (
        FOO
        AND BAR
        AND BAZ
    )
)
    target_link_libraries(
        foo
        PUBLIC
            bar
            baz
    )

    target_link_libraries(
        foo
        PUBLIC
            bar
            baz
        PRIVATE
            dependency_with_very_long_name
            another_dependency
    )
endif()

add_custom_command(
    OUTPUT
        FOOBAR
    COMMAND
        clang-format -length=1000 -sort-includes
        -style=some_kind_of_style -verbose
        -output-replacements-xml
)

add_custom_command(
    OUTPUT
        FOOBAR
    COMMAND
        clang-format -length=1000 -sort-includes
        -style=some_kind_of_style -verbose
        -output-replacements-xml
        "multiline
string"
        -some-flag with_argument -another
)

if(TRUE)
    add_custom_command(
        OUTPUT
            FOOBAR
        COMMAND
            clang-format -length=1000
            -sort-includes
            -style=some_kind_of_style -verbose
            -output-replacements-xml
    )

    add_custom_command(
        OUTPUT
            FOOBAR
        COMMAND
            clang-format -length=1000
            -sort-includes
            -style=some_kind_of_style -verbose
            -output-replacements-xml
            "multiline
string"
            -some-flag with_argument -another
    )
endif()

add_custom_command(
    OUTPUT
        FOO
        # first line comment
        # second line comment
        some_other_output
        another_output
    COMMAND
        FOO
        # first line comment
        # second line comment
        some_arg_to_foo_command
        another_arg_to_foo_command
    COMMAND
        BAZ
)

cmake_minimum_required(VERSION 3.20)

cmake_minimum_required(
    VERSION 3.141592653589793238462643383279502
)
