if(FOO)
endif()

if(FOO AND BAR)
endif()

if(FOO AND BAR AND BAZ)
endif()

if(
    long_arg__________________________________________________
    AND long_arg__________________________________________________
    AND long_arg__________________________________________________
)
endif()

if(
    long_arg__________________________________________________
    AND (
        long_arg__________________________________________________
        AND long_arg__________________________________________________
    )
)
endif()

if(
    FOO
    AND (
        long_arg__________________________________________________
        AND long_arg__________________________________________________
        AND long_arg__________________________________________________
    )
)
endif()

if(
    long_arg__________________________________________________
    AND (
        long_arg__________________________________________________
        AND long_arg__________________________________________________
        AND long_arg__________________________________________________
    )
)
endif()

if(
    long_arg__________________________________________________
    AND (FOO AND BAR AND BAZ)
)
endif()

if(
    NOT FOO
    AND NOT BAR
    AND NOT BAZ
    AND NOT FOO
    AND NOT BAR
    AND NOT BAZ
    AND NOT FOO
    AND NOT BAR
    AND NOT BAZ
)
endif()

if(
    NOT FOO
    AND COMMAND BAR
    AND POLICY BAZ
    AND TARGET FOO
    AND EXISTS BAR
    AND IS_DIRECTORY FOO
    AND IS_SYMLINK BAZ
    AND IS_ABSOLUTE FOO
    AND DEFINED BAR
    AND NOT COMMAND BAZ
)
endif()

if(
    NOT FOO
    OR COMMAND BAR
    OR (
        POLICY BAZ
        OR TARGET FOO
        OR EXISTS BAR
        OR IS_DIRECTORY FOO
        OR IS_SYMLINK BAZ
        OR IS_ABSOLUTE FOO
    )
    OR DEFINED BAR
    OR NOT COMMAND BAZ
)
endif()

if(
    FOO IS_NEWER_THAN BAR
    OR FOO MATCHES BAR
    OR FOO LESS BAR
    OR FOO GREATER BAR
    OR FOO EQUAL BAR
    OR FOO LESS_EQUAL BAR
)
endif()

if(
    FOO
    AND COMMAND BAR
    AND POLICY BAZ
    AND FOO IS_NEWER_THAN BAR
    OR FOO MATCHES BAR
    OR TARGET FOO
    AND EXISTS BAR
    AND IS_DIRECTORY FOO
    AND IS_SYMLINK BAZ
    AND IS_ABSOLUTE FOO
    OR FOO LESS BAR
    OR FOO GREATER BAR
    OR FOO EQUAL BAR
    OR FOO LESS_EQUAL BAR
    AND DEFINED BAR
    AND NOT COMMAND BAZ
)
endif()

if(COMMAND short_arg)
endif()

if(
    COMMAND
        long_arg______________________________________________________________________
)
endif()

if(
    COMMAND
        long_arg______________________________________________________________________
    AND POLICY
        long_arg______________________________________________________________________
)
endif()

if(
    COMMAND
        long_arg______________________________________________________________________
    AND FOO
        IS_NEWER_THAN
        long_arg______________________________________________________________________
    AND DEFINED FOO
)
endif()

if(
    COMMAND
        long_arg______________________________________________________________________
    AND FOO
        IS_NEWER_THAN
        long_arg______________________________________________________________________
    OR BAR
)
endif()

if(
    COMMAND
        long_arg______________________________________________________________________
    AND FOO
        IS_NEWER_THAN
        long_arg______________________________________________________________________
    OR BAR
    OR long_arg______________________________________________________________________
        IN_LIST
        BAR
    AND long_arg______________________________________________________________________
        VERSION_EQUAL
        long_arg______________________________________________________________________
)
endif()

if(
    COMMAND
        long_arg______________________________________________________________________
    AND FOO
        IS_NEWER_THAN
        long_arg______________________________________________________________________
    OR BAR
    OR long_arg______________________________________________________________________
        IN_LIST
        BAR
    AND long_arg______________________________________________________________________
        VERSION_EQUAL
        long_arg______________________________________________________________________
    OR TEST
        long_arg______________________________________________________________________
)
endif()

if(
    long_arg______________________________________________________________________
    AND (
        long_arg______________________________________________________________________
        AND (
            long_arg______________________________________________________________________
            AND (
                long_arg______________________________________________________________________
                AND (
                    long_arg______________________________________________________________________
                    AND long_arg______________________________________________________________________
                )
            )
        )
    )
)
endif()

# nested
if(TRUE)
    if(
        FOO
        AND COMMAND BAR
        AND POLICY BAZ
        AND FOO IS_NEWER_THAN BAR
        OR FOO MATCHES BAR
        OR TARGET FOO
        AND EXISTS BAR
        AND IS_DIRECTORY FOO
        AND IS_SYMLINK BAZ
        AND IS_ABSOLUTE FOO
        OR FOO LESS BAR
        OR FOO GREATER BAR
        OR FOO EQUAL BAR
        OR FOO LESS_EQUAL BAR
        AND DEFINED BAR
        AND NOT COMMAND BAZ
    )
    endif()

    if(
        long_arg______________________________________________________________________
        AND (
            long_arg______________________________________________________________________
            AND (
                long_arg______________________________________________________________________
                AND (
                    long_arg______________________________________________________________________
                    AND (
                        long_arg______________________________________________________________________
                        AND long_arg______________________________________________________________________
                    )
                )
            )
        )
    )
    endif()
endif()
