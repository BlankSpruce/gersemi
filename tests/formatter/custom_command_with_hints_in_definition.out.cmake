function(movie_description_without_hints)
    set(options "")
    set(oneValueArgs DIRECTOR)
    set(multiValueArgs CAST SUMMARY)

    cmake_parse_arguments(
        THIS_FUNCTION_PREFIX
        "${options}"
        "${oneValueArgs}"
        "${multiValueArgs}"
        ${ARGN}
    )
endfunction()

function(movie_description_with_empty_hints)
    # gersemi: hints
    set(options "")
    set(oneValueArgs DIRECTOR)
    set(multiValueArgs CAST SUMMARY)

    cmake_parse_arguments(
        THIS_FUNCTION_PREFIX
        "${options}"
        "${oneValueArgs}"
        "${multiValueArgs}"
        ${ARGN}
    )
endfunction()

function(movie_description_with_unsupported_hints)
    # gersemi: hints { CAST: hello_there, SUMMARY: hi }
    set(options "")
    set(oneValueArgs DIRECTOR)
    set(multiValueArgs CAST SUMMARY)

    cmake_parse_arguments(
        THIS_FUNCTION_PREFIX
        "${options}"
        "${oneValueArgs}"
        "${multiValueArgs}"
        ${ARGN}
    )
endfunction()

function(movie_description_with_unsupported_keywords_in_hints)
    # gersemi: hints { PUBLISHER: pairs }
    set(options "")
    set(oneValueArgs DIRECTOR)
    set(multiValueArgs CAST SUMMARY)

    cmake_parse_arguments(
        THIS_FUNCTION_PREFIX
        "${options}"
        "${oneValueArgs}"
        "${multiValueArgs}"
        ${ARGN}
    )
endfunction()

function(movie_description_with_hints)
    # gersemi: hints { SUMMARY: command_line, CAST: pairs }
    set(options "")
    set(oneValueArgs DIRECTOR)
    set(multiValueArgs CAST SUMMARY)

    cmake_parse_arguments(
        THIS_FUNCTION_PREFIX
        "${options}"
        "${oneValueArgs}"
        "${multiValueArgs}"
        ${ARGN}
    )
endfunction()

movie_description_without_hints(
    Oppenheimer
    DIRECTOR "Christopher Nolan"
    CAST
        "J. Robert Oppenheimer"
        "Cillian Murphy"
        "Kitty Oppenheimer"
        "Emily Blunt"
        "General Leslie Groves"
        "Matt Damon"
    SUMMARY
        Oppenheimer
        is
        an
        epic
        biographical
        thriller
        directed
        by
        Christopher
        Nolan.
)

movie_description_with_empty_hints(
    Oppenheimer
    DIRECTOR "Christopher Nolan"
    CAST
        "J. Robert Oppenheimer"
        "Cillian Murphy"
        "Kitty Oppenheimer"
        "Emily Blunt"
        "General Leslie Groves"
        "Matt Damon"
    SUMMARY
        Oppenheimer
        is
        an
        epic
        biographical
        thriller
        directed
        by
        Christopher
        Nolan.
)

movie_description_with_unsupported_hints(
    Oppenheimer
    DIRECTOR "Christopher Nolan"
    CAST
        "J. Robert Oppenheimer"
        "Cillian Murphy"
        "Kitty Oppenheimer"
        "Emily Blunt"
        "General Leslie Groves"
        "Matt Damon"
    SUMMARY
        Oppenheimer
        is
        an
        epic
        biographical
        thriller
        directed
        by
        Christopher
        Nolan.
)

movie_description_with_unsupported_keywords_in_hints(
    Oppenheimer
    DIRECTOR "Christopher Nolan"
    CAST
        "J. Robert Oppenheimer"
        "Cillian Murphy"
        "Kitty Oppenheimer"
        "Emily Blunt"
        "General Leslie Groves"
        "Matt Damon"
    SUMMARY
        Oppenheimer
        is
        an
        epic
        biographical
        thriller
        directed
        by
        Christopher
        Nolan.
)

movie_description_with_hints(
    Oppenheimer
    DIRECTOR "Christopher Nolan"
    CAST
        "J. Robert Oppenheimer" "Cillian Murphy"
        "Kitty Oppenheimer" "Emily Blunt"
        "General Leslie Groves" "Matt Damon"
    SUMMARY
        Oppenheimer is an epic biographical thriller directed by Christopher
        Nolan.
)
