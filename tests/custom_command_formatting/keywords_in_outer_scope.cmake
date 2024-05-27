set(multiValueArgs SHICHIROJI KIKUCHIYO)
set(oneValueArgs GOROBEI HEIHACHI KYUZO)
set(options KAMBEI KATSUSHIRO)

function(Seven_Samurai some standalone arguments)
    cmake_parse_arguments(
        THIS_FUNCTION_PREFIX
        "${options}"
        "${oneValueArgs}"
        "${multiValueArgs}"
        ${ARGN}
    )
endfunction()
