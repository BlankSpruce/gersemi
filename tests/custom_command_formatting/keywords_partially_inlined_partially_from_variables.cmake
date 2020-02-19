function(SEVEN_SAMURAI some standalone arguments)
    set(options KAMBEI)
    set(oneValueArgs KYUZO)
    set(multiValueArgs SHICHIROJI KIKUCHIYO)

    cmake_parse_arguments(
        THIS_FUNCTION_PREFIX
        "KATSUSHIRO;${options}"
        "${oneValueArgs};GOROBEI;HEIHACHI"
        "${multiValueArgs}"
        ${ARGN}
    )
endfunction()
