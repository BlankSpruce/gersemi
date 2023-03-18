# Set normal variable
set(FOO item1)
set(FOO item1 item2)
set(FOO item1 item2 item3)
set(FOO item1 item2 item3 item4)
set(FOO
    item1
    item2
    item3
    item4
    item5
)

set(FOO "item1")
set(FOO "item1" "item2")
set(FOO "item1" "item2" "item3")
set(FOO "item1" "item2" "item3" "item4")
set(FOO
    "item1"
    "item2"
    "item3"
    "item4"
    "item5"
)

set(FOO [[item1]])
set(FOO [[item1]] [[item2]])
set(FOO [[item1]] [[item2]] [[item3]])
set(FOO [[item1]] [[item2]] [[item3]] [[item4]])
set(FOO
    [[item1]]
    [[item2]]
    [[item3]]
    [[item4]]
    [[item5]]
)

# Set empty variable
set(FOO)

# Set normal variable in parent scope
set(FOO item1 PARENT_SCOPE)
set(FOO item1 item2 PARENT_SCOPE)
set(FOO item1 item2 item3 PARENT_SCOPE)
set(FOO item1 item2 item3 item4 PARENT_SCOPE)
set(FOO
    item1
    item2
    item3
    item4
    item5
    PARENT_SCOPE
)

set(FOO "item1" PARENT_SCOPE)
set(FOO "item1" "item2" PARENT_SCOPE)
set(FOO "item1" "item2" "item3" PARENT_SCOPE)
set(FOO "item1" "item2" "item3" "item4" PARENT_SCOPE)
set(FOO
    "item1"
    "item2"
    "item3"
    "item4"
    "item5"
    PARENT_SCOPE
)

set(FOO [[item1]] PARENT_SCOPE)
set(FOO [[item1]] [[item2]] PARENT_SCOPE)
set(FOO [[item1]] [[item2]] [[item3]] PARENT_SCOPE)
set(FOO [[item1]] [[item2]] [[item3]] [[item4]] PARENT_SCOPE)
set(FOO
    [[item1]]
    [[item2]]
    [[item3]]
    [[item4]]
    [[item5]]
    PARENT_SCOPE
)

# Set empty variable in parent scope
set(FOO PARENT_SCOPE)

# Too big command to fit in one line
set(FOO
    "item1                                                                  "
)

# Set cache entry
# with short content
set(FOO ON CACHE BOOL "short docstring")
set(FOO somefile.ext CACHE FILEPATH "short docstring")
set(FOO somedir CACHE PATH "short docstring")
set(FOO "some string" CACHE STRING "short docstring")
set(FOO [[some internal]] CACHE INTERNAL "short docstring")

# with FORCE
set(FOO ON CACHE BOOL "short docstring" FORCE)
set(FOO somefile.ext CACHE FILEPATH "short docstring" FORCE)
set(FOO somedir CACHE PATH "short docstring" FORCE)
set(FOO "some string" CACHE STRING "short docstring" FORCE)
set(FOO [[some internal]] CACHE INTERNAL "short docstring" FORCE)

# with long content
set(FOO
    item1
    item2
    item3
    item4
    item5
    CACHE INTERNAL "short docstring"
)

# with long content and FORCE
set(FOO
    item1
    item2
    item3
    item4
    item5
    CACHE INTERNAL "short docstring" FORCE
)

# with long docstring
set(FOO
    item1
    CACHE
        INTERNAL
        "long                                                                                 docstring"
        FORCE
)

# with long content and long docstring
set(FOO
    item1
    item2
    item3
    item4
    item5
    CACHE
        INTERNAL
        "long                                                                                 docstring"
)

# with long content, long docstring and FORCE
set(FOO
    item1
    item2
    item3
    item4
    item5
    CACHE
        INTERNAL
        "long                                                                                 docstring"
        FORCE
)

# Set environment variable
# clear variable
set(ENV{FOO})

# set to something
set(ENV{FOO} bar)

# Set in block
if(TRUE)
    set(FOO
        "item1"
        "item2"
        "item3"
        "item4"
        "item5"
    )
endif()
