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

target_sources(
    TGT
    PUBLIC
        FILE_SET FOO
            TYPE BAR
            BASE_DIRS BAZ QUX
            FILES BAR BAR BAZ BAZ FOO FOO QUX
    PRIVATE
        FILE_SET
            long_arg____________________________________________________________
            TYPE bbb
            BASE_DIRS
                aaaa
                cccc____________________________________________________________
            FILES
                bbb
                ccc
                zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz
    INTERFACE FILE_SET FOO
    PUBLIC
        FILE_SET FOO
            FILES
                bbb
                ccc
                zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz
)

target_sources(
    TGT
    PUBLIC
        aaa
        bbb
        ccc
        zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz
)

target_include_directories(
    TGT
    PUBLIC
        aaa
        bbb
        ccc
        zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz
)
