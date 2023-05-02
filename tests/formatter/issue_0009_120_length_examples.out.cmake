find_package(Qt5 COMPONENTS Core REQUIRED)
get_target_property(fooLocation Foo IMPORTED_LOCATION)
find_program(foo_EXECUTABLE foo HINTS "${fooDirectory}")
file(COPY foo DESTINATION "${CMAKE_CURRENT_BINARY_DIR}/foo")
configure_file(Foo.cpp.in Foo.cpp @ONLY)
list(APPEND foo "BAR")
cmake_policy(SET CMP0077 NEW)
set("${outputVar}" "${result}" PARENT_SCOPE)
math(EXPR pos1 "${pos}+1")

foreach(foo IN LISTS bar)
endforeach()

if(FOO STREQUAL "BAR")
endif()

if(FOO AND BAR)
endif()

find_package(
    Qt5
    COMPONENTS
        Core
        Widgets
    REQUIRED
)
find_program(
    foo_EXECUTABLE
    foo
    HINTS
        "${fooDirectory}"
        "${barDirectory}"
)
file(
    COPY
        foo
        bar
    DESTINATION "${CMAKE_CURRENT_BINARY_DIR}/foo"
)
list(
    APPEND
    foo
    "BAR"
    "BAZ"
)
set("${outputVar}"
    "${result}"
    "${another_result}"
    PARENT_SCOPE
)

foreach(foo IN LISTS bar baz)
endforeach()

if(FOO AND BAR AND BAZ)
endif()

if(FOO AND BAR AND BAZ AND QUX)
endif()

if(FOO AND BAR AND BAZ AND QUX AND FOO)
endif()

function(fooo)
    set(OPTIONS "QUIET")
    set(ONE_VALUE_ARGS "NAME")
    set(MULTI_VALUE_ARGS "SOURCES")
    cmake_parse_arguments("FOOO" ${OPTIONS} ${ONE_VALUE_ARGS} ${MULTI_VALUE_ARGS} ${ARGN})
endfunction()

add_custom_command(
    OUTPUT
        foo.txt
    COMMAND
        "${CMAKE_COMMAND}" -E touch foo.txt
    DEPENDS
        bar.txt
        baz.txt
    VERBATIM
)

add_custom_command(
    TARGET Foo
    POST_BUILD
    COMMAND
        "${CMAKE_COMMAND}" -E touch "$<TARGET_FILE_DIR:Foo>/bar.txt"
    VERBATIM
)

find_package(Qt5 REQUIRED COMPONENTS Qml)
find_package(
    Qt5
    REQUIRED
    COMPONENTS
        Qml
        QuickCompiler
)

find_package(Qt5 Qml)
# it's ambiguous whether Qml means version or component
find_package(Qt5 Qml QuickCompiler)
find_package(
    Qt5
    Qml
    QuickCompiler
    Qml
)

find_package(Qt5 REQUIRED Qml)
find_package(
    Qt5
    REQUIRED
    Qml
    QuickCompiler
)

add_test(
    NAME test_foo
    COMMAND
        "${CMAKE_COMMAND}" -E true
    WORKING_DIRECTORY
        # we have to run this in the binary dir
        "${CMAKE_CURRENT_BINARY_DIR}"
)

set(foo "bar" CACHE STRING "docstring")
set(foo
    "bar"
    CACHE STRING
    "long                                                                                               docstring"
)

function(foo bar baz)
endfunction()

foreach(var IN LISTS list1 list2)
endforeach()

if(foo AND bar AND baz)
endif()

set_target_properties(
    Target
    PROPERTIES
        FOO
            bar
)

set_target_properties(
    Target
    PROPERTIES
        FOO
            bar
        BAZ
            goo
)

set_property(
    TARGET
        Target
    PROPERTY
        FOO
            bar
)

set_property(
    TARGET
        Target
    PROPERTY
        FOO
            bar
            baz
)

function(foo)
    cmake_parse_arguments("" "" "FIXTURE;SETUP" "" ${ARGN})
endfunction()
