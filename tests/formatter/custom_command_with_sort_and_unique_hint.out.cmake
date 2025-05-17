function(my_custom_function target_name)
    # gersemi: hints { SOURCES_JUST_SORTED: sort, SOURCES_JUST_UNIQUE: unique, SOURCES: sort+unique }
    set(options "")
    set(oneValueArgs KIND)
    set(multiValueArgs
        SOURCES_JUST_SORTED
        SOURCES_JUST_UNIQUE
        SOURCES
        PROPERTIES
    )

    cmake_parse_arguments(
        THIS_FUNCTION_PREFIX
        "${options}"
        "${oneValueArgs}"
        "${multiValueArgs}"
        ${ARGN}
    )
endfunction()

my_custom_function(
    example
    KIND foo
    SOURCES_JUST_SORTED
        a.cpp
        a.cpp
        b.cpp
        b.cpp
        c.cpp
        c.cpp
        c.cpp
    SOURCES_JUST_UNIQUE
        c.cpp
        a.cpp
        b.cpp
    SOURCES
        a.cpp
        b.cpp
        c.cpp
    PROPERTIES
        foo
        bar
        baz
)
