issue0100_nestedMultiFunction(LINK lib1)

issue0100_nestedMultiFunction(
    LINK
        lib1
        lib2
)

issue0100_nestedMultiFunction(LINK lib1 NESTED_LINK PRIVATE lib1)

issue0100_nestedMultiFunction(
    LINK
        lib1
        lib2
    NESTED_LINK
        PRIVATE
            lib1
)

issue0100_nestedMultiFunction(
    LINK
        lib1
        lib2
    NESTED_LINK
        PRIVATE
            lib1
            lib2
)
