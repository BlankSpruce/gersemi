function(back_to_the_future_part_ii first_argument second_argument)
set(oneValueArgs OLDER_MARTY_MCFLY YOUNGER_MARTY_MCFLY)
set(multiValueArgs EMMETT_DOC_BROWN BIFF_TANNEN)

cmake_parse_arguments(
back_to_the_future_part_ii_PREFIX
""
"${oneValueArgs}"
"${multiValueArgs}"
${ARGN}
)
endfunction()

function(back_to_the_future_part_iii first_argument second_argument third_arg)
set(options MAD_DOG)
set(oneValueArgs DOC_BROWN DELOREAN MARTY)
set(multiValueArgs CLARA_CLAYTON FLUX_CAPACITOR)

cmake_parse_arguments(
back_to_the_future_PREFIX
"${options}"
"${oneValueArgs}"
"${multiValueArgs}"
${ARGN}
)
endfunction()
