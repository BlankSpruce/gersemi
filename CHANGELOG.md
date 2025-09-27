# Changelog
## [0.22.3] 2025-09-25
### Added
- Performance improvement.

## [0.22.2] 2025-09-10
### Fixed
- Relative paths work with `--config`.

## [0.22.1] 2025-08-05
### Fixed
- Parsing regression regarding files with empty lines at the edges.

## [0.22.0] 2025-08-04
### Added
- Support custom block-like pair of commands. (#67)
- Hints in custom commands can be listed in multiple line comments to improve readability.

## [0.21.0] 2025-07-16
### Added
- Trim whitespaces at the end of line comments except for comments inside list of arguments of unknown command. (#64)

## [0.20.1] 2025-07-09
### Fixed
- Proper line breaking for `FILE_SET` keyword in `target_sources`. (#63)

## [0.20.0] 2025-06-30
### Added
- Support extension files.
- Support `sort`, `unique` and `sort+unique` hints for custom commands.
- Support overriding and tweaking builtin commands through extensions.
- Support for new keywords in native commands available in CMake 4.1.

### Fixed
- Proper formatting of `FILE_SET` and associated keywords in `target_sources`.

## [0.19.3] 2025-05-01
### Fixed
- Canoncial casing of `ExternalProject_Add_StepDependencies` and `ExternalProject_Add_StepTargets`. (#61)

## [0.19.2] 2025-03-05
### Added
- Support for new keywords in native commands available in CMake 4.0.

### Fixed
- Correctly recognize multi value keywords of `protobuf_generate`.

## [0.19.1] 2025-02-14
### Fixed
- Make `--diff` usable with `--check`. (#58)

## [0.19.0] 2025-02-10
### Added
- Add `--warnings-as-errors`. (#57)

## [0.18.2] 2025-01-17
### Fixed
- Fix "unknown command" regression. (#52)

## [0.18.1] 2025-01-13
### Fixed
- Proper formatting of first `<artifact-option>...` group in `INSTALL(TARGETS)` command. (#51)

## [0.18.0] 2025-01-10
### Added
- Add support for extensions and provide example extension as a template.

### Fixed
- Recognize `unquoted_legacy` rule of CMake language. (#49)
- Cut down excessive memory usage when used on a project with big number of files.
- Correctly recognize keywords from download, upload and patch steps of `ExternalProject_Add` in `FetchContent_Declare`. (#50)

## [0.17.1] 2024-11-29
### Fixed
- fix `--no-quiet` (#43)

## [0.17.0] 2024-10-26
### Added
- Add `disable_formatting`. (#35)
- `--config` can be used to provide explicit path to configuration file. (#35)
- Add `--print-config` to print outcome configuration in one of three variants: minimal, verbose, default. (#35)
- Warn about options not supported through configuration file.

### Changed
- Configuration has been split into two kinds: outcome and control. Outcome configuration can be changed through either configuration file or command line arguments whereas control configuration be changed only through command line.
- Search strategy for `.gersemirc` file has been changed so that the file closest to given source file is picked instead of using `.gersemirc` that it the most commont among files passed to gersemi.
- `--default-config` is removed because its functionality is subsumed by `--print-config default`.
- `cache`, `color`, `quiet` and `workers` can be changed only through command line.

### Fixed
- custom command definitions nested inside other definitions are picked as well (#39)
- colors stripping when output is redirected (#40)

## [0.16.2] 2024-10-15
### Fixed
- support missing keywords in `file(MAKE_DIRECTORY)` (#38)
- support missing keywords in `try_compile`
- add support for experimental `install(PACKAGE_INFO)`

## [0.16.1] 2024-10-14
### Added
- support for new keywords in native commands available in CMake 3.31

### Fixed
- incorrect keywords in `bison_target` and `flex_target` (#37)

## [0.16.0] 2024-10-11
### Changed
- removed dependency to `dataclasses` package (#36)
- supported Python versions changed from `>= 3.6` to `>= 3.8`
- number of workers can now be specified with either integer or "max", default value will now be "max" instead of numerical value of max on given machine

## [0.15.1] 2024-08-19
### Fixed
- when source or definition path doesn't exist `gersemi` will fail early

## [0.15.0] 2024-08-04
### Added
- cache can be disabled through `--no-cache`/`cache: false`, cache is still enabled by default
- warnings about unknown commands can be suppressed through `--no-warn-about-unknown-commands`/`warn_about_unknown_commands: false`, warnings are enabled by default

### Fixed
- only those files that were checked or formatted without warning will be cached

## [0.14.0] 2024-07-15
### Added
- warnings about unknown commands when `quiet` isn't used

### Changed
- document the intent of only formatting command name and closing parenthesis in "Let's make a deal" section of README

### Fixed
- `set_property` formatting

## [0.13.6] 2024-07-10
### Fixed
- non-deterministic formatting regression (#32)

## [0.13.5] 2024-06-29
### Fixed
- improve consistency of `add_executable`

## [0.13.4] 2024-06-29
### Fixed
- improve consistency of `target_link_libraries`

## [0.13.3] 2024-06-15
### Added
- support for new keywords in native commands available in CMake 3.30

## [0.13.2] 2024-06-11
### Fixed
- fix issue with cached results interfering with stdout mode

## [0.13.1] 2024-06-01
### Fixed
- fix issue with messing up whitespaces in between arguments of unknown custom commands

## [0.13.0] 2024-06-01
### Added
- support for using canonical casing of custom commands (#21)

### Changed
- official CMake commands will be formatted with their canonical casing (like `FetchContent_Declare`) instead of lower case version with the following deliberate exceptions:
    - `check_fortran_function_exists`
    - `check_include_file_cxx`
    - `check_include_file`
    - `check_include_files`
    - `check_library_exists`
    - `check_struct_has_member`
    - `check_variable_exists`

### Fixed
- use specialized formatting of some previously omitted official commands
- improve consistency of `set_package_properties` with similar commands
- fix formatting of first command in `add_custom_target` (#24)
- fix incorrect detection of sections in commands like `install` (#26)

## [0.12.1] 2024-03-27
- improve `find_package` formatting around `REQUIRED` keyword (#20)

## [0.12.0] 2024-03-26
### Added
- support for different kinds of indentation, either specific number of spaces or tabs through `--indent` argument (examples: `--indent=2` or `--indent=tabs`) or `indent` entry in `.gersemirc` (examples: `indent: 2` or `indent: tabs`) (#15)
- support for hints in custom command definition for specialized formatting, currently supported are `command_line` and `pairs`

### Changed
- formatting of `install` command will now correctly recognize sections like `RUNTIME`, `ARCHIVE`, `FILE_SET` etc. (#19)

### Fixed
- inconsistent formatting of `add_library` (#17)
- edge cases of comments present in `COMMAND` argument of `add_custom_command` and similar commands
- improve README and help about heuristic used in `favour-inlining` style (#18)

## [0.11.1] 2024-03-04
### Added
- support for new keywords in native commands and new commands available in CMake 3.29

### Fixed
- fix issue with comments in `COMMAND` argument of `add_custom_command` (#16)

## [0.11.0] 2024-01-11
### Added
- Number of workers spawned for formatting multiple files can be changed with `-w/--workers`. By default it will be number of CPUs available in the system but limited to 60 for Windows machines due to [this](https://github.com/python/cpython/issues/89240).

## [0.10.0] 2023-12-22
### Added
- configuration schema that can be used with yaml LSP server, see: [JSON Schema](https://json-schema.org/) and #12
- yaml header linking to configuration schema in configuration produced by `--default-config`
- support for Python 3.12

### Fixed
- meaningless but syntactically valid `target_link_libraries` with just library name won't crash gersemi (#13)

## [0.9.4] 2023-12-17
### Added
- support for new keywords in native commands available in CMake 3.28

## [0.9.3] 2023-10-18
### Fixed
- warn about conflicting definitions for macros and functions, make usage of conflicting definitions consistent and deterministic (#11)

## [0.9.2] 2023-06-15
### Changed
- allow PyYAML version 6 as a dependency

## [0.9.1] 2023-06-15
### Added
- support for new keywords in native commands available in CMake 3.27

## [0.9.0] 2023-05-02
### Added
- Support for alternative style that favours list expansion for multi-value arguments (keyworded or standalone) through `--list-expansion=favour-expansion` command line argument or `list_expansion: favour-expansion` entry in `.gersemirc`. The explanation of the new style is available in the README. The original formatting style will be still the default one but it can be set explicitly through `--list-expansion=favour-inlining` or `list_expansion: favour-inlining`.

## [0.8.3] 2023-03-04
### Added
- support for new keywords in native commands available in CMake 3.26

## [0.8.2] 2022-10-12
### Added
- support for block/endblock pair
- support for new keywords in native commands available in CMake 3.25

## [0.8.1] 2022-06-17
### Added
- support for new keywords in native commands available in CMake 3.24

## [0.8.0] 2022-02-24
### Added
- support for new keywords in native commands available in CMake 3.23
- support Python 3.10

### Changed
- required version of lark has to be at least 1.0

### Fixed
- AST mismatch issue when reformatting unknown commands with comment inside arguments list

## [0.7.5] 2021-12-11

### Fixed
- specialized dumper for commands with multiple signatures like `file` no longer leaks keywords (#6)

## [0.7.4] 2021-11-22

### Added
- [pre-commit](https://pre-commit.com/) hook

## [0.7.3] 2021-11-19

### Added
- support for new keywords in native commands available in CMake 3.22

## [0.7.2] 2021-07-16

### Added
- support for new keywords in native commands available in CMake 3.21
- relaxed lark version dependency

## [0.7.1] 2021-03-25

### Added
- support for new keywords in native commands available in CMake 3.20

## [0.7.0] 2021-02-19

###  Changed
- when input is provided through stdin `gersemi` will look for configuration file in current or any of the parent directories instead of only current directory

## [0.6.1] 2020-12-29

### Fixed
- on Python 3.6 sqlite related TypeError isn't raised anymore

## [0.6.0] 2020-11-19

### Added
- information about formatted files is cached so that subsequent runs can avoid processing already formatted files
- support for commands introduced between 3.16 and 3.19 releases of CMake

### Changed
- minor change to how OUTPUT argument in file(GENERATE) is formatted

## [0.5.0] 2020-08-25

### Added
- minor performance improvements
- support for Python 3.6

### Changed
- files are taken as input only once even if provided multiple times
- files are no longer overwritten if reformatting wouldn't lead to change of content
- removed dependency to `packaging`

## [0.4.0] 2020-08-05

### Added
- some performance improvements
- relaxed dependency to lark so that 0.9 can be used as well
- loading configuration from `.gersemirc` but command line arguments still take precedence
- colorized diffs with `--color`

### Fixed
- comments no longer interfere in splitting arguments by keywords which led to undesired formatting (#1)

## [0.3.1] 2020-07-20

### Fixed
- line comments in unknown custom commands are preserved in their original form
- fail-safe for AST mismatch (between before and after reformatting) now properly reports file where the problem occured

## [0.3.0] 2020-07-18

### Added
- utilize multiple cores if avaiable through `multiprocessing` module
- use `--quiet` to suppress non-error message on stderr
- support for commands from `cmake-modules` section of CMake documentation
- support formatting of custom commands without keyworded arguments
- custom command definitions can be marked now with `# gersemi: ignore` to suppress generating specialized formatter for these commands

### Changed
- commands with `PROPERTIES` keyword such as `set_directory_properties` now are formatted in uniform way as other commands with keyworded arguments

### Fixed
- idempotence of preserving formatting of unknown custom commands

## [0.2.2] 2020-06-23

### Fixed
- fixed condition syntax formatting edge-case with opening parenthesis indentation

## [0.2.1] 2020-06-20

### Fixed
- Missing value for one value keyword no longer leads to stopping formatting of remaining files in the batch

## [0.2.0] 2020-06-14

### Added
- custom commands formatting when definitions of these commands are provided with `--definitions`
- preserving CRLF style of newlines if formatted file used that style
- `--version`
- performance improvements

### Fixed
- bracket argument / bracket comment parsing bugfixes
- removed strict dependency to lark `0.8.0`, now anything from `0.8` but below `0.9` should work

## [0.1.2] 2020-02-14

### Changed
- formatting of COMMAND keyworded arguments look better when wrapped to line (or multiple lines) instead of listing each constituent of command in separate line

## [0.1.1] 2020-02-13

### Added
- added missing CHANGELOG
- some basic parsing error reporting

### Fixed
- bracket argument candidate which was not closed with proper ending bracket was interpreted as unquoted argument instead of being treated as parsing error

## [0.1.0] 2020-02-11

- first release of `gersemi` which should do some nice formatting
- using [SemVer](https://semver.org/)
