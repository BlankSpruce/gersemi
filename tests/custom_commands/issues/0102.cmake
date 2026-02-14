function(issue0102)
    # gersemi: hints { SORT_ME: sort }
    set(options)
    set(single)
    set(multi SORT_ME)
    cmake_parse_arguments(_ "${options}" "${single}" "${multi}" ${ARGN})
endfunction()
