# as in report
include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(
    Pylon
    REQUIRED_VARS
        PYLON_INCLUDE_DIR
        PYLON_BASE_LIBRARY
        PYLON_GC_BASE_LIBRARY
        PYLON_GENAPI_LIBRARY
        PYLON_UTILITY_LIBRARY
    # omitted for brevity
    FOUND_VAR PYLON_FOUND
    VERSION_VAR PYLON_VERSION
    FAIL_MESSAGE "Failed to find Pylon"
)

# with line comment
find_package_handle_standard_args(
    Pylon
    FOUND_VAR PYLON_FOUND
    # foobar
    REQUIRED_VARS
        PYLON_INCLUDE_DIR
        PYLON_BASE_LIBRARY
        PYLON_GC_BASE_LIBRARY
        PYLON_GENAPI_LIBRARY
        PYLON_UTILITY_LIBRARY
)

# with bracket comment
find_package_handle_standard_args(
    Pylon
    FOUND_VAR PYLON_FOUND
    #[[foobar]]
    REQUIRED_VARS
        PYLON_INCLUDE_DIR
        PYLON_BASE_LIBRARY
        PYLON_GC_BASE_LIBRARY
        PYLON_GENAPI_LIBRARY
        PYLON_UTILITY_LIBRARY
)

# all kinds of places for comments
find_package_handle_standard_args(
    Pylon
    # foobar
    REQUIRED_VARS # foobar
        PYLON_INCLUDE_DIR
        # foobar
        PYLON_BASE_LIBRARY
        PYLON_GC_BASE_LIBRARY
        PYLON_GENAPI_LIBRARY # foobar
        PYLON_UTILITY_LIBRARY
    # foobar
    FOUND_VAR # foobar
        PYLON_FOUND
    # foobar
    VERSION_VAR PYLON_VERSION
    FAIL_MESSAGE "Failed to find Pylon"
)

# multiple comments on the boundary
find_package_handle_standard_args(
    Pylon
    # foobar
    REQUIRED_VARS # foobar
        PYLON_INCLUDE_DIR
        # foobar
        PYLON_BASE_LIBRARY
        PYLON_GC_BASE_LIBRARY
        PYLON_GENAPI_LIBRARY # foobar
        PYLON_UTILITY_LIBRARY
    # foo
    #[===[ bar ]===]
    # baz
    FOUND_VAR # foobar
        PYLON_FOUND
    # foobar
    VERSION_VAR PYLON_VERSION
    # foobar
    FAIL_MESSAGE "Failed to find Pylon"
    # foo
    # bar
    # baz
)
