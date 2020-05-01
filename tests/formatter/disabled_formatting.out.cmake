# This is formatted
set(FOO BAR)

set(FOO BAR)

set(FOO BAR)

set(FOO BAR)

# This isn't formatted
# gersemi: off
set(FOO BAR)    

set(FOO    BAR   )   

set(    FOO    BAR   )

     set(FOO  BAR)   
# gersemi: on

# In blocks similarly
if(TRUE)
    # This is formatted
    set(FOO BAR)

    set(FOO BAR)

    set(FOO BAR)

    set(FOO BAR)

    # This isn't formatted
    # gersemi: off
set(FOO BAR)    

set(FOO    BAR   )   

set(    FOO    BAR   )

     set(FOO  BAR)   

# nested control block inside disabled formatting block
 if (TRUE)
 set(FOO    BAR)
 endif()

    # gersemi: on

    # and in nested blocks
    if(TRUE)
        # gersemi: off
set(FOO BAR)    

set(FOO    BAR   )   

set(    FOO    BAR   )

     set(FOO  BAR)   
        # gersemi: on

        set(FOO BAR)

        set(FOO BAR)

        set(FOO BAR)

        set(FOO BAR)
    endif()
endif()
