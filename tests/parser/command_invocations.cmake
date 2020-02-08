# Taken from CMake documentation
add_executable(hello world.c)

if(FALSE AND (FALSE OR TRUE)) # evaluates to FALSE
endif()
