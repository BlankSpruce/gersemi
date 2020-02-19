function(SEVEN_SAMURAI some standalone arguments)
    set(options KAMBEI KATSUSHIRO)
    set(oneValueArgs GOROBEI HEIHACHI KYUZO)
    set(multiValueArgs SHICHIROJI KIKUCHIYO)

    cmake_parse_arguments(
        PARSE_ARGV
        3
        THIS_FUNCTION_PREFIX
        "${options}"
        "${oneValueArgs}"
        "${multiValueArgs}"
    )
endfunction()
