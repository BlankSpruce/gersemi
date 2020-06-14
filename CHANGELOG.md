# Changelog

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
