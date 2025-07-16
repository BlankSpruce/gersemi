block()
endblock()

block(SCOPE_FOR POLICIES)
endblock()

block(SCOPE_FOR VARIABLES)
endblock()

block(SCOPE_FOR POLICIES PROPAGATE FOO)
endblock()

block(SCOPE_FOR VARIABLES PROPAGATE FOO)
endblock()

block(
    SCOPE_FOR POLICIES
    PROPAGATE
        FOO
        BAR
        BAZ
        LONG_NAME____________________________________________________________
)
endblock()

block(
    SCOPE_FOR VARIABLES
    PROPAGATE
        FOO
        BAR
        BAZ
        LONG_NAME____________________________________________________________
)
endblock()

block()
    set(FOO "FOO")
endblock()

block(SCOPE_FOR POLICIES)
    set(FOO "FOO")
endblock()

block(SCOPE_FOR VARIABLES PROPAGATE FOO)
    set(FOO "FOO")
endblock()

block(
    SCOPE_FOR VARIABLES
    PROPAGATE
        FOO
        BAR
        BAZ
        LONG_NAME____________________________________________________________
)
    set(FOO "FOO")
endblock()

block(SCOPE_FOR VARIABLES PROPAGATE FOO)
    block(SCOPE_FOR VARIABLES PROPAGATE FOO)
        block(SCOPE_FOR VARIABLES PROPAGATE FOO)
            set(FOO "FOO")
        endblock()
    endblock()
endblock()

block(
    SCOPE_FOR VARIABLES
    PROPAGATE
        FOO
        BAR
        BAZ
        LONG_NAME____________________________________________________________
)
    block(SCOPE_FOR VARIABLES PROPAGATE FOO)
        block(SCOPE_FOR VARIABLES PROPAGATE FOO)
            set(FOO "FOO")
        endblock()
    endblock()
endblock()

block(
    SCOPE_FOR VARIABLES
    PROPAGATE
        FOO
        BAR
        BAZ
        LONG_NAME____________________________________________________________
)
    block(
        SCOPE_FOR VARIABLES
        PROPAGATE
            FOO
            BAR
            BAZ
            LONG_NAME____________________________________________________________
    )
        block(
            SCOPE_FOR VARIABLES
            PROPAGATE
                FOO
                BAR
                BAZ
                LONG_NAME____________________________________________________________
        )
            set(FOO "FOO")
        endblock()
    endblock()
endblock()
