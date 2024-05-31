add_custom_target( foobar ${CMAKE_COMMAND} -E env FOO=bar dostuff COMMAND ${CMAKE_COMMAND} -E env BAR=foo stuffdo DEPENDS foo bar )

add_custom_target( foobar ALL ${CMAKE_COMMAND} -E env FOO=bar dostuff COMMAND ${CMAKE_COMMAND} -E env BAR=foo stuffdo DEPENDS foo bar )
