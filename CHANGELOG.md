# Changelog

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
