message(long_argument very_long_argument very_very_long_argument very_very_long_argument argument yet_another_argument very_very_long_argument line_limit_long_________________________________________________________argument argument)

message(line_limit_long_________________________________________________________argument argument_longer_than___________________________________________________line_limit argument)

message(unquoted_argument long_unquoted__________________________________argument unquoted_argument "quoted_argument" "long unquoted                                        argument" "quoted argument" [[bracket argument]] [[long bracket                  argument]] [[bracket argument]])

message(some_very_long_______________________________argument) # Long comment next to command invocation

# Line limits inside indented blocks
if(TRUE)
    message(long_argument very_long_argument very_very_long_argument very_very_long_argument argument yet_another_argument very_very_long_argument line_limit_long_________________________________________________________argument argument)

    message(line_limit_long_____________________________________________________argument ab argument_longer_than_______________________________________________line_limit a)

    message(unquoted_argument long_unquoted__________________________________argument unquoted_argument "quoted_argument" "long unquoted                                        argument" "quoted argument" [[bracket argument]] [[long bracket                  argument]] [[bracket argument]])

    message(some_very_long___________________________argument) # Long comment next to command invocation
endif()

if(TRUE)
    if(TRUE)
        message(long_argument very_long_argument very_very_long_argument very_very_long_argument argument yet_another_argument very_very_long_argument line_limit_long_________________________________________________________argument argument)

        message(line_limit_long_________________________________________________argument abcdef argument_longer_than___________________________________________line_limit abcde)

        message(unquoted_argument long_unquoted__________________________argument unquoted_argument "quoted_argument" "long unquoted                                        argument" "quoted argument" [[bracket argument]] [[long bracket                  argument]] [[bracket argument]])

        message(some_very_long_______________________argument) # Long comment next to command invocation
    endif()
endif()