if(TRUE)
message(STATUS "bar")
while(TRUE)
message(STATUS "baz")
foreach(i item1 item2 item3)
message(STATUS i)
endforeach()

message(STATUS "foo")

foreach(j item1 item2 item3)
message(STATUS j)
endforeach()
endwhile()
else()
foreach(k item1 item2 item3)
message(STATUS k)
endforeach()
endif()