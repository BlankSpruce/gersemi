install(TARGETS FOO)

install(TARGETS FOO BAR BAZ)

install(TARGETS FOO EXPORT BAR ARCHIVE)

install(
    TARGETS FOO
    LIBRARY DESTINATION BAR PERMISSIONS OWNER_READ OWNER_WRITE
)

install(
    TARGETS FOO
    RUNTIME
        PERMISSIONS
            OWNER_READ
            OWNER_WRITE
            OWNER_EXECUTE
            GROUP_READ
            GROUP_WRITE
            GROUP_EXECUTE
            WORLD_READ
            WORLD_WRITE
            WORLD_EXECUTE
            SETUID
            SETGID
        NAMELINK_SKIP
)

install(
    TARGETS FOO
    EXPORT BAR
    OBJECTS
        DESTINATION BAZ
        PERMISSIONS OWNER_READ
        CONFIGURATIONS Debug
        COMPONENT FOO
        NAMELINK_COMPONENT BAR
        OPTIONAL
        EXCLUDE_FROM_ALL
        NAMELINK_ONLY
    INCLUDES DESTINATION FOO
)

install(
    TARGETS FOO BAR BAZ
    EXPORT BAR
    FRAMEWORK
        DESTINATION BAZ
        PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE
        CONFIGURATIONS Debug
        COMPONENT FOO
        NAMELINK_COMPONENT BAR
        OPTIONAL
        EXCLUDE_FROM_ALL
        NAMELINK_ONLY
    INCLUDES DESTINATION FOO BAR BAZ
)

install(
    TARGETS long_arg____________________________________________________________
)

install(
    TARGETS
        long_arg____________________________________________________________
        long_arg____________________________________________________________
        long_arg____________________________________________________________
)

install(
    TARGETS long_arg____________________________________________________________
    EXPORT long_arg____________________________________________________________
    ARCHIVE
)

install(
    TARGETS long_arg____________________________________________________________
    BUNDLE
        DESTINATION
            long_arg____________________________________________________________
        PERMISSIONS OWNER_READ OWNER_WRITE
)

install(
    TARGETS long_arg____________________________________________________________
    PRIVATE_HEADER
        PERMISSIONS
            OWNER_READ
            OWNER_WRITE
            OWNER_EXECUTE
            GROUP_READ
            GROUP_WRITE
            GROUP_EXECUTE
            WORLD_READ
            WORLD_WRITE
            WORLD_EXECUTE
            SETUID
            SETGID
)

install(
    TARGETS long_arg____________________________________________________________
    EXPORT long_arg____________________________________________________________
    PUBLIC_HEADER
        DESTINATION
            long_arg____________________________________________________________
        PERMISSIONS OWNER_READ
        CONFIGURATIONS Debug
        COMPONENT
            long_arg____________________________________________________________
        NAMELINK_COMPONENT
            long_arg____________________________________________________________
        OPTIONAL
        EXCLUDE_FROM_ALL
        NAMELINK_ONLY
    INCLUDES DESTINATION
        long_arg____________________________________________________________
)

install(
    TARGETS
        long_arg____________________________________________________________
        long_arg____________________________________________________________
        long_arg____________________________________________________________
    EXPORT long_arg____________________________________________________________
    RESOURCE
        DESTINATION
            long_arg____________________________________________________________
        PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE
        CONFIGURATIONS Debug
        COMPONENT
            long_arg____________________________________________________________
        NAMELINK_COMPONENT
            long_arg____________________________________________________________
        OPTIONAL
        EXCLUDE_FROM_ALL
        NAMELINK_ONLY
    INCLUDES DESTINATION
        long_arg____________________________________________________________
        long_arg____________________________________________________________
        long_arg____________________________________________________________
)

install(FILES FOO)

install(FILES FOO TYPE BAR PERMISSIONS OWNER_READ)

install(FILES FOO DESTINATION BAR CONFIGURATIONS BAZ COMPONENT FOO)

install(
    FILES FOO
    DESTINATION BAR
    PERMISSIONS OWNER_READ
    CONFIGURATIONS Debug
    COMPONENT BAZ
    RENAME BAR
    OPTIONAL
    EXCLUDE_FROM_ALL
)

install(
    FILES FOO BAR BAZ
    DESTINATION FOO
    PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE
    CONFIGURATIONS Debug
    COMPONENT BAZ
    RENAME BAR
    OPTIONAL
    EXCLUDE_FROM_ALL
)

install(
    FILES long_arg____________________________________________________________
)

install(
    FILES long_arg____________________________________________________________
    TYPE long_arg____________________________________________________________
    PERMISSIONS OWNER_READ
)

