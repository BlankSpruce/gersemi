# one command
execute_process(COMMAND ${PYTHON_CMD} -c "import this")

# one long command
execute_process(COMMAND ${PYTHON_CMD} -c "long_lambda=lambda: 42; print(long_lambda())")

# one very long command
execute_process(COMMAND ${PYTHON_CMD} -c "very_long_lambda=lambda: 42; print(very_long_lambda())")

# two short commands
execute_process(COMMAND ${PYTHON} -c "print(1)" COMMAND ${PYTHON} -c "print(1)")

# two commands
execute_process(COMMAND ${PYTHON} -c "import this" COMMAND ${PYTHON} -c "import this")

# two long commands
execute_process(
    COMMAND ${PYTHON_CMD} -c "very_long_lambda=lambda: 42; print(very_long_lambda())"
    COMMAND ${PYTHON_CMD} -c "very_long_lambda=lambda: 42; print(very_long_lambda())"
)

# one short and one long command
execute_process(
    COMMAND ${PYTHON_CMD} -c "import this"
    COMMAND ${PYTHON_CMD} -c "very_long_lambda=lambda: 42; print(very_long_lambda())"
)

# one command with short list of keyworded arguments
execute_process(COMMAND ${CMD} TIMEOUT 10 ERROR_VARIABLE error OUTPUT_QUIET)

# one command with longer list of keyworded arguments
execute_process(COMMAND ${CMD} TIMEOUT 10 WORKING_DIRECTORY foo ERROR_VARIABLE error OUTPUT_QUIET ENCODING UTF-8)

# one command with all keyworded arguments
execute_process(COMMAND ${PYTHON_CMD} -c "import this"
                WORKING_DIRECTORY foo
                TIMEOUT ${timeout}
                RESULT_VARIABLE result
                RESULTS_VARIABLE results
                OUTPUT_VARIABLE output
                ERROR_VARIABLE error
                INPUT_FILE input
                OUTPUT_FILE output
                ERROR_FILE error
                OUTPUT_QUIET
                ERROR_QUIET
                COMMAND_ECHO sink
                OUTPUT_STRIP_TRAILING_WHITESPACE
                ERROR_STRIP_TRAILING_WHITESPACE
                ENCODING UTF-8)

if(TRUE)
execute_process(COMMAND ${PYTHON_CMD} -c "import this")

execute_process(COMMAND ${PYTHON} -c "import this" COMMAND ${PYTHON} -c "import this")
endif()

execute_process(
COMMAND clang-format -length=1000 -sort-includes -style=some_kind_of_style -verbose -output-replacements-xml
)

execute_process(
COMMAND clang-format -length=1000 -sort-includes -style=some_kind_of_style -verbose -output-replacements-xml "multiline
string" -some-flag with_argument -another
COMMAND clang-format -length=1000 -sort-includes -style=some_kind_of_style -verbose -output-replacements-xml "multiline
string" -some-flag with_argument -another
)

if(TRUE)
execute_process(
COMMAND clang-format -length=1000 -sort-includes -style=some_kind_of_style -verbose -output-replacements-xml
)

execute_process(
COMMAND clang-format -length=1000 -sort-includes -style=some_kind_of_style -verbose -output-replacements-xml "multiline
string" -some-flag with_argument -another
COMMAND clang-format -length=1000 -sort-includes -style=some_kind_of_style -verbose -output-replacements-xml "multiline
string" -some-flag with_argument -another
)
endif()