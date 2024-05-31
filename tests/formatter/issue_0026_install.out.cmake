install(
    DIRECTORY "foobar"
    DESTINATION "/"
    PATTERN "something" EXCLUDE
    PATTERN "bin/*"
        PERMISSIONS
            OWNER_READ
            OWNER_WRITE
            OWNER_EXECUTE
            GROUP_READ
            GROUP_EXECUTE
            WORLD_READ
            WORLD_EXECUTE
    PATTERN "other-*"
        PERMISSIONS
            OWNER_READ
            OWNER_WRITE
            OWNER_EXECUTE
            GROUP_READ
            GROUP_EXECUTE
            WORLD_READ
            WORLD_EXECUTE
    # bracket argument PATTERN, I don't know if it's legal though
    PATTERN [[bracket pattern]]
        EXCLUDE
        PERMISSIONS
            OWNER_READ
            OWNER_WRITE
            OWNER_EXECUTE
            GROUP_READ
            GROUP_EXECUTE
            WORLD_READ
            WORLD_EXECUTE
)

# weird constructs but they shouldn't break code
install(
    DIRECTORY "foobar"
    DESTINATION "/"
    PATTERN # comment
    "something"
        PERMISSIONS
            OWNER_READ
            OWNER_WRITE
            OWNER_EXECUTE
            GROUP_READ
            GROUP_EXECUTE
            WORLD_READ
            WORLD_EXECUTE
    PATTERN #[==[ comment ]==] "something"
        PERMISSIONS
            OWNER_READ
            OWNER_WRITE
            OWNER_EXECUTE
            GROUP_READ
            GROUP_EXECUTE
            WORLD_READ
            WORLD_EXECUTE
)

# edge case
if(TRUE)
    install(
        DIRECTORY "foobar"
        DESTINATION "/"
        PATTERN
        "really_long____________________________________________________________pattern"
            EXCLUDE
            PERMISSIONS
                OWNER_READ
                OWNER_WRITE
                OWNER_EXECUTE
                GROUP_READ
                GROUP_EXECUTE
                WORLD_READ
                WORLD_EXECUTE
        PATTERN
        # line comment
        "really_long_pattern_with_line_comment________________________________________"
            PERMISSIONS
                OWNER_READ
                OWNER_WRITE
                OWNER_EXECUTE
                GROUP_READ
                GROUP_EXECUTE
                WORLD_READ
                WORLD_EXECUTE
    )

    install(
        DIRECTORY "foobar"
        DESTINATION "/"
        PATTERN
        "really_long____________________________________________________________pattern"
            EXCLUDE
            PERMISSIONS
                OWNER_READ
                OWNER_WRITE
                OWNER_EXECUTE
                GROUP_READ
                GROUP_EXECUTE
                WORLD_READ
                WORLD_EXECUTE
        PATTERN
        #[[ bracket

  comment ]]
        "really_long_pattern_with_line_comment________________________________________"
            PERMISSIONS
                OWNER_READ
                OWNER_WRITE
                OWNER_EXECUTE
                GROUP_READ
                GROUP_EXECUTE
                WORLD_READ
                WORLD_EXECUTE
    )
endif()
