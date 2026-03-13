cmake_instrumentation(
    API_VERSION 1
    DATA_VERSION 1
    HOOKS foo bar baz
    OPTIONS foo bar baz
    CALLBACK foo
    CALLBACK bar
    CALLBACK baz
    CUSTOM_CONTENT foo STRING foo
    CUSTOM_CONTENT foo__________________________________________________
        LIST foo
    CUSTOM_CONTENT foo JSON foo
)
