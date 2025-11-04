if(TRUE)
set(FOO bar)
    set(FOO bar)
        set(FOO bar)
            set(FOO bar)
                set(FOO bar)
                    set(FOO bar)
                        set(FOO bar)
# formatted below
    project(FOO BAR)

    set(FOO BAR BAZ)

    if(
        TRUE
        OR TRUE
        OR TARGET FOOBAR__________________________________________________
    )
        message(STATUS "FOOBAR")
    endif()

# formatted above
set(FOO bar)
    set(FOO bar)
        set(FOO bar)
            set(FOO bar)
                set(FOO bar)
                    set(FOO bar)
                        set(FOO bar)
endif()
