function(foo)
    cmake_parse_arguments("ARG" "ONE" "TWO" "THREE" ${ARGN})
endfunction()
