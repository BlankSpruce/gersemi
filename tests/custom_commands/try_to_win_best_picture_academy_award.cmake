function(try_to_win_best_picture_academy_award title alternative_title)
    set(options FOREIGN_LANGUAGE)
    set(oneValueArgs GENRE YEAR)
    set(multiValueArgs DIRECTORS CAST)

    cmake_parse_arguments(
        THIS_FUNCTION_PREFIX
        "${options}"
        "${oneValueArgs}"
        "${multiValueArgs}"
        ${ARGN}
    )
endfunction()
