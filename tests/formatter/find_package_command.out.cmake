find_package(FOO)

find_package(FOO 1.23)

find_package(FOO 1.23 EXACT QUIET MODULE REQUIRED NO_POLICY_SCOPE)

find_package(
    FOO
    1.23
    EXACT
    QUIET
    MODULE
    REQUIRED
    foo
    bar
    OPTIONAL_COMPONENTS foo bar
    NO_POLICY_SCOPE
)

find_package(
    FOO
    1.23
    EXACT
    QUIET
    MODULE
    REQUIRED
    COMPONENTS foo bar
    OPTIONAL_COMPONENTS foo bar
    NO_POLICY_SCOPE
)

find_package(
    FOO
    1.23
    EXACT
    QUIET
    REQUIRED
    foo
    bar
    OPTIONAL_COMPONENTS foo bar
    CONFIG
    NO_POLICY_SCOPE
    NAMES foo bar
    CONFIGS foo bar
    HINTS foo bar
    PATHS foo bar
    PATH_SUFFIXES foo bar
    NO_DEFAULT_PATH
    NO_PACKAGE_ROOT_PATH
    NO_CMAKE_PATH
    NO_CMAKE_ENVIRONMENT_PATH
    NO_CMAKE_PACKAGE_REGISTRY
    NO_CMAKE_BUILDS_PATH
    NO_CMAKE_SYSTEM_PATH
    NO_CMAKE_SYSTEM_PACKAGE_REGISTRY
    CMAKE_FIND_ROOT_PATH_BOTH
)

find_package(
    FOO
    1.23
    EXACT
    QUIET
    REQUIRED
    COMPONENTS foo bar
    OPTIONAL_COMPONENTS foo bar
    CONFIG
    NO_POLICY_SCOPE
    NAMES foo bar
    CONFIGS foo bar
    HINTS foo bar
    PATHS foo bar
    PATH_SUFFIXES foo bar
    NO_DEFAULT_PATH
    NO_PACKAGE_ROOT_PATH
    NO_CMAKE_PATH
    NO_CMAKE_ENVIRONMENT_PATH
    NO_CMAKE_PACKAGE_REGISTRY
    NO_CMAKE_BUILDS_PATH
    NO_CMAKE_SYSTEM_PATH
    NO_CMAKE_SYSTEM_PACKAGE_REGISTRY
    CMAKE_FIND_ROOT_PATH_BOTH
)

find_package(
    FOO
    1.23
    EXACT
    QUIET
    MODULE
    REQUIRED
    long_arg__________________________________________________
    long_arg__________________________________________________
    OPTIONAL_COMPONENTS
        long_arg__________________________________________________
        long_arg__________________________________________________
    NO_POLICY_SCOPE
)

find_package(
    FOO
    1.23
    EXACT
    QUIET
    MODULE
    REQUIRED
    COMPONENTS
        long_arg__________________________________________________
        long_arg__________________________________________________
    OPTIONAL_COMPONENTS
        long_arg__________________________________________________
        long_arg__________________________________________________
    NO_POLICY_SCOPE
)

find_package(
    long_arg__________________________________________________
    1.23
    EXACT
    QUIET
    REQUIRED
    long_arg__________________________________________________
    long_arg__________________________________________________
    OPTIONAL_COMPONENTS
        long_arg__________________________________________________
        long_arg__________________________________________________
    CONFIG
    NO_POLICY_SCOPE
    NAMES
        long_arg__________________________________________________
        long_arg__________________________________________________
    CONFIGS
        long_arg__________________________________________________
        long_arg__________________________________________________
    HINTS
        long_arg__________________________________________________
        long_arg__________________________________________________
    PATHS
        long_arg__________________________________________________
        long_arg__________________________________________________
    PATH_SUFFIXES
        long_arg__________________________________________________
        long_arg__________________________________________________
    NO_DEFAULT_PATH
    NO_PACKAGE_ROOT_PATH
    NO_CMAKE_PATH
    NO_CMAKE_ENVIRONMENT_PATH
    NO_CMAKE_PACKAGE_REGISTRY
    NO_CMAKE_BUILDS_PATH
    NO_CMAKE_SYSTEM_PATH
    NO_CMAKE_SYSTEM_PACKAGE_REGISTRY
    CMAKE_FIND_ROOT_PATH_BOTH
)

find_package(
    long_arg__________________________________________________
    1.23
    EXACT
    QUIET
    REQUIRED
    COMPONENTS
        long_arg__________________________________________________
        long_arg__________________________________________________
    OPTIONAL_COMPONENTS
        long_arg__________________________________________________
        long_arg__________________________________________________
    CONFIG
    NO_POLICY_SCOPE
    NAMES
        long_arg__________________________________________________
        long_arg__________________________________________________
    CONFIGS
        long_arg__________________________________________________
        long_arg__________________________________________________
    HINTS
        long_arg__________________________________________________
        long_arg__________________________________________________
    PATHS
        long_arg__________________________________________________
        long_arg__________________________________________________
    PATH_SUFFIXES
        long_arg__________________________________________________
        long_arg__________________________________________________
    NO_DEFAULT_PATH
    NO_PACKAGE_ROOT_PATH
    NO_CMAKE_PATH
    NO_CMAKE_ENVIRONMENT_PATH
    NO_CMAKE_PACKAGE_REGISTRY
    NO_CMAKE_BUILDS_PATH
    NO_CMAKE_SYSTEM_PATH
    NO_CMAKE_SYSTEM_PACKAGE_REGISTRY
    CMAKE_FIND_ROOT_PATH_BOTH
)
