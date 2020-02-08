if(FOO)
    message(STATUS "OK")
elseif(BAR)
    message(STATUS "OK")
else()
    message(STATUS "OK")
endif()

if(
    COMMAND
        long_arg______________________________________________________________________
    AND FOO
        IS_NEWER_THAN
        long_arg______________________________________________________________________
    OR (
        BAR
        OR long_arg______________________________________________________________________
            IN_LIST
            BAR
        AND long_arg______________________________________________________________________
            VERSION_EQUAL
            long_arg______________________________________________________________________
    )
    OR TEST
        long_arg______________________________________________________________________
)
    message(STATUS "OK")
elseif(
    COMMAND
        long_arg______________________________________________________________________
    AND FOO
        IS_NEWER_THAN
        long_arg______________________________________________________________________
    OR (
        BAR
        OR long_arg______________________________________________________________________
            IN_LIST
            BAR
        AND long_arg______________________________________________________________________
            VERSION_EQUAL
            long_arg______________________________________________________________________
    )
    OR TEST
        long_arg______________________________________________________________________
)
    message(STATUS "OK")
else()
    message(STATUS "OK")
endif()

# repeated condition of if() in else() and endif()
if(FOO)
    message(STATUS "OK")
elseif(BAR)
    message(STATUS "OK")
else(FOO)
    message(STATUS "OK")
endif(FOO)

if(
    COMMAND
        long_arg______________________________________________________________________
    AND FOO
        IS_NEWER_THAN
        long_arg______________________________________________________________________
    OR (
        BAR
        OR long_arg______________________________________________________________________
            IN_LIST
            BAR
        AND long_arg______________________________________________________________________
            VERSION_EQUAL
            long_arg______________________________________________________________________
    )
    OR TEST
        long_arg______________________________________________________________________
)
    message(STATUS "OK")
elseif(
    COMMAND
        long_arg______________________________________________________________________
    AND FOO
        IS_NEWER_THAN
        long_arg______________________________________________________________________
    OR (
        BAR
        OR long_arg______________________________________________________________________
            IN_LIST
            BAR
        AND long_arg______________________________________________________________________
            VERSION_EQUAL
            long_arg______________________________________________________________________
    )
    OR TEST
        long_arg______________________________________________________________________
)
    message(STATUS "OK")
else(
    COMMAND
        long_arg______________________________________________________________________
    AND FOO
        IS_NEWER_THAN
        long_arg______________________________________________________________________
    OR (
        BAR
        OR long_arg______________________________________________________________________
            IN_LIST
            BAR
        AND long_arg______________________________________________________________________
            VERSION_EQUAL
            long_arg______________________________________________________________________
    )
    OR TEST
        long_arg_____________________________________________________________________
)
    message(STATUS "OK")
endif(
    COMMAND
        long_arg______________________________________________________________________
    AND FOO
        IS_NEWER_THAN
        long_arg______________________________________________________________________
    OR (
        BAR
        OR long_arg______________________________________________________________________
            IN_LIST
            BAR
        AND long_arg______________________________________________________________________
            VERSION_EQUAL
            long_arg______________________________________________________________________
    )
    OR TEST
        long_arg_____________________________________________________________________
)

if(
    TARGET
        [[some very long bracket argument                                                  ]]
)
    message(STATUS "OK")
endif()

if(
    TARGET
        "some very long quoted argument                                                     "
)
    message(STATUS "OK")
endif()

if(
    TARGET
        [[some multi
line bracket
argument
foo bar baz]]
)
    message(STATUS "OK")
endif()

if(
    TARGET
        "some multi
line quoted
argument
foo bar baz"
)
    message(STATUS "OK")
endif()

if(
    FOO
        MATCHES
        [[some very long bracket argument                                             ]]
)
    message(STATUS "OK")
endif()

if(
    FOO
        MATCHES
        "some very long quoted argument                                                "
)
    message(STATUS "OK")
endif()

if(
    FOO
        MATCHES
        [[some multi
line bracket
argument
foo bar baz]]
)
    message(STATUS "OK")
endif()

if(
    FOO
        MATCHES
        "some multi
line quoted
argument
foo bar baz"
)
    message(STATUS "OK")
endif()
