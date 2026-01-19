function(begin_target arg)
    # gersemi: block_end end_target
endfunction()

function(end_target)
endfunction()

function(require arg)
endfunction()

function(prologue)
    # gersemi: block_end epilogue
    # gersemi: hints { CHARACTERS: pairs, DESCRIPTION: command_line }
    set(options "")
    set(oneValueArgs)
    set(multiValueArgs CHARACTERS DESCRIPTION)

    cmake_parse_arguments(
        THIS_FUNCTION_PREFIX
        "${options}"
        "${oneValueArgs}"
        "${multiValueArgs}"
        ${ARGN}
    )
endfunction()

function(epilogue)
    # gersemi: hints { CHARACTERS: pairs, DESCRIPTION: command_line }
    set(options "")
    set(oneValueArgs)
    set(multiValueArgs CHARACTERS DESCRIPTION)

    cmake_parse_arguments(
        THIS_FUNCTION_PREFIX
        "${options}"
        "${oneValueArgs}"
        "${multiValueArgs}"
        ${ARGN}
    )
endfunction()

function(block_with_missing_end_function_definition)
    # gersemi: block_end foobar
endfunction()

# simple
begin_target(EXE)
    require("thirdparty_lib")
    require("my_lib")
    require(
        "very_long______________________________________________________________________name"
    )
end_target()
require("foobar")

# nested
begin_target(EXE)
    begin_target(EXE)
        require("thirdparty_lib")
        require("my_lib")
        require(
            "very_long______________________________________________________________________name"
        )
    end_target()
    require("foobar")
end_target()
require("foobar")

# with keywords
prologue(
    CHARACTERS
        "Bilbo Baggins" "Hobbit"
        "Gandalf" "Wizard_____________________________________________"
    DESCRIPTION
        Certain wizard visits a hobbit
)
    require("thirdparty_lib")
    require("my_lib")
    require(
        "very_long______________________________________________________________________name"
    )
epilogue(
    CHARACTERS
        "Bilbo Baggins" "Hobbit"
        "Gandalf" "Wizard_____________________________________________"
    DESCRIPTION
        Certain wizard visits a hobbit
)
require("foobar")

# mixed
prologue(
    CHARACTERS
        "Bilbo Baggins" "Hobbit"
        "Gandalf" "Wizard_____________________________________________"
    DESCRIPTION
        Certain wizard visits a hobbit
)
    begin_target(EXE)
        require("thirdparty_lib")
        require("my_lib")
        require(
            "very_long______________________________________________________________________name"
        )
    end_target()
    require("foobar")
epilogue(
    CHARACTERS
        "Bilbo Baggins" "Hobbit"
        "Gandalf" "Wizard_____________________________________________"
        "Balin" "The dwarf"
    DESCRIPTION
        Certain wizard and certain dwarf visit a friend
)
require("foobar")

# with ending that lacks definition
block_with_missing_end_function_definition(EXE)
    require("thirdparty_lib")
    require("my_lib")
    require(
        "very_long______________________________________________________________________name"
    )
foobar()
require("foobar")
