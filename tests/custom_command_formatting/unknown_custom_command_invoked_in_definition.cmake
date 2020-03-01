function(SEVEN_SAMURAI some standalone arguments)
    set(options KAMBEI KATSUSHIRO)
    set(oneValueArgs GOROBEI HEIHACHI KYUZO)
    set(multiValueArgs SHICHIROJI KIKUCHIYO)

    some_unknown_custom_command(ONE TWO THREE "FOUR" [[FIVE]] ${SIX})

    cmake_parse_arguments(
        THIS_FUNCTION_PREFIX
        "${options}"
        "${oneValueArgs}"
        "${multiValueArgs}"
        ${ARGN}
    )

    another_unknown_custom_command(ONE "TWO" [[THREE]])
endfunction()
