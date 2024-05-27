function(Seven_Samurai some standalone arguments)
    cmake_parse_arguments(
        THIS_FUNCTION_PREFIX
        "KAMBEI;KATSUSHIRO"
        "GOROBEI;HEIHACHI;KYUZO"
        "SHICHIROJI;KIKUCHIYO"
        ${ARGN}
    )
endfunction()
