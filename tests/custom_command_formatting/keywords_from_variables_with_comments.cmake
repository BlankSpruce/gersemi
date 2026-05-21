function(Seven_Samurai some standalone arguments)
    set(options
        KAMBEI
        KATSUSHIRO # foobar
    )
    set(oneValueArgs
        GOROBEI # foobar
        HEIHACHI # foobar
        KYUZO
    )
    set(multiValueArgs # foobar
        SHICHIROJI # foobar
        KIKUCHIYO # foobar
    )

    cmake_parse_arguments(
        THIS_FUNCTION_PREFIX
        "${options}"
        "${oneValueArgs}"
        "${multiValueArgs}"
        ${ARGN}
    )
endfunction()
