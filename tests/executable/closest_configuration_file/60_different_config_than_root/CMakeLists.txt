# no expansion
target_link_libraries(FOO PRIVATE BAR)

# expand when line length is 40
target_link_libraries(FOO PRIVATE BAR_____)

# expand when line length is 60
target_link_libraries(
    FOO
    PRIVATE BAR_________________________
)

# expand when line length is 80
target_link_libraries(
    FOO
    PRIVATE BAR_____________________________________________
)

# expand when line length is 100
target_link_libraries(
    FOO
    PRIVATE
        BAR_________________________________________________________________
)
