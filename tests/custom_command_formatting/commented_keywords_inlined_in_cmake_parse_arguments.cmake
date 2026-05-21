function(Seven_Samurai some standalone arguments)
    cmake_parse_arguments(
        THIS_FUNCTION_PREFIX
        "KAMBEI;KATSUSHIRO" # options
        "GOROBEI;HEIHACHI;KYUZO" # one-value arguments
        "SHICHIROJI;KIKUCHIYO" # multi-value arguments
        ${ARGN}
    )
endfunction()
