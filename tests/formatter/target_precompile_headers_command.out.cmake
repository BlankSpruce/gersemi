target_precompile_headers(TGT PUBLIC)

target_precompile_headers(TGT PRIVATE BAR)

target_precompile_headers(TGT INTERFACE BAR BAZ QUX)

target_precompile_headers(TGT PUBLIC BAR PRIVATE BAZ INTERFACE QUX)

target_precompile_headers(TGT PUBLIC BAR BAZ PRIVATE BAZ QUX INTERFACE QUX FOO)

target_precompile_headers(TGT PUBLIC)

target_precompile_headers(
    TGT
    PRIVATE long_arg____________________________________________________________
)

target_precompile_headers(
    TGT
    INTERFACE
        long_arg____________________________________________________________
        long_arg____________________________________________________________
        long_arg____________________________________________________________
)

target_precompile_headers(
    TGT
    PUBLIC long_arg____________________________________________________________
    PRIVATE long_arg____________________________________________________________
    INTERFACE
        long_arg____________________________________________________________
)

target_precompile_headers(
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

target_precompile_headers(
    long_arg____________________________________________________________
    PUBLIC
)

target_precompile_headers(
    long_arg____________________________________________________________
    PRIVATE BAR
)

target_precompile_headers(
    long_arg____________________________________________________________
    INTERFACE BAR BAZ QUX
)

target_precompile_headers(
    long_arg____________________________________________________________
    PUBLIC BAR
    PRIVATE BAZ
    INTERFACE QUX
)

target_precompile_headers(
    long_arg____________________________________________________________
    PUBLIC BAR BAZ
    PRIVATE BAZ QUX
    INTERFACE QUX FOO
)

target_precompile_headers(
    long_arg____________________________________________________________
    PUBLIC
)

target_precompile_headers(
    long_arg____________________________________________________________
    PRIVATE long_arg____________________________________________________________
)

target_precompile_headers(
    long_arg____________________________________________________________
    INTERFACE
        long_arg____________________________________________________________
        long_arg____________________________________________________________
        long_arg____________________________________________________________
)

target_precompile_headers(
    long_arg____________________________________________________________
    PUBLIC long_arg____________________________________________________________
    PRIVATE long_arg____________________________________________________________
    INTERFACE
        long_arg____________________________________________________________
)

target_precompile_headers(
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

target_precompile_headers(FOO REUSE_FROM BAR)

target_precompile_headers(
    long_arg____________________________________________________________
    REUSE_FROM
        long_arg____________________________________________________________
)
