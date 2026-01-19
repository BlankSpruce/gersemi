set_directory_properties(PROPERTIES)

set_directory_properties(PROPERTIES prop1 value1)

set_directory_properties(PROPERTIES prop1 value1 prop2 value2)

set_directory_properties(
    PROPERTIES
        prop1 value1
        prop2 value2
        prop3 value3
)

set_directory_properties(
    PROPERTIES
        prop1 value1
        prop2 value2
        prop3 value3
        prop4 value4
)

set_directory_properties(
    PROPERTIES
        long_property_name_________ value1
        prop2 value2
        prop3 value3
)

set_directory_properties(
    PROPERTIES
        longer_property_name_______________________________________________________
            value1
        prop2 value2
        prop3 value3
)

set_directory_properties(
    PROPERTIES
        prop1 long_value__________________
        prop2 value2
        prop3 value3
)

set_directory_properties(
    PROPERTIES
        prop1
            longer_value_____________________________________________________________
        prop2 value2
        prop3 value3
)

set_directory_properties(
    PROPERTIES
        long_property_name_________ long_value__________________
        prop2 value2
        prop3 value3
)

set_directory_properties(
    PROPERTIES
        longer_property_name_______________________________________________________
            longer_value_____________________________________________________________
        prop2 value2
        prop3 value3
)

if(TRUE)
    set_directory_properties(PROPERTIES prop1 value1)

    set_directory_properties(
        PROPERTIES
            prop1 value1
            prop2 value2
            prop3 value3
            prop4 value4
    )
endif()
