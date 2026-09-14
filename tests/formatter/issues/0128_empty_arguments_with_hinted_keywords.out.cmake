function(movie_description_with_hints)
    # gersemi: hints { PAIRS: pairs, COMMAND_LINE: command_line }
    set(options "")
    set(oneValueArgs)
    set(multiValueArgs PAIRS COMMAND_LINE)

    cmake_parse_arguments(
        THIS_FUNCTION_PREFIX
        "${options}"
        "${oneValueArgs}"
        "${multiValueArgs}"
        ${ARGN}
    )
endfunction()

movie_description_with_hints(
    "Empty key in pair"
    PAIRS
        "ok" "ok_______________________________________________________________"
        "" "not_ok_____________________________________________________________"
        [[ok]] [[ok___________________________________________________________]]
        [[]] [[not_ok_________________________________________________________]]
    COMMAND_LINE ""
)

movie_description_with_hints(
    "Empty value in pair"
    PAIRS
        "ok_______________________________________________________________" "ok"
        "not_ok_____________________________________________________________" ""
        [[ok___________________________________________________________]] [[ok]]
        [[not_ok_________________________________________________________]] [[]]
    COMMAND_LINE [[]]
)

movie_description_with_hints(
    "Empty key and empty value in pair"
    PAIRS
        "ok_______________________________________________________________" "ok"
        "" ""
        [[ok___________________________________________________________]] [[ok]]
        [[]] [[]]
    COMMAND_LINE [[]] ""
)
