function(poem)
    cmake_parse_arguments("ARG" "" "" "LINES" ${ARGN})
    message(FATAL_ERROR ${ARG_LINES})
endfunction()
