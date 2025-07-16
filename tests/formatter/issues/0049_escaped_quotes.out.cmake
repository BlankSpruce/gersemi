set(MY_VAR -DCMAKE_INSTALL_PREFIX="\"${INSTALL_PREFIX}\"")

set(MY_VAR -DCMAKE_INSTALL_PREFIX="\"${INSTALL_PREFIX}\"")

set(MY_VAR -DCMAKE_INSTALL_PREFIX="\"${INSTALL_PREFIX}\"" FOO)

set(MY_VAR -DCMAKE_INSTALL_PREFIX="\"${INSTALL_PREFIX}\"" FOO)

set(MY_VAR
    -DCMAKE_INSTALL_PREFIX="\"${INSTALL_PREFIX}\""
    FOO
    -DCMAKE_INSTALL_PREFIX="\"${INSTALL_PREFIX}\""
)

set(MY_VAR
    -DCMAKE_INSTALL_PREFIX="\"${INSTALL_PREFIX}\""
    FOO
    -DCMAKE_INSTALL_PREFIX="\"${INSTALL_PREFIX}\""
)

set(MY_VAR
    -DCMAKE_INSTALL_PREFIX="\"${INSTALL_PREFIX}\""
    FOO
    -DCMAKE_INSTALL_PREFIX="\"${INSTALL_PREFIX}\""
    foo
)

set(MY_VAR
    -DCMAKE_INSTALL_PREFIX="\"${INSTALL_PREFIX}\""
    FOO
    -DCMAKE_INSTALL_PREFIX="\"${INSTALL_PREFIX}\""
    foo
)

set(cmake_doc_example a)
set(cmake_doc_example a" ")
set(cmake_doc_example a" "b)
set(cmake_doc_example a" "b"c")
set(cmake_doc_example a" "b"c"d)
set(cmake_doc_example a" "b"c"d" ")
set(cmake_doc_example a" "b"c"d" "e)
set(cmake_doc_example a" "b"c"d" "e"f")

set(comment_case
    FOO
    "foo" # line comment
)
set(comment_case
    FOO"foo" # line comment
)
set(comment_case
    FOO"foo"FOO # line comment
)
set(comment_case
    FOO"foo"FOO"foo" # line comment
)
set(comment_case
    FOO"foo"FOO"foo"FOO # line comment
)

set(comment_case FOO "foo" #[[bracket comment]])
set(comment_case FOO"foo" #[[bracket comment]])
set(comment_case FOO"foo"FOO #[[bracket comment]])
set(comment_case FOO"foo"FOO"foo" #[[bracket comment]])
set(comment_case FOO"foo"FOO"foo"FOO #[[bracket comment]])

set(comment_case FOO "foo" #[[bracket comment]] FOO "foo")
set(comment_case FOO"foo" #[[bracket comment]] FOO"foo")
set(comment_case FOO"foo"FOO #[[bracket comment]] FOO"foo"FOO)

# don't mess with complex_argument
if((FOO STREQUAL "foo"))
endif()
