cmake_parse_arguments(FOO BAR BAZ QUX)

cmake_parse_arguments(FOO BAR BAZ QUX some_argument)

cmake_parse_arguments(
    FOO
    BAR
    BAZ
    QUX
    some_argument1
    some_argument2
    some_argument3
)

cmake_parse_arguments(PARSE_ARGV 42 FOO BAR BAZ QUX)

cmake_parse_arguments(
    FOO
    LONG_WORD________________________________________________
    BAZ
    QUX
    some_argument
)

cmake_parse_arguments(
    FOO
    LONG_WORD________________________________________________
    BAZ
    QUX
    some_argument1
    some_argument2
    some_argument3
)

cmake_parse_arguments(
    PARSE_ARGV
    42
    FOO
    LONG_WORD________________________________________________
    BAZ
    QUX
)

if(TRUE)
    cmake_parse_arguments(FOO BAR BAZ QUX)

    cmake_parse_arguments(FOO BAR BAZ QUX some_argument)

    cmake_parse_arguments(PARSE_ARGV 42 FOO BAR BAZ QUX)

    cmake_parse_arguments(
        FOO
        LONG_WORD________________________________________________
        BAZ
        QUX
        some_argument
    )

    cmake_parse_arguments(
        PARSE_ARGV
        42
        FOO
        LONG_WORD________________________________________________
        BAZ
        QUX
    )
endif()