install(
    FILES long_arg____________________________________________________________
    DESTINATION
        long_arg____________________________________________________________
    CONFIGURATIONS
        long_arg____________________________________________________________
    COMPONENT
        long_arg____________________________________________________________
)

install(
    FILES long_arg____________________________________________________________
    DESTINATION
        long_arg____________________________________________________________
    PERMISSIONS OWNER_READ
    CONFIGURATIONS Debug
    COMPONENT
        long_arg____________________________________________________________
    RENAME long_arg____________________________________________________________
    OPTIONAL
    EXCLUDE_FROM_ALL
)

install(
    FILES
        long_arg____________________________________________________________
        long_arg____________________________________________________________
        long_arg____________________________________________________________
    DESTINATION
        long_arg____________________________________________________________
    PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE
    CONFIGURATIONS Debug
    COMPONENT
        long_arg____________________________________________________________
    RENAME long_arg____________________________________________________________
    OPTIONAL
    EXCLUDE_FROM_ALL
)

install(PROGRAMS FOO TYPE BAR)

install(PROGRAMS FOO TYPE BAR PERMISSIONS OWNER_READ)

install(PROGRAMS FOO DESTINATION BAR CONFIGURATIONS BAZ COMPONENT FOO)

install(
    PROGRAMS FOO
    DESTINATION BAR
    PERMISSIONS OWNER_READ
    CONFIGURATIONS Debug
    COMPONENT BAZ
    RENAME BAR
    OPTIONAL
    EXCLUDE_FROM_ALL
)

install(
    PROGRAMS FOO BAR BAZ
    DESTINATION FOO
    PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE
    CONFIGURATIONS Debug
    COMPONENT BAZ
    RENAME BAR
    OPTIONAL
    EXCLUDE_FROM_ALL
)

install(
    PROGRAMS
        long_arg____________________________________________________________
)

install(
    PROGRAMS
        long_arg____________________________________________________________
    TYPE long_arg____________________________________________________________
    PERMISSIONS OWNER_READ
)

install(
    PROGRAMS
        long_arg____________________________________________________________
    DESTINATION
        long_arg____________________________________________________________
    CONFIGURATIONS
        long_arg____________________________________________________________
    COMPONENT
        long_arg____________________________________________________________
)

install(
    PROGRAMS
        long_arg____________________________________________________________
    DESTINATION
        long_arg____________________________________________________________
    PERMISSIONS OWNER_READ
    CONFIGURATIONS Debug
    COMPONENT
        long_arg____________________________________________________________
    RENAME long_arg____________________________________________________________
    OPTIONAL
    EXCLUDE_FROM_ALL
)

install(
    PROGRAMS
        long_arg____________________________________________________________
        long_arg____________________________________________________________
        long_arg____________________________________________________________
    DESTINATION
        long_arg____________________________________________________________
    PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE
    CONFIGURATIONS Debug
    COMPONENT
        long_arg____________________________________________________________
    RENAME long_arg____________________________________________________________
    OPTIONAL
    EXCLUDE_FROM_ALL
)

install(DIRECTORY FOO TYPE BAR)

install(DIRECTORY FOO DESTINATION BAR FILE_PERMISSIONS OWNER_READ)

install(
    DIRECTORY FOO
    DESTINATION BAR
    FILE_PERMISSIONS OWNER_READ
    DIRECTORY_PERMISSIONS OWNER_READ
    USE_SOURCE_PERMISSIONS
    OPTIONAL
    MESSAGE_NEVER
    CONFIGURATIONS Debug
    COMPONENT FOO
    EXCLUDE_FROM_ALL
    FILES_MATCHING
    PATTERN FOO EXCLUDE PERMISSIONS OWNER_READ
)

install(
    DIRECTORY FOO BAR BAZ
    DESTINATION BAR
    FILE_PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE
    DIRECTORY_PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE
    USE_SOURCE_PERMISSIONS
    OPTIONAL
    MESSAGE_NEVER
    CONFIGURATIONS Debug
    COMPONENT FOO
    EXCLUDE_FROM_ALL
    FILES_MATCHING
    REGEX FOO EXCLUDE PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE
)

install(
    DIRECTORY
        long_arg____________________________________________________________
    TYPE long_arg____________________________________________________________
)

install(
    DIRECTORY
        long_arg____________________________________________________________
    DESTINATION
        long_arg____________________________________________________________
    FILE_PERMISSIONS OWNER_READ
)

install(
    DIRECTORY
        long_arg____________________________________________________________
    DESTINATION
        long_arg____________________________________________________________
    FILE_PERMISSIONS OWNER_READ
    DIRECTORY_PERMISSIONS OWNER_READ
    USE_SOURCE_PERMISSIONS
    OPTIONAL
    MESSAGE_NEVER
    CONFIGURATIONS Debug
    COMPONENT
        long_arg____________________________________________________________
    EXCLUDE_FROM_ALL
    FILES_MATCHING
    PATTERN long_arg____________________________________________________________
        EXCLUDE
        PERMISSIONS OWNER_READ
)

