gtest_discover_tests(FOOBAR)

gtest_discover_tests(FOOBAR EXTRA_ARGS arg1 arg2 arg3 arg4)

gtest_discover_tests(
    FOOBAR
    EXTRA_ARGS arg1 arg2 arg3 arg4 arg5
)

gtest_discover_tests(
    FOOBAR
    EXTRA_ARGS arg1 arg2 arg3 arg4 arg5 arg6 arg7 arg8 arg9 arg10
)

gtest_discover_tests(
    FOOBAR
    EXTRA_ARGS
        --option1
        --long_option__________________________________________________ --key
        long_value__________________________________________________
)

gtest_discover_tests(FOOBAR PROPERTIES key1 value1 key2 value2)

gtest_discover_tests(
    FOOBAR
    PROPERTIES key1 value1 key2 value2 key3 value3 key4 value4
)

gtest_discover_tests(
    FOOBAR
    PROPERTIES
        key1 value1
        key2 value2
        key3 value3
        key4 value4
        key5 value5
        key6 value6
        key7 value7
        key8 value8
)

gtest_discover_tests(
    FOOBAR
    PROPERTIES
        key1 value1
        key2 value2
        # line comment
        key3 value3
        key4 value4
        key5 value5
        key6 value6
        key7 value7
        key8 value8
)

gtest_discover_tests(
    FOOBAR
    PROPERTIES
        key1 value1
        key2 value2
        short_key
            long_value____________________________________________________________
        long_key____________________________________________________________
            short_value
        long_key____________________________________________________________
            long_value____________________________________________________________
        key6 value6
        key7 value7
)

gtest_discover_tests(
    FOOBAR
    EXTRA_ARGS
        --option1
        --long_option__________________________________________________ --key
        long_value__________________________________________________
    WORKING_DIRECTORY FOO
    TEST_PREFIX BAR
    TEST_SUFFIX BAZ
    NO_PRETTY_TYPES
    NO_PRETTY_VALUES
    PROPERTIES
        key1 value1
        key2 value2
        short_key
            long_value____________________________________________________________
        # line comment
        long_key____________________________________________________________
            short_value
        long_key____________________________________________________________
            long_value____________________________________________________________
        key6 value6
        key7 value7
    TEST_LIST FOO
    DISCOVERY_TIMEOUT BAR
    XML_OUTPUT_DIR BAZ
    DISCOVERY_MODE POST_BUILD
)
