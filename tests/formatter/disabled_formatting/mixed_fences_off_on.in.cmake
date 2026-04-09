# This is formatted
set(FOO BAR)    

set(FOO    BAR   )   

set(    FOO    BAR   )

     set(FOO  BAR)   

# This isn't formatted
# fmt: off
set(FOO BAR)    

set(FOO    BAR   )   

set(    FOO    BAR   )

     set(FOO  BAR)   
# gersemi: on

# In blocks similarly
if(TRUE)
# This is formatted
set(FOO BAR)    

set(FOO    BAR   )   

set(    FOO    BAR   )

     set(FOO  BAR)   

# This isn't formatted
# cmake-format: off
set(FOO BAR)    

set(FOO    BAR   )   

set(    FOO    BAR   )

     set(FOO  BAR)   

# nested control block inside disabled formatting block
 if (TRUE)
 set(FOO    BAR)
 endif()

# fmt: on

# and in nested blocks
if(TRUE)
# gersemi: off
set(FOO BAR)    

set(FOO    BAR   )   

set(    FOO    BAR   )

     set(FOO  BAR)   
# cmake-format: on

set(FOO BAR)    

set(FOO    BAR   )   
# gersemi: on
set(    FOO    BAR   )

     set(FOO  BAR)   
endif()

endif()
