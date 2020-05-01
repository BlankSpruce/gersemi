add_library(FOO)

add_library(FOO BAR)

add_library(FOO BAR BAZ)

add_library(
    FOO
    STATIC
    EXCLUDE_FROM_ALL
    BAR
    BAZ
)

add_library(
    long_arg____________________________________________________________
)

add_library(
    long_arg____________________________________________________________
    long_arg____________________________________________________________
)

add_library(
    long_arg____________________________________________________________
    long_arg____________________________________________________________
    long_arg____________________________________________________________
)

add_library(
    long_arg____________________________________________________________
    SHARED
    EXCLUDE_FROM_ALL
    long_arg____________________________________________________________
    long_arg____________________________________________________________
)

add_library(FOO SHARED IMPORTED)

add_library(FOO UNKNOWN IMPORTED)

add_library(FOO STATIC IMPORTED GLOBAL)

add_library(
    long_arg____________________________________________________________
    MODULE
    IMPORTED
)

add_library(
    long_arg____________________________________________________________
    OBJECT
    IMPORTED
    GLOBAL
)

add_library(FOO OBJECT BAR)

add_library(
    FOO
    OBJECT
    BAR
    BAZ
    QUX
)

add_library(
    long_arg____________________________________________________________
    OBJECT
    long_arg____________________________________________________________
)

add_library(
    long_arg____________________________________________________________
    OBJECT
    long_arg____________________________________________________________
    long_arg____________________________________________________________
    long_arg____________________________________________________________
)

add_library(FOO ALIAS BAR)

add_library(
    long_arg____________________________________________________________
    ALIAS
    long_arg____________________________________________________________
)

add_library(FOO INTERFACE)

add_library(FOO INTERFACE IMPORTED)

add_library(FOO INTERFACE IMPORTED GLOBAL)

add_library(
    long_arg____________________________________________________________
    INTERFACE
)

add_library(
    long_arg____________________________________________________________
    INTERFACE
    IMPORTED
)

add_library(
    long_arg____________________________________________________________
    INTERFACE
    IMPORTED
    GLOBAL
)
