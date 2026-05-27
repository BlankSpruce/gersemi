FetchContent_Declare(foobar FIND_PACKAGE_ARGS 1.23)

FetchContent_Declare(
    foobar
    FIND_PACKAGE_ARGS 1.23 EXACT QUIET MODULE REQUIRED NO_POLICY_SCOPE
)

FetchContent_Declare(
    foobar
    FIND_PACKAGE_ARGS
        1.23
        EXACT
        QUIET
        MODULE
        REQUIRED foo bar
        OPTIONAL_COMPONENTS foo bar
        NO_POLICY_SCOPE
)

FetchContent_Declare(foobar FIND_PACKAGE_ARGS)

FetchContent_Declare(
    foobar
    FIND_PACKAGE_ARGS EXACT QUIET MODULE REQUIRED NO_POLICY_SCOPE
)

FetchContent_Declare(
    foobar
    FIND_PACKAGE_ARGS
        EXACT
        QUIET
        MODULE
        REQUIRED
            foo
            bar____________________________________________________________
        OPTIONAL_COMPONENTS foo bar
        NO_POLICY_SCOPE
)
