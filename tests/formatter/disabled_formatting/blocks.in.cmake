# normal case
if(TRUE)
message(STATUS "OK")
endif()

# block case
# gersemi: off
if(TRUE)
# gersemi: on
message(STATUS "OK")
# gersemi: off
endif()
# gersemi: on

# nested block case
if(TRUE)
# gersemi: off
if(TRUE)
# gersemi: on
message(STATUS "OK")
# gersemi: off
endif()
# gersemi: on
endif()

# nested nested block case
if(TRUE)
    if(TRUE)
# gersemi: off
if(TRUE)
# gersemi: on
            message(STATUS "OK")
# gersemi: off
endif()
# gersemi: on
    endif()
endif()
