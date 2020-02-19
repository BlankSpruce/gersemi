set(multiValueArgs SHICHIROJI KIKUCHIYO)
set(oneValueArgs GOROBEI HEIHACHI KYUZO)
set(options KAMBEI KATSUSHIRO)

function(SEVEN_SAMURAI some standalone arguments)
    cmake_parse_arguments(
        THIS_FUNCTION_PREFIX
        "${options}"
        "${oneValueArgs}"
        "${multiValueArgs}"
        ${ARGN}
    )
endfunction()
