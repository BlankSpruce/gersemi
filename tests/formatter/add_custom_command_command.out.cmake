add_custom_command(OUTPUT FOO COMMAND BAR)

add_custom_command(OUTPUT FOO COMMAND BAR BAZ)

add_custom_command(OUTPUT FOO COMMAND BAR ARGS BAZ QUX)

add_custom_command(
    OUTPUT long_arg____________________________________________________________
    COMMAND long_arg____________________________________________________________
)

add_custom_command(
    OUTPUT long_arg____________________________________________________________
    COMMAND
        long_arg____________________________________________________________
        long_arg____________________________________________________________
)

add_custom_command(
    OUTPUT long_arg____________________________________________________________
    COMMAND long_arg____________________________________________________________
    ARGS
        long_arg____________________________________________________________
        long_arg____________________________________________________________
)

add_custom_command(
    OUTPUT FOO BAR BAZ
    COMMAND FOO BAR BAZ
    COMMAND FOO BAR BAZ
    COMMAND FOO BAR BAZ
    MAIN_DEPENDENCY FOO
    DEPENDS FOO BAR BAZ
    BYPRODUCTS FOO BAR BAZ
    IMPLICIT_DEPENDS CXX FOO PYTHON BAR FORTRAN BAZ
    WORKING_DIRECTORY FOO
    COMMENT BAR
    DEPFILE BAZ
    JOB_POOL FOO
    VERBATIM
    APPEND
    USES_TERMINAL
    COMMAND_EXPAND_LISTS
)

add_custom_command(
    OUTPUT
        long_arg____________________________________________________________
        long_arg____________________________________________________________
        long_arg____________________________________________________________
    COMMAND
        long_arg____________________________________________________________
        long_arg____________________________________________________________
        long_arg____________________________________________________________
    COMMAND
        long_arg____________________________________________________________
        long_arg____________________________________________________________
        long_arg____________________________________________________________
    COMMAND
        long_arg____________________________________________________________
        long_arg____________________________________________________________
        long_arg____________________________________________________________
    MAIN_DEPENDENCY
        long_arg____________________________________________________________
    DEPENDS
        long_arg____________________________________________________________
        long_arg____________________________________________________________
        long_arg____________________________________________________________
    BYPRODUCTS
        long_arg____________________________________________________________
        long_arg____________________________________________________________
        long_arg____________________________________________________________
    IMPLICIT_DEPENDS
        CXX
        long_arg____________________________________________________________
        PYTHON
        long_arg____________________________________________________________
        FORTRAN
        long_arg____________________________________________________________
    WORKING_DIRECTORY
        long_arg____________________________________________________________
    COMMENT long_arg____________________________________________________________
    DEPFILE long_arg____________________________________________________________
    JOB_POOL
        long_arg____________________________________________________________
    VERBATIM
    APPEND
    USES_TERMINAL
    COMMAND_EXPAND_LISTS
)

add_custom_command(TARGET FOO PRE_BUILD COMMAND BAR)

add_custom_command(TARGET FOO PRE_BUILD COMMAND BAR BAZ)

add_custom_command(TARGET FOO PRE_BUILD COMMAND BAR ARGS BAZ QUX)

add_custom_command(
    TARGET long_arg____________________________________________________________
    PRE_LINK
    COMMAND long_arg____________________________________________________________
)

add_custom_command(
    TARGET long_arg____________________________________________________________
    PRE_LINK
    COMMAND
        long_arg____________________________________________________________
        long_arg____________________________________________________________
)

add_custom_command(
    TARGET long_arg____________________________________________________________
    PRE_LINK
    COMMAND long_arg____________________________________________________________
    ARGS
        long_arg____________________________________________________________
        long_arg____________________________________________________________
)

add_custom_command(
    TARGET FOO
    POST_BUILD
    COMMAND FOO BAR BAZ
    COMMAND FOO BAR BAZ
    COMMAND FOO BAR BAZ
    BYPRODUCTS FOO BAR BAZ
    WORKING_DIRECTORY FOO
    COMMENT BAR
    VERBATIM
    USES_TERMINAL
    COMMAND_EXPANDS_LISTS
)

add_custom_command(
    TARGET long_arg____________________________________________________________
    POST_BUILD
    COMMAND
        long_arg____________________________________________________________
        long_arg____________________________________________________________
        long_arg____________________________________________________________
    COMMAND
        long_arg____________________________________________________________
        long_arg____________________________________________________________
        long_arg____________________________________________________________
    COMMAND
        long_arg____________________________________________________________
        long_arg____________________________________________________________
        long_arg____________________________________________________________
    BYPRODUCTS
        long_arg____________________________________________________________
        long_arg____________________________________________________________
        long_arg____________________________________________________________
    WORKING_DIRECTORY
        long_arg____________________________________________________________
    COMMENT long_arg____________________________________________________________
    VERBATIM
    USES_TERMINAL
    COMMAND_EXPANDS_LISTS
)

add_custom_command(
    OUTPUT FOOBAR
    COMMAND
        clang-format -length=1000 -sort-includes -style=some_kind_of_style
        -verbose -output-replacements-xml
)

add_custom_command(
    OUTPUT FOOBAR
    COMMAND
        clang-format -length=1000 -sort-includes -style=some_kind_of_style
        -verbose -output-replacements-xml
        "multiline
string"
        -some-flag with_argument -another
)

if(TRUE)
    add_custom_command(
        OUTPUT FOOBAR
        COMMAND
            clang-format -length=1000 -sort-includes -style=some_kind_of_style
            -verbose -output-replacements-xml
    )

    add_custom_command(
        OUTPUT FOOBAR
        COMMAND
            clang-format -length=1000 -sort-includes -style=some_kind_of_style
            -verbose -output-replacements-xml
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
        some_arg_to_foo_command another_arg_to_foo_command
    COMMAND BAZ
)

add_custom_command(
    OUTPUT FOOBAR
    COMMAND clang-format
    ARGS
        -length=1000 -sort-includes -style=some_kind_of_style -verbose
        -output-replacements-xml
        "multiline
string"
        -some-flag with_argument -another
)
