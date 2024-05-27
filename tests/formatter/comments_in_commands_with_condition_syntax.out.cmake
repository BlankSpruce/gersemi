if(
    FOO STREQUAL "bar"
    OR
    # line comment
    FOO STREQUAL "baz"
)
endif()

if(
    FOO STREQUAL "bar"
    OR
    # line comment
    # with
    # multiple lines
    FOO STREQUAL "baz"
)
endif()

if(
    FOO STREQUAL "bar"
    OR
    # line comment
    # with
    # multiple lines
    FOO STREQUAL "baz"
)
endif()

if(
    FOO STREQUAL "bar"
    OR
    #[ bracket comment ]
    FOO STREQUAL "baz"
)
endif()

if(
    FOO STREQUAL "bar"
    OR
    #[[ bracket comment
      with
      multiple lines ]]
    FOO STREQUAL "baz"
)
endif()

if(
    FOO STREQUAL "bar"
    OR
    #[[ bracket comment
      with
      multiple lines ]]
    FOO STREQUAL "baz"
)
endif()
