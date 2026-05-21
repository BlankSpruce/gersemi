function(Seven_Samurai some standalone arguments)
    cmake_parse_arguments(
        PARSE_ARGV
        3
        parsed
        "KAMBEI;KATSUSHIRO" # options
        "GOROBEI;HEIHACHI;KYUZO" # one-value arguments
        "SHICHIROJI;KIKUCHIYO" # multi-value arguments
    )
endfunction()
