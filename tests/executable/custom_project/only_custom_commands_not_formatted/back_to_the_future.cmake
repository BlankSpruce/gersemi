function(back_to_the_future first_argument)
    set(options DELOREAN)
    set(oneValueArgs FLUX_CAPACITOR)
    set(multiValueArgs EMMETT_BROWN MARTY_MCFLY)

    cmake_parse_arguments(
        back_to_the_future_PREFIX
        "${options}"
        "${oneValueArgs}"
        "${multiValueArgs}"
        ${ARGN}
    )
endfunction()
