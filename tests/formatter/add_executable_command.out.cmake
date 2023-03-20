add_executable(FOO)

add_executable(FOO BAR)

add_executable(FOO BAR BAZ)

add_executable(FOO WIN32 MACOSX_BUNDLE EXCLUDE_FROM_ALL BAR BAZ)

add_executable(
    long_arg____________________________________________________________
)

add_executable(
    long_arg____________________________________________________________
    long_arg____________________________________________________________
)

add_executable(
    long_arg____________________________________________________________
    long_arg____________________________________________________________
    long_arg____________________________________________________________
)

add_executable(
    long_arg____________________________________________________________
    WIN32
    MACOSX_BUNDLE
    EXCLUDE_FROM_ALL
    long_arg____________________________________________________________
    long_arg____________________________________________________________
)

add_executable(FOO IMPORTED)

add_executable(FOO IMPORTED GLOBAL)

add_executable(
    long_arg____________________________________________________________
    IMPORTED
)

add_executable(
    long_arg____________________________________________________________
    IMPORTED
    GLOBAL
)

add_executable(FOO ALIAS BAR)

add_executable(
    long_arg____________________________________________________________
    ALIAS long_arg____________________________________________________________
)
