ctest_test(BUILD FOO APPEND START BAR END BAZ STRIDE FOO EXCLUDE BAR)

ctest_test(
    BUILD FOO
    APPEND
    START BAR
    END BAZ
    STRIDE FOO
    EXCLUDE BAR
    INCLUDE BAZ
    EXCLUDE_LABEL FOO
    INCLUDE_LABEL BAR
    EXCLUDE_FIXTURE BAZ
    EXCLUDE_FIXTURE_SETUP FOO
    EXCLUDE_FIXTURE_CLEANUP BAR
    PARALLEL_LEVEL BAZ
    RESOURCE_SPEC_FILE FOO
    TEST_LOAD BAR
    SCHEDULE_RANDOM ON
    STOP_TIME FOO
    RETURN_VALUE BAR
    CAPTURE_CMAKE_ERROR BAZ
    QUIET
)

ctest_test(
    BUILD long_arg____________________________________________________________
    APPEND
    START long_arg____________________________________________________________
    END long_arg____________________________________________________________
    STRIDE long_arg____________________________________________________________
    EXCLUDE long_arg____________________________________________________________
)

ctest_test(
    BUILD long_arg____________________________________________________________
    APPEND
    START long_arg____________________________________________________________
    END long_arg____________________________________________________________
    STRIDE long_arg____________________________________________________________
    EXCLUDE long_arg____________________________________________________________
    INCLUDE long_arg____________________________________________________________
    EXCLUDE_LABEL
        long_arg____________________________________________________________
    INCLUDE_LABEL
        long_arg____________________________________________________________
    EXCLUDE_FIXTURE
        long_arg____________________________________________________________
    EXCLUDE_FIXTURE_SETUP
        long_arg____________________________________________________________
    EXCLUDE_FIXTURE_CLEANUP
        long_arg____________________________________________________________
    PARALLEL_LEVEL
        long_arg____________________________________________________________
    RESOURCE_SPEC_FILE
        long_arg____________________________________________________________
    TEST_LOAD
        long_arg____________________________________________________________
    SCHEDULE_RANDOM ON
    STOP_TIME
        long_arg____________________________________________________________
    RETURN_VALUE
        long_arg____________________________________________________________
    CAPTURE_CMAKE_ERROR
        long_arg____________________________________________________________
    QUIET
)
