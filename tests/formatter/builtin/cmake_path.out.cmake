cmake_path(GET FOO EXTENSION LAST_ONLY BAR)

cmake_path(
    GET long_name__________________________________________________
    EXTENSION LAST_ONLY BAR
)

cmake_path(
    GET FOO
    EXTENSION LAST_ONLY long_name________________________________________
)

cmake_path(
    GET long_name__________________________________________________
    EXTENSION LAST_ONLY
        long_name__________________________________________________
)

cmake_path(REPLACE_EXTENSION FOO LAST_ONLY OUTPUT_VARIABLE BAR)

cmake_path(
    REPLACE_EXTENSION
        long_name__________________________________________________
    LAST_ONLY
    OUTPUT_VARIABLE BAR
)

cmake_path(
    REPLACE_EXTENSION FOO
    LAST_ONLY
    OUTPUT_VARIABLE
        long_name____________________________________________________________
)

cmake_path(
    REPLACE_EXTENSION
        long_name__________________________________________________
    LAST_ONLY
    OUTPUT_VARIABLE long_name__________________________________________________
)
