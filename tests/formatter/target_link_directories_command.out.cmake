target_link_directories(TGT PUBLIC)

target_link_directories(TGT PRIVATE BAR)

target_link_directories(TGT INTERFACE BAR BAZ QUX)

target_link_directories(TGT PUBLIC BAR PRIVATE BAZ INTERFACE QUX)

target_link_directories(TGT PUBLIC BAR BAZ PRIVATE BAZ QUX INTERFACE QUX FOO)

target_link_directories(TGT BEFORE PRIVATE BAR)

target_link_directories(TGT BEFORE INTERFACE BAR BAZ QUX)

target_link_directories(TGT BEFORE PUBLIC BAR PRIVATE BAZ INTERFACE QUX)

target_link_directories(
    TGT
    BEFORE
    PUBLIC BAR BAZ
    PRIVATE BAZ QUX
    INTERFACE QUX FOO
)

target_link_directories(
    TGT
    PRIVATE long_arg____________________________________________________________
)

target_link_directories(
    TGT
    INTERFACE
        long_arg____________________________________________________________
        long_arg____________________________________________________________
        long_arg____________________________________________________________
)

target_link_directories(
    TGT
    PUBLIC long_arg____________________________________________________________
    PRIVATE long_arg____________________________________________________________
    INTERFACE
        long_arg____________________________________________________________
)

target_link_directories(
    TGT
    PUBLIC
        long_arg____________________________________________________________
        long_arg____________________________________________________________
    PRIVATE
        long_arg____________________________________________________________
        long_arg____________________________________________________________
    INTERFACE
        long_arg____________________________________________________________
        long_arg____________________________________________________________
)

target_link_directories(
    TGT
    BEFORE
    PUBLIC
        long_arg____________________________________________________________
        long_arg____________________________________________________________
    PRIVATE
        long_arg____________________________________________________________
        long_arg____________________________________________________________
    INTERFACE
        long_arg____________________________________________________________
        long_arg____________________________________________________________
)

target_link_directories(
    long_arg____________________________________________________________
    PUBLIC
)

target_link_directories(
    long_arg____________________________________________________________
    PRIVATE BAR
)

target_link_directories(
    long_arg____________________________________________________________
    INTERFACE BAR BAZ QUX
)

target_link_directories(
    long_arg____________________________________________________________
    PUBLIC BAR
    PRIVATE BAZ
    INTERFACE QUX
)

target_link_directories(
    long_arg____________________________________________________________
    PUBLIC BAR BAZ
    PRIVATE BAZ QUX
    INTERFACE QUX FOO
)

target_link_directories(
    long_arg____________________________________________________________
    BEFORE
    PUBLIC BAR BAZ
    PRIVATE BAZ QUX
    INTERFACE QUX FOO
)

target_link_directories(
    long_arg____________________________________________________________
    PUBLIC
)

target_link_directories(
    long_arg____________________________________________________________
    PRIVATE long_arg____________________________________________________________
)

target_link_directories(
    long_arg____________________________________________________________
    INTERFACE
        long_arg____________________________________________________________
        long_arg____________________________________________________________
        long_arg____________________________________________________________
)

target_link_directories(
    long_arg____________________________________________________________
    PUBLIC long_arg____________________________________________________________
    PRIVATE long_arg____________________________________________________________
    INTERFACE
        long_arg____________________________________________________________
)

target_link_directories(
    long_arg____________________________________________________________
    PUBLIC
        long_arg____________________________________________________________
        long_arg____________________________________________________________
    PRIVATE
        long_arg____________________________________________________________
        long_arg____________________________________________________________
    INTERFACE
        long_arg____________________________________________________________
        long_arg____________________________________________________________
)

target_link_directories(
    long_arg____________________________________________________________
    BEFORE
    PUBLIC
        long_arg____________________________________________________________
        long_arg____________________________________________________________
    PRIVATE
        long_arg____________________________________________________________
        long_arg____________________________________________________________
    INTERFACE
        long_arg____________________________________________________________
        long_arg____________________________________________________________
)
