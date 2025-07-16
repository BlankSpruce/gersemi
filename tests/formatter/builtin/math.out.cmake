math(EXPR FOO "2 + 2")

math(EXPR FOO "2 + 2" OUTPUT_FORMAT DECIMAL)

math(EXPR FOO "2 + 2" OUTPUT_FORMAT HEXADECIMAL)

math(
    EXPR
    FOO
    "long expression                        "
    OUTPUT_FORMAT HEXADECIMAL
)

math(
    EXPR
    FOO
    "longer expression                                                         "
)

math(
    EXPR
    FOO
    "longer expression                                                         "
    OUTPUT_FORMAT DECIMAL
)

math(
    EXPR
    long_variable_name________________________________________________________
    "2 + 2"
)

math(
    EXPR
    long_variable_name________________________________________________________
    "2 + 2"
    OUTPUT_FORMAT DECIMAL
)

math(
    EXPR
    long_variable_name________________________________________________________
    "long expression                                                         "
)

math(
    EXPR
    long_variable_name________________________________________________________
    "long expression                                                         "
    OUTPUT_FORMAT DECIMAL
)

if(TRUE)
    math(EXPR FOO "2 + 2" OUTPUT_FORMAT HEXADECIMAL)

    math(
        EXPR
        FOO
        "longer expression                                                         "
        OUTPUT_FORMAT DECIMAL
    )
endif()
