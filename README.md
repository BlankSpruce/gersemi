# gersemi

[![Status](https://github.com/BlankSpruce/gersemi/workflows/Tests/badge.svg?branch=master)](https://github.com/BlankSpruce/gersemi/actions) [![License: MPL 2.0](https://img.shields.io/badge/License-MPL%202.0-brightgreen.svg)](https://opensource.org/licenses/MPL-2.0) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A formatter to make your CMake code the real treasure.

## Installation

You can install gersemi from PyPI:
```
$ pip3 install gersemi
```

## Usage

```
usage: gersemi [-c] [-i] [--diff] [--default-config] [--version] [-h] [-l INTEGER]
               [--unsafe] [-q] [--color] [--definitions src [src ...]]
               [--list-expansion {favour-inlining,favour-expansion}]
               [src ...]

A formatter to make your CMake code the real treasure.

positional arguments:
  src                   File or directory to format. If only - is provided input is taken
                        from stdin instead

modes:
  -c, --check           Check if files require reformatting. Return 0 when there's nothing
                        to reformat, return 1 when some files would be reformatted
  -i, --in-place        Format files in-place
  --diff                Show diff on stdout for each formatted file instead
  --default-config      Generate default .gersemirc configuration file
  --version             Show version.
  -h, --help            Show this help message and exit.

configuration:
  By default configuration is loaded from YAML formatted .gersemirc file if it's
  available. This file should be placed in one of the common parent directories of source
  files. Arguments from command line can be used to override parts of that configuration
  or supply them in absence of configuration file.

  -l INTEGER, --line-length INTEGER
                        Maximum line length in characters [default: 80]
  --unsafe              Skip default sanity checks
  -q, --quiet           Skip printing non-error messages to stderr
  --color               If --diff is selected showed diff is colorized
  --definitions src [src ...]
                        Files or directories containing custom command definitions
                        (functions or macros). If only - is provided custom definitions, if
                        there are any, are taken from stdin instead. Commands from not
                        deprecated CMake native modules don't have to be provided (check
                        https://cmake.org/cmake/help/latest/manual/cmake-modules.7.html)
  --list-expansion {favour-inlining,favour-expansion}
                        Switch controls how code is expanded into multiple lines when it's
                        not possible to keep it formatted in one line. With 'favour-
                        inlining' (default) the list of entities will be formatted in such
                        way that sublists might still be formatted into single line as long
                        as it's possible. With 'favour-expansion' the list of entities will
                        be formatted in such way that sublists will be completely expanded
                        once expansion becomes necessary at all.

```

### [pre-commit](https://pre-commit.com/) hook

You can use gersemi with a pre-commit hook by adding the following to `.pre-commit-config.yaml` of your repository:
```yaml
repos:
- repo: https://github.com/BlankSpruce/gersemi
  rev: 0.9.3
  hooks:
  - id: gersemi
```

Update `rev` to relevant version used in your repository. For more details refer to https://pre-commit.com/#using-the-latest-version-for-a-repository

## Formatting

The key goal is for the tool to "just work" and to have as little configuration as possible so that you don't have to worry about fine-tuning formatter to your needs - as long as you embrace the `gersemi` style of formatting, similarly as `black` or `gofmt` do their job. Currently only line length can be changed with `80` as default value. Currently the basic assumption is that code to format is valid CMake language code - `gersemi` might be able to format some particular cases of invalid code but it's not guaranteed and it shouldn't be relied upon. Moreover only commands from CMake 3.0 onwards are supported and will be formatted properly - for instance [`exec_program` has been deprecated since CMake 3.0](https://cmake.org/cmake/help/latest/command/exec_program.html) so it won't be formatted. Be warned though it's not production ready so the changes to code might be destructive and you should always have a backup (version control helps a lot).

### Style

#### Default style `favour-inlining`

`gersemi` will try to format the code in a way that respects set character limit for single line and only break line whenever necessary.

Example:
```cmake
cmake_minimum_required(VERSION 3.18 FATAL_ERROR)
project(example CXX)

message(STATUS "This is example project")
message(
    STATUS
    "Here is yet another but much much longer message that should be displayed"
)

# project version
set(VERSION_MAJOR 0)
set(VERSION_MINOR 1)
set(VERSION_PATCH 0)

add_compile_options(
    -Wall
    -Wpedantic
    -fsanitize=address
    -fconcepts
    -fsomething-else
)

if(NOT ${SOME_OPTION})
    add_compile_options(-Werror)
endif()

# foobar library
add_library(foobar)
add_library(example::foobar ALIAS foobar)

target_sources(
    foobar
    PUBLIC
        include/some_subdirectory/header.hpp
        include/another_subdirectory/header.hpp
    PRIVATE
        src/some_subdirectory/src1.cpp
        src/some_subdirectory/src1.cpp
        src/another_subdirectory/src1.cpp
        src/another_subdirectory/src2.cpp
        src/another_subdirectory/src3.cpp
)

target_include_directories(
    foobar
    INTERFACE
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
)

target_link_libraries(
    foobar
    PUBLIC example::dependency_one example::dependency_two
    PRIVATE
        example::some_util
        external::some_lib
        external::another_lib
        Boost::Boost
)

include(GNUInstallDirs)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/${CMAKE_INSTALL_LIBDIR})
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/${CMAKE_INSTALL_LIBDIR})
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/${CMAKE_INSTALL_BINDIR})

# example executable
add_executable(app main.cpp)
target_link_libraries(app PRIVATE example::foobar Boost::Boost)

# tests
include(CTest)
include(GTest)
enable_testing()
add_subdirectory(tests)

# some helper function - see more details in "Let's make a deal" section
function(add_test_executable)
    set(OPTIONS
        QUIET
        VERBOSE
        SOME_PARTICULARLY_LONG_KEYWORD_THAT_ENABLES_SOMETHING
    )
    set(ONE_VALUE_ARGS NAME TESTED_TARGET)
    set(MULTI_VALUE_ARGS SOURCES DEPENDENCIES)

    cmake_parse_arguments(
        THIS_FUNCTION_PREFIX
        ${OPTIONS}
        ${ONE_VALUE_ARGS}
        ${MULTI_VALUE_ARGS}
    )
    # rest of the function
endfunction()

add_test_executable(
    NAME foobar_tests
    TESTED_TARGET foobar
    SOURCES
        some_test1.cpp
        some_test2.cpp
        some_test3.cpp
        some_test4.cpp
        some_test5.cpp
    QUIET
    DEPENDENCIES googletest::googletest
)

add_custom_command(
    OUTPUT ${SOMETHING_TO_OUTPUT}
    COMMAND ${CMAKE_COMMAND} -E cat foobar
    COMMAND cmake -E echo foobar
    COMMAND
        cmake -E echo "something quite a bit                           longer"
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/something
    DEPENDS
        ${CMAKE_CURRENT_SOURCE_DIR}/something
        ${CMAKE_CURRENT_SOURCE_DIR}/something_else
    COMMENT "example custom command"
)
```

#### Alternative style `favour-expansion`

In this style lines are broken in one of these cases:
- there is at least one multi-value argument present a single command invocation, either keyworded one like `PUBLIC` in `target_link_libraries` or standalone one like list of files in `add_library`, which has more than one value
- there are more than one multi-value arguments present in the command invocation like `target_link_libraries` with `PUBLIC` and `PRIVATE` arguments.
- character limit for single line is reached

One-value arguments (like `NAME` in `add_test`) will be inlined unless that'd violate character limit. Structure or control flow commands (`if`, `while`, `function`, `foreach` etc.) are exempted from these special rules and follow the same formatting as `favour-inlining`. This style is more merge or `git blame` friendly because usually multi-value arguments are changed one element at a time and with this style such change will be visible as one line of code per element.

Example:
```cmake
cmake_minimum_required(VERSION 3.18 FATAL_ERROR)
project(example CXX)

message(STATUS "This is example project")
message(
    STATUS
    "Here is yet another but much much longer message that should be displayed"
)

# project version
set(VERSION_MAJOR 0)
set(VERSION_MINOR 1)
set(VERSION_PATCH 0)

add_compile_options(
    -Wall
    -Wpedantic
    -fsanitize=address
    -fconcepts
    -fsomething-else
)

if(NOT ${SOME_OPTION})
    add_compile_options(-Werror)
endif()

# foobar library
add_library(foobar)
add_library(example::foobar ALIAS foobar)

target_sources(
    foobar
    PUBLIC
        include/some_subdirectory/header.hpp
        include/another_subdirectory/header.hpp
    PRIVATE
        src/some_subdirectory/src1.cpp
        src/some_subdirectory/src1.cpp
        src/another_subdirectory/src1.cpp
        src/another_subdirectory/src2.cpp
        src/another_subdirectory/src3.cpp
)

target_include_directories(
    foobar
    INTERFACE
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
)

target_link_libraries(
    foobar
    PUBLIC
        example::dependency_one
        example::dependency_two
    PRIVATE
        example::some_util
        external::some_lib
        external::another_lib
        Boost::Boost
)

include(GNUInstallDirs)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/${CMAKE_INSTALL_LIBDIR})
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/${CMAKE_INSTALL_LIBDIR})
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/${CMAKE_INSTALL_BINDIR})

# example executable
add_executable(app main.cpp)
target_link_libraries(
    app
    PRIVATE
        example::foobar
        Boost::Boost
)

# tests
include(CTest)
include(GTest)
enable_testing()
add_subdirectory(tests)

# some helper function - see more details in "Let's make a deal" section
function(add_test_executable)
    set(OPTIONS
        QUIET
        VERBOSE
        SOME_PARTICULARLY_LONG_KEYWORD_THAT_ENABLES_SOMETHING
    )
    set(ONE_VALUE_ARGS
        NAME
        TESTED_TARGET
    )
    set(MULTI_VALUE_ARGS
        SOURCES
        DEPENDENCIES
    )

    cmake_parse_arguments(
        THIS_FUNCTION_PREFIX
        ${OPTIONS}
        ${ONE_VALUE_ARGS}
        ${MULTI_VALUE_ARGS}
    )
    # rest of the function
endfunction()

add_test_executable(
    NAME foobar_tests
    TESTED_TARGET foobar
    SOURCES
        some_test1.cpp
        some_test2.cpp
        some_test3.cpp
        some_test4.cpp
        some_test5.cpp
    QUIET
    DEPENDENCIES googletest::googletest
)

add_custom_command(
    OUTPUT
        ${SOMETHING_TO_OUTPUT}
    COMMAND
        ${CMAKE_COMMAND} -E cat foobar
    COMMAND
        cmake -E echo foobar
    COMMAND
        cmake -E echo "something quite a bit                           longer"
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/something
    DEPENDS
        ${CMAKE_CURRENT_SOURCE_DIR}/something
        ${CMAKE_CURRENT_SOURCE_DIR}/something_else
    COMMENT "example custom command"
)
```

### Let's make a deal

It's possible to provide reasonable formatting for custom commands. However on language level there are no hints available about supported keywords for given command so `gersemi` has to generate specialized formatter. To do that custom command definition is necessary which should be provided with `--definitions`. There are limitations though since it'd probably require full-blown CMake language interpreter to do it in every case so let's make a deal: if your custom command definition (function or macro) uses `cmake_parse_arguments` and does it in obvious manner such specialized formatter will be generated. For instance this definition is okay (you can find other examples in `tests/custom_command_formatting/`):
```cmake
function(SEVEN_SAMURAI some standalone arguments)
    set(options KAMBEI KATSUSHIRO)
    set(oneValueArgs GOROBEI HEIHACHI KYUZO)
    set(multiValueArgs SHICHIROJI KIKUCHIYO)

    cmake_parse_arguments(
        THIS_FUNCTION_PREFIX
        "${options}"
        "${oneValueArgs}"
        "${multiValueArgs}"
        ${ARGN}
    )

    # rest of the function definition...
endfunction()
```

With this definition available it's possible to format code like so:
```cmake
seven_samurai(
    three
    standalone
    arguments
    KAMBEI
    KATSUSHIRO
    GOROBEI foo
    HEIHACHI bar
    KYUZO baz
    SHICHIROJI foo bar baz
    KIKUCHIYO bar baz foo
)
```

Otherwise `gersemi` will fallback to only fixing indentation and preserving original formatting. If you find these limitations too strict let me know about your case.

If your definition should be ignored for purposes of generating specialized formatter you can use `# gersemi: ignore` at the beginning of the custom command:
```cmake
function(harry_potter_and_the_philosophers_stone some standalone arguments)
    # gersemi: ignore
    set(options HARRY)
    set(oneValueArgs HERMIONE)
    set(multiValueArgs RON)

    cmake_parse_arguments(
        THIS_FUNCTION_PREFIX
        "${options}"
        "${oneValueArgs}"
        "${multiValueArgs}"
        ${ARGN}
    )

    # rest of the definition...
endfunction()

# no reformatting
harry_potter_and_the_philosophers_stone(HARRY
    HERMIONE foo
              RON foo bar baz)
```

It should be still preferred simply to not provide that definition instead.

### How to disable reformatting

Gersemi can be disallowed to format block of code using pair of comments `# gersemi: off`/`# gersemi: on`. Example:

```cmake
the_hobbit(
    BURGLAR "Bilbo Baggins"
    WIZARD Gandalf
    DWARVES
        "Thorin Oakenshield"
        Fili
        Kili
        Balin
        Dwalin
        Oin
        Gloin
        Dori
        Nori
        Ori
        Bifur
        Bofur
        Bombur
)

# gersemi: off
the_fellowship_of_the_ring     (
    RING_BEARER Frodo GARDENER Samwise
    Merry Pippin Aragon
            Boromir
            Gimli
       Legolas
       Gandalf
       )
# gersemi: on
```

Pair of comments should be in the same scope, so the following is not supported:
```cmake
# gersemi: off
the_godfather()

function(how_to_make_a_successful_movie args)
step_one_have_a_good_scenario()
# gersemi: on
step_two_make_the_movie()
endfunction()
```

## Contributing

Bug or style inconsitencies reports are always welcomed. In case of style enhancement or feature proposals consider providing rationale (and maybe some example) having in mind the deliberate choice mentioned above. As long as it's meant to improve something go for it and be prepared to defend your point.

## Running tests

Entire test suite can be run with just:
```
tox
```

Selecting functional tests can be done like so:
```
tox -e tests -- -k <test_pattern>
```

If you are familiar with `pytest` then you can pass relevant arguments after `--`.
