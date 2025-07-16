# https://cmake.org/cmake/help/latest/command/install.html#signatures
#
#     The first <artifact-option>... group applies to target Output Artifacts
#     that do not have a dedicated group specified later in the same call.

install(TARGETS ${LIB_NAME} COMPONENT TARGET_COMPONENT DESTINATION lib)

install(
    TARGETS
        ${LIB_NAME}
        ${LIB2_NAME}
    COMPONENT TARGET_COMPONENT
    DESTINATION lib
)

install(
    TARGETS
        ${LIB_NAME}
    COMPONENT TARGET_COMPONENT
    DESTINATION lib
    PERMISSIONS
        foo
        bar
        baz
)

install(
    TARGETS
        ${LIB_NAME}
    COMPONENT TARGET_COMPONENT
    DESTINATION lib
    RUNTIME
        COMPONENT TARGET_COMPONENT
        DESTINATION lib
)

install(
    TARGETS
        ${LIB_NAME}
    COMPONENT TARGET_COMPONENT
    DESTINATION lib
    PERMISSIONS
        foo
        bar
        baz
    RUNTIME
        COMPONENT TARGET_COMPONENT
        DESTINATION lib
        PERMISSIONS
            foo
            bar
            baz
)

install(
    TARGETS
        ${LIB_NAME}
        ${LIB2_NAME}
    COMPONENT TARGET_COMPONENT
    DESTINATION lib
    RUNTIME
        COMPONENT TARGET_COMPONENT
        DESTINATION lib
)

install(
    TARGETS
        ${LIB_NAME}
        ${LIB2_NAME}
    COMPONENT TARGET_COMPONENT
    DESTINATION lib
    RUNTIME
        COMPONENT TARGET_COMPONENT
        DESTINATION lib
    LIBRARY
        COMPONENT TARGET_COMPONENT
        DESTINATION lib
)

install(
    RUNTIME_DEPENDENCY_SET
        deps
    RUNTIME
        DESTINATION bin
        COMPONENT bin2
    LIBRARY
        DESTINATION lib
        COMPONENT lib2
    FRAMEWORK
        DESTINATION fw
        COMPONENT fw2
)
