ctest_configure(BUILD FOO SOURCE BAR APPEND OPTIONS BAZ RETURN_VALUE QUX QUIET)

ctest_configure(
    BUILD FOO
    SOURCE BAR
    APPEND
    OPTIONS BAZ
    RETURN_VALUE QUX
    QUIET
    CAPTURE_CMAKE_ERROR FOO
)

ctest_configure(
    BUILD long_arg____________________________________________________________
    SOURCE long_arg____________________________________________________________
    APPEND
    OPTIONS long_arg____________________________________________________________
    RETURN_VALUE
        long_arg____________________________________________________________
    QUIET
)

ctest_configure(
    BUILD long_arg____________________________________________________________
    SOURCE long_arg____________________________________________________________
    APPEND
    OPTIONS long_arg____________________________________________________________
    RETURN_VALUE
        long_arg____________________________________________________________
    QUIET
    CAPTURE_CMAKE_ERROR
        long_arg____________________________________________________________
)