install(
    DIRECTORY
        long_arg____________________________________________________________
        long_arg____________________________________________________________
        long_arg____________________________________________________________
    DESTINATION
        long_arg____________________________________________________________
    FILE_PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE
    DIRECTORY_PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE
    USE_SOURCE_PERMISSIONS
    OPTIONAL
    MESSAGE_NEVER
    CONFIGURATIONS Debug
    COMPONENT
        long_arg____________________________________________________________
    EXCLUDE_FROM_ALL
    FILES_MATCHING
    REGEX long_arg____________________________________________________________
        EXCLUDE
        PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE
)

install(SCRIPT FOO)

install(SCRIPT FOO COMPONENT BAR)

install(SCRIPT FOO COMPONENT BAR EXCLUDE_FROM_ALL)

install(
    SCRIPT long_arg____________________________________________________________
)

install(
    SCRIPT long_arg____________________________________________________________
    COMPONENT
        long_arg____________________________________________________________
)

install(
    SCRIPT long_arg____________________________________________________________
    COMPONENT
        long_arg____________________________________________________________
    EXCLUDE_FROM_ALL
)

install(
    CODE long_arg____________________________________________________________
)

install(
    CODE long_arg____________________________________________________________
    COMPONENT
        long_arg____________________________________________________________
)

install(
    CODE long_arg____________________________________________________________
    COMPONENT
        long_arg____________________________________________________________
    EXCLUDE_FROM_ALL
)

install(
    CODE long_arg____________________________________________________________
)

install(
    CODE long_arg____________________________________________________________
    COMPONENT
        long_arg____________________________________________________________
)

install(
    CODE long_arg____________________________________________________________
    COMPONENT
        long_arg____________________________________________________________
    EXCLUDE_FROM_ALL
)

install(EXPORT FOO DESTINATION BAR)

install(EXPORT FOO DESTINATION BAR NAMESPACE FOO FILE BAR)

install(
    EXPORT FOO
    DESTINATION BAR
    NAMESPACE FOO
    FILE BAR
    PERMISSIONS OWNER_READ
    CONFIGURATIONS Debug
    EXPORT_LINK_INTERFACE_LIBRARIES
    COMPONENT FOO
    EXCLUDE_FROM_ALL
)

install(
    EXPORT FOO
    DESTINATION BAR
    NAMESPACE FOO
    FILE BAR
    PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE
    CONFIGURATIONS Debug
    EXPORT_LINK_INTERFACE_LIBRARIES
    COMPONENT FOO
    EXCLUDE_FROM_ALL
)

install(
    EXPORT long_arg____________________________________________________________
    DESTINATION
        long_arg____________________________________________________________
)

install(
    EXPORT long_arg____________________________________________________________
    DESTINATION
        long_arg____________________________________________________________
    NAMESPACE
        long_arg____________________________________________________________
    FILE long_arg____________________________________________________________
)

install(
    EXPORT long_arg____________________________________________________________
    DESTINATION
        long_arg____________________________________________________________
    NAMESPACE
        long_arg____________________________________________________________
    FILE long_arg____________________________________________________________
    PERMISSIONS OWNER_READ
    CONFIGURATIONS Debug
    EXPORT_LINK_INTERFACE_LIBRARIES
    COMPONENT
        long_arg____________________________________________________________
    EXCLUDE_FROM_ALL
)

install(
    EXPORT long_arg____________________________________________________________
    DESTINATION
        long_arg____________________________________________________________
    NAMESPACE
        long_arg____________________________________________________________
    FILE long_arg____________________________________________________________
    PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE
    CONFIGURATIONS Debug
    EXPORT_LINK_INTERFACE_LIBRARIES
    COMPONENT
        long_arg____________________________________________________________
    EXCLUDE_FROM_ALL
)

install(EXPORT_ANDROID_MK FOO DESTINATION BAR)

install(EXPORT_ANDROID_MK FOO DESTINATION BAR NAMESPACE FOO FILE BAR)

install(
    EXPORT_ANDROID_MK FOO
    DESTINATION BAR
    NAMESPACE FOO
    FILE BAR
    PERMISSIONS OWNER_READ
    CONFIGURATIONS Debug
    EXPORT_LINK_INTERFACE_LIBRARIES
    COMPONENT FOO
    EXCLUDE_FROM_ALL
)

