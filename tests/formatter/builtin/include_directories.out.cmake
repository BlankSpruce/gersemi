include_directories(FOO)

include_directories(FOO BAR BAZ)

include_directories(AFTER FOO BAR BAZ)

include_directories(BEFORE SYSTEM FOO BAR BAZ)

include_directories(
    long_arg____________________________________________________________
)

include_directories(
    long_arg____________________________________________________________
    long_arg____________________________________________________________
    long_arg____________________________________________________________
)

include_directories(
    AFTER
    long_arg____________________________________________________________
    long_arg____________________________________________________________
    long_arg____________________________________________________________
)

include_directories(
    BEFORE
    SYSTEM
    long_arg____________________________________________________________
    long_arg____________________________________________________________
    long_arg____________________________________________________________
)
