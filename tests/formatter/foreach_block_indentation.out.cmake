foreach(i item1 item2 item3)
    message(STATUS i)
endforeach()

# nested foreach
foreach(i item1 item2 item3)
    message(STATUS i)
    # empty lines don't introduce superfluous spaces

    # comment also gets indented
    foreach(j item4 item5)
        # and here
        message(STATUS j)
        # and there
    endforeach()
endforeach()
