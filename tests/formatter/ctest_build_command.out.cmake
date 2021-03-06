ctest_build(BUILD FOO APPEND CONFIGURATION BAR FLAGS BAZ PROJECT_NAME QUX)

ctest_build(
    BUILD FOO
    APPEND
    CONFIGURATION BAR
    FLAGS BAZ
    PROJECT_NAME QUX
    TARGET FOO
    NUMBER_ERRORS BAR
    NUMBER_WARNINGS BAZ
    RETURN_VALUE QUX
    CAPTURE_CMAKE_ERROR FOO
    QUIET
)

ctest_build(
    BUILD long_arg____________________________________________________________
    APPEND
    CONFIGURATION
        long_arg____________________________________________________________
    FLAGS long_arg____________________________________________________________
    PROJECT_NAME
        long_arg____________________________________________________________
)

ctest_build(
    BUILD long_arg____________________________________________________________
    APPEND
    CONFIGURATION
        long_arg____________________________________________________________
    FLAGS long_arg____________________________________________________________
    PROJECT_NAME
        long_arg____________________________________________________________
    TARGET long_arg____________________________________________________________
    NUMBER_ERRORS
        long_arg____________________________________________________________
    NUMBER_WARNINGS
        long_arg____________________________________________________________
    RETURN_VALUE
        long_arg____________________________________________________________
    CAPTURE_CMAKE_ERROR
        long_arg____________________________________________________________
    QUIET
)
