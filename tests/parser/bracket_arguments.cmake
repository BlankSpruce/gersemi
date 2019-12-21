message(first [=[single line bracket argument]=] third)
message(first [=[multi
line bracket
argument]=] third)

# Some other symbol than = after one of inner ]
foo(bar [[baz [0-9]+]])

# Multiple = but not matching number
foo([====[some content
    with too few equal signs ]] ]=] ]==] ]===]] and
    too many ]=====] ]======] ]=======] and
    incomplete ]==== bracket_close ]====])
    
foo(bar [=====[some content with ]==== ]=====])


# Taken from CMake documentation
message([=[
This is the first line in a bracket argument with bracket length 1.
No \-escape sequences or ${variable} references are evaluated.
This is always one argument even though it contains a ; character.
The text does not end on a closing bracket of length 0 like ]].
It does end in a closing bracket of length 1.
]=])
