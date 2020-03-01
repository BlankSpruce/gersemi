function(SEVEN_SAMURAI some standalone arguments)
    set(options KAMBEI KATSUSHIRO)
    set(oneValueArgs GOROBEI HEIHACHI KYUZO)
    set(multiValueArgs SHICHIROJI KIKUCHIYO)

    message(STATUS "ABC")

    cmake_parse_arguments(
        THIS_FUNCTION_PREFIX
        "${options}"
        "${oneValueArgs}"
        "${multiValueArgs}"
        ${ARGN}
    )

    message(STATUS "DEF")
endfunction()
