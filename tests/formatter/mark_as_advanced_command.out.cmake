mark_as_advanced(FOO)

mark_as_advanced(CLEAR FOO)

mark_as_advanced(FORCE FOO)

mark_as_advanced(
    long_variable_name_________________________________________________
)

mark_as_advanced(
    CLEAR
    long_variable_name_________________________________________________
)

mark_as_advanced(
    FORCE
    long_variable_name_________________________________________________
)

if(TRUE)
    mark_as_advanced(FOO)

    mark_as_advanced(
        FORCE
        long_variable_name_________________________________________________
    )
endif()
