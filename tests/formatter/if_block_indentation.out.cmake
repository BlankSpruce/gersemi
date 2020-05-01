if(TRUE)
    message(STATUS "bar")
endif()

# nested if statement
if(TRUE)
    message(STATUS "foo")
    # empty lines don't introduce superfluous spaces

    # comment also gets indented
    if(TRUE)
        # and here
        message(STATUS "bar")
        # and there
    endif()
endif()

if(FALSE)
    # some comment
    message(STATUS "foo")
    # another comment
elseif(FALSE)
    message(STATUS "bar")
elseif(TRUE)
    if(TRUE)
        # comment in nested scope
        message(STATUS "baz")
    else()
        message(STATUS "BAZ")
        # another comment in nested scope
    endif()
elseif(FALSE)
    message(STATUS "foo")
else()
    message(STATUS "bar")
endif()
