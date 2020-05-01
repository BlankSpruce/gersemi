get_directory_property(FOO MACROS)

get_directory_property(FOO DIRECTORY bar MACROS)

get_directory_property(
    FOO
    DIRECTORY long_directory_name____________________
    MACROS
)

get_directory_property(
    FOO
    DIRECTORY
        even_longer_directory_name_________________________________________
    MACROS
)

get_directory_property(FOO DIRECTORY bar DEFINITION BAZ)

get_directory_property(
    FOO
    DIRECTORY long_directory_name____________________
    DEFINITION BAZ
)

get_directory_property(
    FOO
    DIRECTORY
        even_longer_directory_name_________________________________________
    DEFINITION BAZ
)

get_directory_property(
    FOO
    DIRECTORY bar
    DEFINITION long_variable_name____________________
)

get_directory_property(
    FOO
    DIRECTORY bar
    DEFINITION
        even_longer_variable_name_________________________________________
)

get_directory_property(
    FOO
    DIRECTORY
        very_long_directory_name___________________________________________
    DEFINITION
        very_long_variable_name____________________________________________
)

if(TRUE)
    get_directory_property(FOO DIRECTORY bar MACROS)

    get_directory_property(
        FOO
        DIRECTORY long_directory_name____________________
        DEFINITION BAZ
    )
endif()
