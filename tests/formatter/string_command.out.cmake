string(FIND foo bar baz)

string(FIND foo bar baz REVERSE)

string(
    FIND
        long_string_________________________
        long_substring_________________________
        long_output_variable_________________________
)

string(
    FIND
        long_string_________________________
        long_substring_________________________
        long_output_variable_________________________
    REVERSE
)

string(REPLACE foo bar baz input1)

string(
    REPLACE
    long_string_________________________
    long_string_________________________
    long_output_variable_________________________
    input1
    long_input_________________________
)

string(REGEX MATCH regex foo bar)

string(REGEX MATCHALL regex foo bar)

string(REGEX REPLACE regex foo bar baz)

string(
    REGEX MATCH
    long_regex_________________________
    long_output_variable_________________________
    input1
    long_input_________________________
)

string(APPEND foo bar)

string(
    APPEND
    long_argument_____________________________________________
    long_argument_____________________________________________
)

string(PREPEND foo bar)

string(
    PREPEND
    long_argument_____________________________________________
    long_argument_____________________________________________
)

string(CONCAT foo bar)

string(
    CONCAT
    long_argument_____________________________________________
    long_argument_____________________________________________
)

string(JOIN foo bar baz)

string(
    JOIN
    long_argument_____________________________________________
    long_argument_____________________________________________
    long_argument_____________________________________________
)

string(TOLOWER foo bar)

string(
    TOLOWER
    long_argument_____________________________________________
    long_argument_____________________________________________
)

string(TOUPPER foo bar)

string(
    TOUPPER
    long_argument_____________________________________________
    long_argument_____________________________________________
)

string(LENGTH foo bar)

string(
    LENGTH
    long_argument_____________________________________________
    long_argument_____________________________________________
)

string(SUBSTRING foo 10 42 bar)

string(
    SUBSTRING
    long_argument_____________________________________________
    10
    42
    long_argument_____________________________________________
)

string(STRIP foo bar)

string(
    STRIP
    long_argument_____________________________________________
    long_argument_____________________________________________
)

string(GENEX_STRIP foo bar)

string(
    GENEX_STRIP
    long_argument_____________________________________________
    long_argument_____________________________________________
)

string(REPEAT foo 100 bar)

string(
    REPEAT
    long_argument_____________________________________________
    100
    long_argument_____________________________________________
)

string(COMPARE LESS foo bar baz)

string(COMPARE GREATER foo bar baz)

string(COMPARE EQUAL foo bar baz)

string(COMPARE NOTEQUAL foo bar baz)

string(COMPARE LESS_EQUAL foo bar baz)

string(COMPARE GREATER_EQUAL foo bar baz)

string(
    COMPARE LESS
    long_argument_______________________________
    long_argument_______________________________
    long_argument_______________________________
)

string(
    COMPARE GREATER
    long_argument_______________________________
    long_argument_______________________________
    long_argument_______________________________
)

string(
    COMPARE EQUAL
    long_argument_______________________________
    long_argument_______________________________
    long_argument_______________________________
)

string(
    COMPARE NOTEQUAL
    long_argument_______________________________
    long_argument_______________________________
    long_argument_______________________________
)

string(
    COMPARE LESS_EQUAL
    long_argument_______________________________
    long_argument_______________________________
    long_argument_______________________________
)

string(
    COMPARE GREATER_EQUAL
    long_argument_______________________________
    long_argument_______________________________
    long_argument_______________________________
)

string(<HASH> foo MD5)

string(
    <HASH>
    long_argument______________________________________________________________
    SHA224
)

string(ASCII 1 2 3 foo)

string(
    ASCII
    1
    2
    3
    long_argument______________________________________________________________
)

string(CONFIGURE foo bar @ONLY ESCAPE_QUOTES)

string(
    CONFIGURE
        long_argument______________________________________________________________
        long_argument______________________________________________________________
    @ONLY
    ESCAPE_QUOTES
)

string(MAKE_C_IDENTIFIER foo bar)

string(
    MAKE_C_IDENTIFIER
    long_argument______________________________________________________________
    long_argument______________________________________________________________
)

string(RANDOM LENGTH 1 ALPHABET foo RANDOM_SEED 42 foo)

string(
    RANDOM
    LENGTH 1
    ALPHABET
        long_argument______________________________________________________________
    RANDOM_SEED 42
    long_argument______________________________________________________________
)

string(TIMESTAMP foo format UTC)

string(
    TIMESTAMP
    long_argument______________________________________________________________
    long_argument______________________________________________________________
    UTC
)

string(UUID foo NAMESPACE bar NAME baz TYPE MD5 UPPER)

string(
    UUID
        long_argument______________________________________________________________
    NAMESPACE
        long_argument______________________________________________________________
    NAME
        long_argument______________________________________________________________
    TYPE SHA1
    UPPER
)
