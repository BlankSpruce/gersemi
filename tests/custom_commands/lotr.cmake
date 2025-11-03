function(the_hobbit)
    set(options)
    set(oneValueArgs BURGLAR WIZARD)
    set(multiValueArgs DWARVES)

    cmake_parse_arguments(
        THIS_FUNCTION_PREFIX
        "${options}"
        "${oneValueArgs}"
        "${multiValueArgs}"
        ${ARGN}
    )
endfunction()

function(the_fellowship_of_the_ring)
    set(options)
    set(oneValueArgs RING_BEARER GARDENER)
    set(multiValueArgs)

    cmake_parse_arguments(
        THIS_FUNCTION_PREFIX
        "${options}"
        "${oneValueArgs}"
        "${multiValueArgs}"
        ${ARGN}
    )
endfunction()

function(the_two_towers)
    set(options)
    set(oneValueArgs RING_BEARER GARDENER)
    set(multiValueArgs)

    cmake_parse_arguments(
        THIS_FUNCTION_PREFIX
        "${options}"
        "${oneValueArgs}"
        "${multiValueArgs}"
        ${ARGN}
    )
endfunction()

function(step_one_have_a_good_scenario)
endfunction()

function(step_two_make_the_movie)
endfunction()
