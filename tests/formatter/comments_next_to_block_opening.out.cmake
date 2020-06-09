if(TRUE) # FOOBAR
    message(STATUS FOO)
endif()

while(TRUE) # FOOBAR
    message(STATUS FOO)
endwhile()

function(TRUE) # FOOBAR
    message(STATUS FOO)
endfunction()

macro(TRUE) # FOOBAR
    message(STATUS FOO)
endmacro()

foreach(TRUE) # FOOBAR
    message(STATUS FOO)
endforeach()
