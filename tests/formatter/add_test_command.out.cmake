add_test(NAME FOO COMMAND BAR)

add_test(NAME FOO COMMAND BAR BAZ QUX)

add_test(NAME FOO COMMAND BAR CONFIGURATIONS FOO COMMAND_EXPAND_LISTS)

add_test(NAME FOO COMMAND BAR BAZ WORKING_DIRECTORY FOO COMMAND_EXPAND_LISTS)

add_test(
    NAME FOO
    COMMAND BAR BAZ QUX
    CONFIGURATIONS FOO
    WORKING_DIRECTORY FOO
    COMMAND_EXPAND_LISTS
)

add_test(
    NAME long_arg____________________________________________________________
    COMMAND long_arg____________________________________________________________
)

add_test(
    NAME long_arg____________________________________________________________
    COMMAND
        long_arg____________________________________________________________
        long_arg____________________________________________________________
        long_arg____________________________________________________________
)

add_test(
    NAME long_arg____________________________________________________________
    COMMAND long_arg____________________________________________________________
    CONFIGURATIONS
        long_arg____________________________________________________________
    COMMAND_EXPAND_LISTS
)

add_test(
    NAME long_arg____________________________________________________________
    COMMAND
        long_arg____________________________________________________________
        long_arg____________________________________________________________
    WORKING_DIRECTORY
        long_arg____________________________________________________________
    COMMAND_EXPAND_LISTS
)

add_test(
    NAME long_arg____________________________________________________________
    COMMAND
        long_arg____________________________________________________________
        long_arg____________________________________________________________
        long_arg____________________________________________________________
    CONFIGURATIONS
        long_arg____________________________________________________________
    WORKING_DIRECTORY
        long_arg____________________________________________________________
    COMMAND_EXPAND_LISTS
)

add_test(FOO BAR)

add_test(FOO BAR BAZ QUX)

add_test(
    long_arg____________________________________________________________
    long_arg____________________________________________________________
)

add_test(
    long_arg____________________________________________________________
    long_arg____________________________________________________________
    long_arg____________________________________________________________
    long_arg____________________________________________________________
)
