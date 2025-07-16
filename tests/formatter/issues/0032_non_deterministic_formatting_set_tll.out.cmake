set(list_containing_keyword
    PUBLIC
    pthread
)

target_link_libraries(unrelated PRIVATE pthread)