install(
    EXPORT_ANDROID_MK FOO
    DESTINATION BAR
    NAMESPACE FOO
    FILE BAR
    PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE
    CONFIGURATIONS Debug
    EXPORT_LINK_INTERFACE_LIBRARIES
    COMPONENT FOO
    EXCLUDE_FROM_ALL
)

install(
    EXPORT_ANDROID_MK
        long_arg____________________________________________________________
    DESTINATION
        long_arg____________________________________________________________
)

install(
    EXPORT_ANDROID_MK
        long_arg____________________________________________________________
    DESTINATION
        long_arg____________________________________________________________
    NAMESPACE
        long_arg____________________________________________________________
    FILE long_arg____________________________________________________________
)

install(
    EXPORT_ANDROID_MK
        long_arg____________________________________________________________
    DESTINATION
        long_arg____________________________________________________________
    NAMESPACE
        long_arg____________________________________________________________
    FILE long_arg____________________________________________________________
    PERMISSIONS OWNER_READ
    CONFIGURATIONS Debug
    EXPORT_LINK_INTERFACE_LIBRARIES
    COMPONENT
        long_arg____________________________________________________________
    EXCLUDE_FROM_ALL
)

install(
    EXPORT_ANDROID_MK
        long_arg____________________________________________________________
    DESTINATION
        long_arg____________________________________________________________
    NAMESPACE
        long_arg____________________________________________________________
    FILE long_arg____________________________________________________________
    PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE
    CONFIGURATIONS Debug
    EXPORT_LINK_INTERFACE_LIBRARIES
    COMPONENT
        long_arg____________________________________________________________
    EXCLUDE_FROM_ALL
)

install(
    TARGETS FOO
    EXPORT BAR
    FILE_SET FOOBAR
        DESTINATION BAZ
        PERMISSIONS OWNER_READ
        CONFIGURATIONS Debug
        COMPONENT FOO
        NAMELINK_ONLY
    INCLUDES DESTINATION FOO
)

install(
    TARGETS ${target}
    EXPORT ${target}Targets
    RUNTIME
        DESTINATION "${OBS_EXECUTABLE_DESTINATION}"
        COMPONENT Development
        EXCLUDE_FROM_ALL
    LIBRARY
        DESTINATION "${OBS_LIBRARY_DESTINATION}"
        COMPONENT Development
        EXCLUDE_FROM_ALL
    ARCHIVE
        DESTINATION "${OBS_LIBRARY_DESTINATION}"
        COMPONENT Development
        EXCLUDE_FROM_ALL
    FRAMEWORK
        DESTINATION Frameworks____________________
        COMPONENT Development
        EXCLUDE_FROM_ALL
    INCLUDES DESTINATION "${include_destination}"
    PUBLIC_HEADER
        DESTINATION "${include_destination}"
        COMPONENT Development
        EXCLUDE_FROM_ALL
)

install(
    IMPORTED_RUNTIME_ARTIFACTS
        FOO__________________________________________________
        BAR__________________________________________________
        BAZ__________________________________________________
    RUNTIME_DEPENDENCY_SET BAR__________________________________________________
    LIBRARY
        DESTINATION BAR__________________________________________________
        PERMISSIONS
            BAR__________________________________________________
            BAR__________________________________________________
            BAR__________________________________________________
        CONFIGURATIONS
            BAR__________________________________________________
            BAR__________________________________________________
            BAR__________________________________________________
        COMPONENT BAR__________________________________________________
        OPTIONAL
        EXCLUDE_FROM_ALL
    RUNTIME
        DESTINATION BAR__________________________________________________
        PERMISSIONS
            BAR__________________________________________________
            BAR__________________________________________________
            BAR__________________________________________________
        CONFIGURATIONS
            BAR__________________________________________________
            BAR__________________________________________________
            BAR__________________________________________________
        COMPONENT BAR__________________________________________________
        OPTIONAL
        EXCLUDE_FROM_ALL
    FRAMEWORK
        DESTINATION BAR__________________________________________________
        PERMISSIONS
            BAR__________________________________________________
            BAR__________________________________________________
            BAR__________________________________________________
        CONFIGURATIONS
            BAR__________________________________________________
            BAR__________________________________________________
            BAR__________________________________________________
        COMPONENT BAR__________________________________________________
        OPTIONAL
        EXCLUDE_FROM_ALL
    BUNDLE
        DESTINATION BAR__________________________________________________
        PERMISSIONS
            BAR__________________________________________________
            BAR__________________________________________________
            BAR__________________________________________________
        CONFIGURATIONS
            BAR__________________________________________________
            BAR__________________________________________________
            BAR__________________________________________________
        COMPONENT BAR__________________________________________________
        OPTIONAL
        EXCLUDE_FROM_ALL
)
