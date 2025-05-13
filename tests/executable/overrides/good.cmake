target_compile_definitions(
    foobar
    PRIVATE
        aaa
        bbb
        ccc
        zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz
)

target_link_libraries(
    foobar
    PRIVATE
        aaa
        bbb
        ccc
        zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz
    PUBLIC
        debug bbb
        general ccc
        optimized aaa
        zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz
    INTERFACE
        aaa
        bbb
        ccc
        zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz
)
