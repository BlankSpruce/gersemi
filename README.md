# gersemi

[![Status](https://github.com/BlankSpruce/gersemi/workflows/Tests/badge.svg)](https://github.com/BlankSpruce/gersemi/actions) [![License: MPL 2.0](https://img.shields.io/badge/License-MPL%202.0-brightgreen.svg)](https://opensource.org/licenses/MPL-2.0) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A formatter to make your CMake code the real treasure.

## Installation

You can install gersemi from PyPI:

```shell
pip3 install gersemi
```

## Usage

```plain
usage: gersemi [-c] [-i] [--diff] [--print-config {minimal,verbose,default}] [--version]
               [-h] [-l INTEGER] [--indent (INTEGER | tabs)] [--unsafe]
               [--definitions src [src ...]]
               [--list-expansion {favour-inlining,favour-expansion}]
               [--warn-about-unknown-commands] [--disable-formatting]
               [--extensions extension-name [extension-name ...]] [-q] [--color]
               [-w (INTEGER | max)] [--cache] [--config CONFIGURATION_FILE]
               [--warnings-as-errors]
               [src ...]

A formatter to make your CMake code the real treasure.

positional arguments:
  src                   File or directory to format. When directory is provided then
                        CMakeLists.txt and files with .cmake extension are automatically
                        discovered. If only `-` is provided, input is taken from stdin
                        instead.

modes:
  -c, --check           Check if files require reformatting. Return 0 when there's
                        nothing to reformat. Return 1 when some files would be
                        reformatted. It can be used together with --diff.
  -i, --in-place        Format files in-place.
  --diff                Show diff on stdout for each formatted file instead. It can be
                        used together with --check.
  --print-config {minimal,verbose,default}
                        Print configuration for files. With "minimal" prints source of
                        outcome configuration (configuration file or defaults) and the
                        options that differ from defaults. With "verbose" prints source
                        of outcome configuration (configuration file or defaults), files
                        for which this configuration is applicable and complete listing
                        of options. With "default" prints outcome configuration with
                        default values. Command line arguments are taken into
                        consideration just as they would be for formatting. When
                        configuration file is found values in "definitions" are printed
                        as relative paths, otherwise absolute paths are printed. Output
                        can be placed in .gersemirc file verbatim.
  --version             Show version.
  -h, --help            Show this help message and exit.

outcome configuration:
  These arguments control how gersemi formats source code. Values for these arguments
  can be stored in .gersemirc file which can be placed in directory next to the source
  file or any parent directory. The highest priority has file provided through
  --config, then file closest to the source file, then file in parent directory etc.
  until root of file system is reached. Arguments from command line can be used to
  override parts of that stored configuration or supply them in absence of
  configuration file. Precedence: (command line arguments) > (configuration file) >
  (defaults)

  -l INTEGER, --line-length INTEGER
                        Maximum line length in characters. [default: 80]
  --indent (INTEGER | tabs)
                        Number of spaces used to indent or 'tabs' for indenting with
                        tabs [default: 4]
  --unsafe              Skip default sanity checks.
  --definitions src [src ...]
                        Files or directories containing custom command definitions
                        (functions or macros). If only - is provided custom definitions,
                        if there are any, are taken from stdin instead. Commands from
                        not deprecated CMake native modules don't have to be provided.
                        See: https://cmake.org/cmake/help/latest/manual/cmake-
                        modules.7.html
  --list-expansion {favour-inlining,favour-expansion}
                        Switch controls how code is expanded into multiple lines when
                        it's not possible to keep it formatted in one line. With
                        "favour-inlining" the list of entities will be formatted in such
                        way that sublists might still be formatted into single line as
                        long as it's possible or as long as it doesn't break the "more
                        than four standalone arguments" heuristic that's mostly focused
                        on commands like `set` or `list(APPEND)`. With "favour-
                        expansion" the list of entities will be formatted in such way
                        that sublists will be completely expanded once expansion becomes
                        necessary at all. [default: favour-inlining]
  --warn-about-unknown-commands, --no-warn-about-unknown-commands
                        When enabled file which has unknown custom commands will have
                        warnings issued about that and result won't be cached. See:
                        "Let's make a deal" section in README. [default: warnings
                        enabled, same as --warn-about-unknown-commands]
  --disable-formatting, --enable-formatting
                        Completely disable formatting. [default: formatting enabled]
  --extensions extension-name-or-path [extension-name-or-path ...]
                        Names of extension modules or paths to extension files. See:
                        "Extensions" section in README.

control configuration:
  These arguments control how gersemi operates rather than how it formats source code.
  Values for these options are not read from configuration file. Default values are
  used when the arguments aren't supplied. Precedence: (command line arguments) >
  (defaults)

  -q, --quiet, --no-quiet
                        Skip printing non-error messages to stderr.
                        [default: don't skip, same as --no-quiet]
  --color, --no-color   If --diff is selected showed diff is colorized. Colorama has to
                        be installed for this option to work.
                        [default: don't colorize diff, same as --no-color]
  -w (INTEGER | max), --workers (INTEGER | max)
                        Explicit number of workers or 'max' for maximum possible number
                        of workers on given machine used to format multiple files in
                        parallel. [default: max]
  --cache, --no-cache   Enables cache with data about files that are known to be
                        formatted to speed up execution.
                        [default: cache enabled, same as --cache]
  --config CONFIGURATION_FILE
                        Path to configuration file. When present this configuration file
                        will be used for determining configuration for all sources
                        instead of automatically found configuration files closest to
                        each of the sources. [default: omitted]
  --warnings-as-errors  Treat warnings as errors so that status code becomes 1 when at
                        least one warning would be issued. This option is not inhibited
                        by --quiet.

```
### [pre-commit](https://pre-commit.com/) hook

You can use gersemi with a pre-commit hook by adding the following to `.pre-commit-config.yaml` of your repository:

```yaml
repos:
- repo: https://github.com/BlankSpruce/gersemi
  rev: 0.20.1
  hooks:
  - id: gersemi
```

Update `rev` to relevant version used in your repository. For more details refer to https://pre-commit.com/#using-the-latest-version-for-a-repository

<details>
<summary><h3><b>Extensions in pre-commit hook</b></h3></summary>

If you want to use extensions with pre-commit list them with [`additional_dependencies`](https://pre-commit.com/#config-additional_dependencies). Example assuming that outcome configuration is in `.gersemirc`:

`.pre-commit-config.yaml`:
```yaml
repos:
- repo: https://github.com/BlankSpruce/gersemi
  rev: 0.20.1
  hooks:
  - id: gersemi
    additional_dependencies:
    - https://github.com/BlankSpruce/gersemi/extension-example/extension
```

`.gersemirc`:
```yaml
line_length: 123
extensions:
- extension_example
```

</details>

## Formatting

> [!IMPORTANT]
Changes to code might be destructive and you should always have a backup (version control helps a lot).

The key goals:
- Formatter should "just work" and should have as little configuration as possible so that you don't have to worry about fine-tuning formatter to your needs - as long as you embrace the `gersemi` style of formatting, similarly as `black` or `gofmt` do their job.
- Only valid CMake language code is considered - `gersemi` might be able to format some particular cases of invalid code but it's not guaranteed and it shouldn't be relied upon. 
- Only commands from CMake 3.0 onwards are supported and will be formatted properly - for instance [`exec_program` has been deprecated since CMake 3.0](https://cmake.org/cmake/help/latest/command/exec_program.html) so it won't be formatted. 
- Formatter can be informed about commands not supported out of the box:
  - through command definition (see: [Let's make a deal](#lets-make-a-deal))
  - through extensions (see: [Extensions](#extensions))

### Style

General goals:
- Canonical casing is used as it's defined in official CMake documentation like `FetchContent_Declare`. There are a few deliberate exceptions for which lower case name was chosen to provide broader consistency with other CMake commands. In case of unknown commands, not provided through `definitions`, lower case will be used.
- Arguments attached to certain multi-value keywords, like `PUBLIC`/`PRIVATE`/`INTERFACE` in `target_link_libraries`, are treated as an argument group and such group might introduce another level of indentation. It's meant to introduce a visual hint that certain arguments have different, specific meaning.
- Arguments that represent key-value pairs will be treated as such pairs.
  <details>
  <summary><b>It's applicable to:</b></summary>

  - `PROPERTIES` keyword in the following official commands:
    - `gtest_discover_test`
    - `set_directory_properties`
    - `set_package_properties`
    - `set_source_files_properties`
    - `set_target_properties`
    - `set_test_properties`
  - keyword in custom commands that has `pairs` hint (See: Let's make a deal).

  </details>
- Arguments that represent shell command-like sequence won't be expanded in multiple lines unless character limit for single line is reached. In case of expansion arguments not fitting in given line will be placed in the next one instead of putting each argument in its own line like it would happen for usual multi-value arguments.

  <details>
  <summary>Empty comments can be used to force some explicit expansions:</summary>

  ```cmake
  add_test(
      NAME foo
      COMMAND
          some_command --with-argument-one foo --with argument-two bar --with-some-option
          --with-another-option --with-another-another-option
  )
  add_test(
      NAME foo
      COMMAND
          some_command #
          --with-argument-one foo #
          --with argument-two bar #
          --with-some-option --with-another-option --with-another-another-option
  )
  ```

  </details>

  <details>
  <summary><b>It's applicable to:</b></summary>

  - `COMMAND` keyword in the following official commands:
    - `add_test`
    - `execute_process`
    - `env_module`
  - `COMMAND` and `ARGS` keywords in `add_custom_command`
  - `COMMAND` keyword and positional arguments of `add_custom_target`
  - `CMAKE_COMMAND_LINE` in `cmake_add_fortran_subdirectory`
  - `GCOV_OPTIONS` in `ctest_coverage_collect_gcov`
  - these keywords in `ExternalProject_Add`:
    - `DOWNLOAD_COMMAND`
    - `GIT_CONFIG`
    - `UPDATE_COMMAND`
    - `PATCH_COMMAND`
    - `CONFIGURE_COMMAND`
    - `CMAKE_ARGS`
    - `CMAKE_CACHE_ARGS`
    - `CMAKE_CACHE_DEFAULT_ARGS`
    - `BUILD_COMMAND`
    - `INSTALL_COMMAND`
    - `TEST_COMMAND`
    - `COMMAND`
  - these keywords in `FetchContent_Declare`:
    - `DOWNLOAD_COMMAND`
    - `UPDATE_COMMAND`
    - `PATCH_COMMAND`
  - `EXTRA_ARGS` and `DISCOVERY_EXTRA_ARGS` keywords in `gtest_discover_tests`
  - `MATLAB_ADDITIONAL_STARTUP_OPTIONS` in `matlab_add_unit_test`
  - keyword in custom commands that has `command_line` hint (See: Let's make a deal).
  </details>

#### Default style `favour-inlining`

`gersemi` will try to format the code in a way that respects set character limit for single line and only break line whenever necessary with one exception. The commands that have a group of parameters that aren't attached to any specific keyword (like `set` or `list(APPEND)`) will be broken into multiple lines when there are more than 4 arguments in that group. The exception to the rule is made as a heuristic to avoid large local diff when the given command won't fit into maximum line length:
```cmake
# Four elements in the list "Oceans_Eleven"
set(Oceans_Eleven Danny Frank Rusty Reuben)

# Five elements in the list "Oceans_Twelve"
set(Oceans_Twelve
    Danny
    Frank
    Rusty
    Reuben
    Tess
)
```
You can also force expansion by using an empty comment somewhere in the argument group that you intend to keep expanded:
```cmake
target_link_libraries(FOOBAR PUBLIC foo bar baz PRIVATE foo bar baz)

target_link_libraries(
    FOOBAR #
    PUBLIC foo bar baz
    PRIVATE foo bar baz
)

target_link_libraries(
    FOOBAR
    PUBLIC #
        foo
        bar
        baz
    PRIVATE foo bar baz
)
```
<details>
<summary><h4><b>Example</b></h4></summary>

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
</details>

#### Alternative style `favour-expansion`

In this style lines are broken in one of these cases:
- there is at least one multi-value argument present a single command invocation, either keyworded one like `PUBLIC` in `target_link_libraries` or standalone one like list of files in `add_library`, which has more than one value
- there are more than one multi-value arguments present in the command invocation like `target_link_libraries` with `PUBLIC` and `PRIVATE` arguments.
- character limit for single line is reached

One-value arguments (like `NAME` in `add_test`) will be inlined unless that'd violate character limit. Structure or control flow commands (`if`, `while`, `function`, `foreach` etc.) are exempted from these special rules and follow the same formatting as `favour-inlining`. This style is more merge or `git blame` friendly because usually multi-value arguments are changed one element at a time and with this style such change will be visible as one line of code per element.

<details>
<summary><h4><b>Example</b></h4></summary>

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

</details>

### Let's make a deal

It's possible to provide reasonable formatting for custom commands. However on language level there are no hints available about supported keywords for given command so `gersemi` has to generate specialized formatter. To do that custom command definition is necessary which should be provided with `--definitions`. There are limitations though since it'd probably require full-blown CMake language interpreter to do it in every case so let's make a deal: if your custom command definition (function or macro) uses `cmake_parse_arguments` and does it in obvious manner such specialized formatter will be generated. Name casing used in command definition will be considered canonical for custom command (in the example below canonical casing will be `Seven_Samurai`). For instance this definition is okay (you can find other examples in `tests/custom_command_formatting/`):
```cmake
function(Seven_Samurai some standalone arguments)
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
Seven_Samurai(
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

Otherwise `gersemi` will fallback to only fixing indentation of command name and it's closing parenthesis while preserving original formatting of arguments:
```cmake
# before formatting of unknown command
  watch_david_fincher_movies(
       "Se7en"
       "The Game"
         "Fight Club"
       "Zodiac"     "The Curious Case of Benjamin Button"
         )

# after
watch_david_fincher_movies(
       "Se7en"
       "The Game"
         "Fight Club"
       "Zodiac"     "The Curious Case of Benjamin Button"
)
```
If you find these limitations too strict let me know about your case.

When source code has custom commands but their definitions aren't known `gersemi` will warn about that. Warnings can be suppressed with `--no-warn-about-unknown-commands`/`warn_about_unknown_commands: false`.

#### How to format custom commands for which path to definition can't be guaranteed to be stable? (e.g external dependencies not managed by CMake)

You can either implement [extension](#extensions) or provide stub definitions that will be used only as an input for gersemi. Example of stub definition:
```yaml
# ./.gersemirc
definitions: [./src/cmake/stubs, ...] # ... other paths that might contain actual definitions
line_length: 120
list_expansion: favour-expansion
```

```cmake
# ./src/cmake/stubs/try_to_win_best_picture_academy_award.cmake
# A stub for some external command out of our control
function(try_to_win_best_picture_academy_award)
    # gersemi: hints { CAST: pairs, SUMMARY: command_line }
    set(options FOREIGN_LANGUAGE)
    set(oneValueArgs GENRE YEAR)
    set(multiValueArgs DIRECTORS CAST SUMMARY)

    cmake_parse_arguments(_ "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})
endfunction()
```

#### `gersemi: ignore`
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

#### `gersemi: hints`
If your definition has `# gersemi: hints` at the beginning then after `hints` you can provide YAML formatted pairs `<keyword>: <specialized_formatting>` to indicate how to treat specific multi-value arguments. `<specialized_formatting>` can be:
- `pairs`: values after the keyword will be grouped into pairs, similar to how `set_target_properties(PROPERTIES)` is handled
- `command_line`: values after the keyword will be treated like a sequence of words in command line, similar to how `add_custom_command(COMMAND)` is handled
- `sort`: values after the keyword will be sorted in alphabetical order
- `unique`: repeated values after the keyword will be removed during formatting
- `sort+unique`: values will be sorted and repetitions will be removed

<details>
<summary>Example:</summary>

```cmake
function(movie_description_without_hints)
set(options "")
set(oneValueArgs DIRECTOR)
set(multiValueArgs CAST SUMMARY)

cmake_parse_arguments(THIS_FUNCTION_PREFIX "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})
endfunction()

function(movie_description_with_hints)
# gersemi: hints { CAST: pairs, SUMMARY: command_line }
set(options "")
set(oneValueArgs DIRECTOR)
set(multiValueArgs CAST SUMMARY)

cmake_parse_arguments(THIS_FUNCTION_PREFIX "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})
endfunction()

movie_description_without_hints(
    Oppenheimer
    DIRECTOR "Christopher Nolan"
    CAST
        "J. Robert Oppenheimer"
        "Cillian Murphy"
        "Kitty Oppenheimer"
        "Emily Blunt"
        "General Leslie Groves"
        "Matt Damon"
    SUMMARY
        Oppenheimer
        is
        an
        epic
        biographical
        thriller
        directed
        by
        Christopher
        Nolan.
)

movie_description_with_hints(
    Oppenheimer
    DIRECTOR "Christopher Nolan"
    CAST
        "J. Robert Oppenheimer" "Cillian Murphy"
        "Kitty Oppenheimer" "Emily Blunt"
        "General Leslie Groves" "Matt Damon"
    SUMMARY
        Oppenheimer is an epic biographical thriller directed by Christopher
        Nolan.
)
```

</details>


### Extensions

You can extend gersemi capabilities through Python modules listed with `--extensions`(command line)/`extensions` (configuration file). Such extension has to:
- either:
  - be module installed in gersemi's environment that follows naming convention `gersemi_{extension module name}`,
  - be file that ends with `.py` extension, for example: `acme_corporation.py`
- implement `command_definitions` mapping, where key describes command in its canonical casing and value describes command properties,

> [!IMPORTANT]
> 1) Exact details on command properties are available in [extension example implementation](extension-example/extension/gersemi_extension_example/__init__.py).
> 2) It's possible to override or tweak builtin commands. Extension example shows how to do that with `target_sources` command example. Use with caution.

- pass verification done once during runtime that checks whether `command_definitions` follows some basic constraints like "keyworded arguments are strings", ["command names don't start with a digit"](https://cmake.org/cmake/help/latest/manual/cmake-language.7.html#grammar-token-identifier) etc.

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
