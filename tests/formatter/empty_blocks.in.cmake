if(TRUE)
endif()

if(TRUE)
else()
foo()
endif()

if(TRUE)
foo()
else()
endif()

if(FALSE)
elseif(TRUE)
else()
foo()
endif()

if(FALSE)
elseif(TRUE)
foo()
else()
endif()

if(FALSE)
foo()
elseif(TRUE)
else()
endif()

if(FALSE)
elseif(TRUE)
elseif(TRUE)
elseif(TRUE)
else()
endif()

foreach(i arg1)
endforeach()

while(TRUE)
endwhile()

macro(FOO)
endmacro()

function(FOO)
endfunction()