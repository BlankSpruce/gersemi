function(SEVEN_SAMURAI some standalone arguments)
    # first comment
    set(options KAMBEI KATSUSHIRO)
    # another comment
    set(oneValueArgs GOROBEI HEIHACHI KYUZO) # yet another comment

    #[[more comments]]
    set(multiValueArgs SHICHIROJI KIKUCHIYO)

    cmake_parse_arguments(
        THIS_FUNCTION_PREFIX
        "${options}"
        "${oneValueArgs}"
        "${multiValueArgs}"
        ${ARGN}
    )
endfunction()
