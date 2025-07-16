# top-level comment                                  
function(foo) # comment next to command invocation                                   
# comment inside block                                   

set(
# comment inside command                                   
arg1 # comment inside command next to argument                                   
# comment inside command between arguments                                   
arg2 # comment inside command next to argument                                   
# comment inside command at the end                                   
)

unknown_command(
# comment inside command                                   
arg1 # comment inside command next to argument                                   
# comment inside command between arguments                                   
arg2 # comment inside command next to argument                                   
# comment inside command at the end                                   
)

if(TRUE)
# comment inside block inside another block                                   
endif()
  
endfunction()

#[[top-level comment                                   ]]                                   
function(foo) #[[comment next to command invocation                                   ]]                                   
#[[comment inside block                                   ]]                                   

set(
#[[comment inside command                                   ]]                                                                      
arg1 #[[comment inside command next to argument                                   ]]                                   
#[[comment inside command between arguments                                   ]]                                   
arg2 #[[comment inside command next to argument                                   ]]                                   
#[[comment inside command at the end                                   ]]                                   
)

unknown_command(
#[[comment inside command                                   ]]                                   
arg1 #[[comment inside command next to argument                                   ]]                                   
#[[comment inside command between arguments                                   ]]                                   
arg2 #[[comment inside command next to argument                                   ]]                                   
#[[comment inside command at the end                                   ]]                                   
)

if(TRUE)
#[[comment inside block inside another block                                   ]]                                   
endif()
  
endfunction()

#[[top-level comment                                   ]]     #[[top-level comment                                   ]]          
function(foo) #[[comment next to command invocation                                   ]]     #[[comment next to command invocation                                   ]]          
#[[comment inside block                                   ]]     #[[comment inside block                                   ]]          

set(
#[[comment inside command                                   ]]     #[[comment inside command                                   ]]          
arg1 #[[comment inside command next to argument                                   ]]     #[[comment inside command next to argument                                   ]]          
#[[comment inside command between arguments                                   ]]     #[[comment inside command between arguments                                   ]]          
arg2 #[[comment inside command next to argument                                   ]]     #[[comment inside command next to argument                                   ]]          
#[[comment inside command at the end                                   ]]     #[[comment inside command at the end                                   ]]          
)

unknown_command(
#[[comment inside command                                   ]]     #[[comment inside command                                   ]]          
arg1 #[[comment inside command next to argument                                   ]]     #[[comment inside command next to argument                                   ]]          
#[[comment inside command between arguments                                   ]]     #[[comment inside command between arguments                                   ]]          
arg2 #[[comment inside command next to argument                                   ]]     #[[comment inside command next to argument                                   ]]          
#[[comment inside command at the end                                   ]]     #[[comment inside command at the end                                   ]]          
)

if(TRUE)
#[[comment inside block inside another block                                   ]]     #[[comment inside block inside another block                                   ]]          
endif()
  
endfunction()
