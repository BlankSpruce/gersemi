export(EXPORT FOO)

export(EXPORT FOO NAMESPACE BAR)

export(EXPORT FOO NAMESPACE BAR FILE BAZ)

export(
    EXPORT long_arg____________________________________________________________
)

export(
    EXPORT long_arg____________________________________________________________
    NAMESPACE
        long_arg____________________________________________________________
)

export(
    EXPORT long_arg____________________________________________________________
    NAMESPACE
        long_arg____________________________________________________________
    FILE long_arg____________________________________________________________
)

export(TARGETS FOO)

export(TARGETS FOO BAR BAZ)

export(TARGETS FOO BAR BAZ NAMESPACE FOO APPEND FILE BAR)

export(
    TARGETS FOO BAR BAZ
    NAMESPACE FOO
    APPEND
    FILE BAR
    EXPORT_LINK_INTERFACE_LIBRARIES
)

export(
    TARGETS long_arg____________________________________________________________
)

export(
    TARGETS
        long_arg____________________________________________________________
        long_arg____________________________________________________________
        long_arg____________________________________________________________
)

export(
    TARGETS
        long_arg____________________________________________________________
        long_arg____________________________________________________________
        long_arg____________________________________________________________
    NAMESPACE
        long_arg____________________________________________________________
    APPEND
    FILE long_arg____________________________________________________________
)

export(
    TARGETS
        long_arg____________________________________________________________
        long_arg____________________________________________________________
        long_arg____________________________________________________________
    NAMESPACE
        long_arg____________________________________________________________
    APPEND
    FILE long_arg____________________________________________________________
    EXPORT_LINK_INTERFACE_LIBRARIES
)

export(PACKAGE FOO)

export(
    PACKAGE long_arg____________________________________________________________
)

export(TARGETS FOO ANDROID_MK BAR)

export(TARGETS FOO BAR BAZ ANDROID_MK FOO)

export(
    TARGETS long_arg____________________________________________________________
    ANDROID_MK
        long_arg____________________________________________________________
)

export(
    TARGETS
        long_arg____________________________________________________________
        long_arg____________________________________________________________
        long_arg____________________________________________________________
    ANDROID_MK
        long_arg____________________________________________________________
)

export(
    SETUP foo
    PACKAGE_DEPENDENCY bar ENABLED AUTO EXTRA_ARGS baz qux foo
    TARGET bar XCFRAMEWORK_LOCATION baz
)

export(
    SETUP foo__________________________________________________
    PACKAGE_DEPENDENCY
        bar__________________________________________________
        ENABLED AUTO
        EXTRA_ARGS
            baz__________________________________________________
            qux__________________________________________________
            foo__________________________________________________
    TARGET
        bar__________________________________________________
        XCFRAMEWORK_LOCATION
            baz__________________________________________________
)
