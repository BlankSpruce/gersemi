list(LENGTH FOO BAR)

list(
    LENGTH
    long_list_name_________________________
    long_variable_name_________________________
)

list(GET FOO 1 BAR)

list(
    GET
    long_list_name_________________________
    1
    2
    3
    4
    5
    6
    7
    long_variable_name_________________________
)

list(JOIN FOO bar BAZ)

list(
    JOIN
    long_list_name_________________________
    long_glue_________________________
    long_variable_name_________________________
)

list(SUBLIST FOO 0 5 BAR)

list(
    SUBLIST
    long_list_name_________________________
    0
    5
    long_variable_name_________________________
)

list(FIND FOO 42 BAR)

list(
    FIND
    long_list_name_________________________
    42
    long_variable_name_________________________
)

list(APPEND FOO bar)

list(
    APPEND
    long_list_name_________________________
    arg1
    arg2
    arg3
    arg4
    long_arg_________________________
)

list(FILTER FOO INCLUDE REGEX regex)

list(FILTER FOO EXCLUDE REGEX regex)

list(
    FILTER long_list_name_________________________
    INCLUDE
    REGEX long_regex_________________________
)

list(INSERT FOO 42 element1)

list(
    INSERT
    long_list_name_________________________
    42
    element1
    element2
    element3
    element4
    long_element_________________________
)

list(POP_BACK FOO bar)

list(
    POP_BACK
    long_list_name_________________________
    out_var1
    out_var2
    out_var3
    out_var4
    long_out_var_________________________
)

list(POP_FRONT FOO bar)

list(
    POP_FRONT
    long_list_name_________________________
    out_var1
    out_var2
    out_var3
    out_var4
    long_out_var_________________________
)

list(PREPEND FOO element1)

list(
    PREPEND
    long_list_name_________________________
    element1
    element2
    element3
    element4
    long_element_________________________
)

list(REMOVE_ITEM FOO value1)

list(
    REMOVE_ITEM
    long_list_name_________________________
    value1
    value2
    value3
    value4
    long_value_________________________
)

list(REMOVE_AT FOO 1)

list(REMOVE_AT FOO 1 2 3 4)

list(
    REMOVE_AT
    FOO
    1
    2
    3
    4
    5
)

list(REMOVE_DUPLICATES FOO)

list(
    REMOVE_DUPLICATES
    long_list_name____________________________________________________________
)

list(
    TRANSFORM
        long_list_name____________________________________________________________
    APPEND long_value_________________________
)

list(TRANSFORM FOO APPEND bar)

list(TRANSFORM FOO PREPEND bar)

list(TRANSFORM FOO TOLOWER bar)

list(TRANSFORM FOO TOUPPER bar)

list(TRANSFORM FOO STRIP bar)

list(TRANSFORM FOO GENEX_STRIP bar)

list(TRANSFORM FOO REPLACE bar baz)

list(
    TRANSFORM
        long_list_name____________________________________________________________
    REPLACE regex replace1 long_replace_________________________
)

list(REVERSE foo)

list(SORT FOO COMPARE STRING CASE SENSITIVE ORDER ASCENDING)

list(
    SORT
        long_list_name____________________________________________________________
    COMPARE FILE_BASENAME
    CASE INSENSITIVE
    ORDER DESCENDING
)

list(
    TRANSFORM
        long_list_name____________________________________________________________
    REPLACE expression replace_expression
    AT 0 1 2 314159
    OUTPUT_VARIABLE
        long_output_variable_name____________________________________________________________
)

list(
    TRANSFORM
        long_list_name____________________________________________________________
    REPLACE
        long_expression____________________________________________________________
        replace_expression
    AT
        0
        1
        2
        long_index____________________________________________________________
        314159
    OUTPUT_VARIABLE
        long_output_variable_name____________________________________________________________
)
