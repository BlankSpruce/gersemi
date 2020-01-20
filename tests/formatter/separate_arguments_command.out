separate_arguments(FOO UNIX_COMMAND "bar baz bye")

separate_arguments(FOO WINDOWS_COMMAND "bar baz bye")

separate_arguments(FOO NATIVE_COMMAND "bar baz bye")

separate_arguments(FOO)

separate_arguments(
    FOO
    NATIVE_COMMAND
    "bar baz bye another_long_argument_______________"
)

if(TRUE)
    separate_arguments(FOO UNIX_COMMAND "bar baz bye")

    separate_arguments(
        FOO
        NATIVE_COMMAND
        "bar baz bye another_long_argument_______________"
    )
endif()
