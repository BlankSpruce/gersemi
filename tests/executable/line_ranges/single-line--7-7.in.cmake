# only message(STATUS) is formatted

project( FOO BAR )

  if( TRUE OR TRUE OR TARGET FOOBAR__________________________________________________ )

      message(STATUS "FOOBAR"                   )
      
      endif()
