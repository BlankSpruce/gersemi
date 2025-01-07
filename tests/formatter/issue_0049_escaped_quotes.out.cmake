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
