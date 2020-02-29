set(captain JACK_SPARROW)

macro(the_curse_of_the_black_pearl one two three)
set(options ${captain} BARBOSSA)
set(oneValueArgs WILL_TURNER ELIZABETH_SWANN)
set(multiValueArgs NORRINGTON GOVERNOR_SWANN GIBBS)

cmake_parse_arguments(the_curse_of_the_black_pearl_prefix "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})
endmacro()

the_curse_of_the_black_pearl(JACK_SPARROW BARBOSSA WILL_TURNER foo ELIZABETH_SWANN bar NORRINGTON foo bar baz GOVERNOR_SWANN foo__________________________________________________ bar__________________________________________________ baz__________________________________________________ GIBBS foo bar "baz                                                  ")

function(dead_mans_chest one two three)
set(captain DAVY_JONES)
set(options WILL_TURNER ELIZABETH_SWANN BOOTSTRAP_BILL_TURNER)
set(oneValueArgs LORD_BECKETT JAMES_NORRINGTON)
set(multiValueArgs CAPTAIN_JACK_SPARROW ${captain})

cmake_parse_arguments(dead_mans_chest_prefix "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})
endfunction()

dead_mans_chest(WILL_TURNER ELIZABETH_SWANN BOOTSTRAP_BILL_TURNER LORD_BECKETT foo JAMES_NORRINGTON bar CAPTAIN_JACK_SPARROW foo__________________________________________________ bar__________________________________________________ baz__________________________________________________ DAVY_JONES foo bar baz)

macro(at_worlds_end one two three)
set(options JOSHAMEE_GIBBS)
set(oneValueArgs DAVY_JONES BECKETT)
set(multiValueArgs ${captain} BARBOSSA WILL_TURNER ELIZABETH_SWANN)

cmake_parse_arguments(at_worlds_end_prefix "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})
endmacro()

at_worlds_end(JOSHAMEE_GIBBS DAVY_JONES foo BECKETT "foo                                                                                 " JACK_SPARROW foo bar baz WILL_TURNER foo [[bar                                                            ]] baz ELIZABETH_SWANN foo bar baz)

the_curse_of_the_black_pearl(JACK_SPARROW BARBOSSA WILL_TURNER foo ELIZABETH_SWANN bar NORRINGTON foo bar baz GOVERNOR_SWANN foo__________________________________________________ bar__________________________________________________ baz__________________________________________________ GIBBS foo bar "baz                                                  ")

dead_mans_chest( WILL_TURNER ELIZABETH_SWANN BOOTSTRAP_BILL_TURNER LORD_BECKETT foo JAMES_NORRINGTON bar CAPTAIN_JACK_SPARROW foo__________________________________________________ bar__________________________________________________ baz__________________________________________________ DAVY_JONES foo bar baz)

at_worlds_end( JOSHAMEE_GIBBS DAVY_JONES foo BECKETT "foo                                                                                 " JACK_SPARROW foo bar baz WILL_TURNER foo [[bar                                                            ]] baz ELIZABETH_SWANN foo bar baz)
