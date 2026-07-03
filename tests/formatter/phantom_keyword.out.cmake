set(MY_SOURCES #[[plain bracket comment]]
    c.h
    a.h
    d_____________________________________________.h
    c.h
    a.h
    b.h
    CACHE INTERNAL
    "Short docstring"
    FORCE
)

set(MY_SOURCES
    #[[gersemi: sort+unique]]
        a.h
        b.h
        c.h
        d_____________________________________________.h
    CACHE INTERNAL
    "Short docstring"
    FORCE
)

set(MY_SOURCES
    #[[gersemi: sort]]
        a.h
        a.h
        b.h
        c.h
        c.h
        d_____________________________________________.h
    CACHE INTERNAL
    "Short docstring"
    FORCE
)

set(MY_SOURCES
    #[[gersemi: unique]]
        c.h
        a.h
        d_____________________________________________.h
        b.h
    CACHE INTERNAL
    "Short docstring"
    FORCE
)

set(OppenheimerCast
    #[[gersemi: pairs]]
        "J. Robert Oppenheimer" "Cillian Murphy"
        "Kitty Oppenheimer" "Emily Blunt"
        "General Leslie Groves" "Matt Damon"
)

set(add_custom_command_COMMAND
    #[[gersemi: command_line]]
        clang-format -length=1000 -sort-includes -style=some_kind_of_style
        -verbose -output-replacements-xml
)

set(add_custom_command_COMMAND_2
    #[[gersemi: command_line]]
        clang-format #
        -length=1000 #
        -sort-includes #
        -style=some_kind_of_style #
        -verbose #
        -output-replacements-xml
)

set(multiple_phantom_comments
    #[[gersemi: sort+unique]]
        a.h
        b.h
        c.h
        d_____________________________________________.h
    #[[gersemi: pairs]]
        "J. Robert Oppenheimer" "Cillian Murphy"
        "Kitty Oppenheimer" "Emily Blunt"
        "General Leslie Groves" "Matt Damon"
    #[[gersemi: command_line]]
        clang-format #
        -length=1000 #
        -sort-includes #
        -style=some_kind_of_style #
        -verbose #
        -output-replacements-xml
    CACHE INTERNAL
    "Short docstring"
    FORCE
)

set(commented_phantom_keyword
    #[[gersemi: sort+unique]] # my line comment
        a.h
        b.h
        c.h
        d_____________________________________________.h
    #[[gersemi: pairs]] #[[my bracket comment]]
        "J. Robert Oppenheimer" "Cillian Murphy"
        "Kitty Oppenheimer" "Emily Blunt"
        "General Leslie Groves" "Matt Damon"
    CACHE INTERNAL
    "Short docstring"
    FORCE
)
