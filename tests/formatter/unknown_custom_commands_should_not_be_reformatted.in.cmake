# custom commands shouldn't have their original formatting changed
some_custom_command(in   one    line)

some_custom_command(FOO
    BAR
        Baz
    FOO
        bar bAZ
    [[some bracket
multiline \- argument ]=]
which shouldn't [===[ have
its content changed]]
    "some quoted
multiline argument \
which \" shouldn't have
its \\-content changed"
    )

# except for indentation inside blocks
if(TRUE)
some_custom_command(in   one    line)

some_custom_command(FOO
    BAR
        Baz
    FOO
        bar bAZ
    [[some bracket
multiline \- argument ]=]
which shouldn't [===[ have
its content changed]]
    "some quoted
multiline argument \
which \" shouldn't have
its \\-content changed"
    )
endif()

if(TRUE)
if(TRUE)
some_custom_command(in   one    line)

some_custom_command(FOO
    BAR
        Baz
    FOO
        bar bAZ
    [[some bracket
multiline \- argument ]=]
which shouldn't [===[ have
its content changed]]
    "some quoted
multiline argument \
which \" shouldn't have
its \\-content changed"
    )
endif()
endif()

# command name will still get downcased and parentheses will get properly aligned
SOME_custom_COMMAND(in   one    line)

SOME_custom_COMMAND(FOO
    BAR
        Baz
    FOO
        bar bAZ
    [[some bracket
multiline \- argument ]=]
which shouldn't [===[ have
its content changed]]
    "some quoted
multiline argument \
which \" shouldn't have
its \\-content changed"
          )

if(TRUE)
# command name will still get downcased and parentheses will get properly aligned
SOME_custom_COMMAND(in   one    line)

SOME_custom_COMMAND(FOO
    BAR
        Baz
    FOO
        bar bAZ
    [[some bracket
multiline \- argument ]=]
which shouldn't [===[ have
its content changed]]
    "some quoted
multiline argument \
which \" shouldn't have
its \\-content changed"
          )
endif()