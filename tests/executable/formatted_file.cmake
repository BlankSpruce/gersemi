project(FOO BAR)

set(FOO BAR BAZ)

if(
    TRUE
    OR TRUE
    OR TARGET FOOBAR__________________________________________________
)
    message(STATUS "FOOBAR")
endif()
