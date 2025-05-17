target_compile_definitions(
    foobar
    PRIVATE
        ccc
        bbb
        aaa
        zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz
)

target_link_libraries(
    foobar
    PRIVATE
        bbb
        zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz
        ccc
        aaa
    PUBLIC
        debug bbb
        optimized aaa
        zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz
        general ccc
    INTERFACE
        zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz
        bbb
        ccc
        aaa
)

target_sources(
    TGT
    PUBLIC
        FILE_SET FOO
        TYPE BAR
        BASE_DIRS BAZ QUX
        FILES FOO BAR BAZ QUX FOO BAR BAZ
    PRIVATE
        FILE_SET long_arg____________________________________________________________
        TYPE
            bbb
        BASE_DIRS
            cccc____________________________________________________________
            aaaa
        FILES
            bbb
            zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz
            ccc
    INTERFACE FILE_SET FOO
    PUBLIC
        FILE_SET FOO
        FILES
            bbb
            zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz
            ccc
)

target_sources(
    TGT
    PUBLIC
        zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz
        bbb
        ccc
        aaa
)

target_include_directories(
    TGT
    PUBLIC
        zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz
        bbb
        ccc
        aaa
        zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz
        bbb
        ccc
        aaa
        zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz
        bbb
        ccc
        aaa
)
