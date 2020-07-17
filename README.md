# gersemi

[![Build Status](https://travis-ci.com/BlankSpruce/gersemi.svg?token=jx3tcqsq9rGNwJNLQHdj&branch=master)](https://travis-ci.com/BlankSpruce/gersemi) [![License: MPL 2.0](https://img.shields.io/badge/License-MPL%202.0-brightgreen.svg)](https://opensource.org/licenses/MPL-2.0) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A formatter to make your CMake code the real treasure.

## Installation

You can install gersemi from PyPI:
```
$ pip3 install gersemi
```

## Usage

```
usage: gersemi [-h] [-c] [-i] [-l INTEGER] [--definitions src [src ...]]
               [--diff] [--unsafe] [--version]
               [src [src ...]]

A formatter to make your CMake code the real treasure.

positional arguments:
  src                   File or directory to format. If only - is provided
                        input is taken from stdin instead

optional arguments:
  -h, --help            show this help message and exit
  -c, --check           Check if files require reformatting. Return 0 when
                        there's nothing to reformat, return 1 when some files
                        would be reformatted
  -i, --in-place        Format files in-place
  -l INTEGER, --line-length INTEGER
                        Maximum line length in characters
  --definitions src [src ...]
                        Files or directories containing custom command
                        definitions (functions or macros). If only - is
                        provided custom definitions, if there are any, are
                        taken from stdin instead
  --diff                Show diff on stdout for each formatted file instead
  --unsafe              Skip default sanity checks
  --version             Show version.
```

## Formatting

The key goal is for the tool to "just work" and to have as little configuration as possible so that you don't have to worry about fine-tuning formatter to your needs - as long as you embrace the `gersemi` style of formatting, similarly as `black` or `gofmt` do their job. Currently only line length can be changed with `80` as default value - this default might be subject to change as project progresses. Currently the basic assumption is that code to format is valid CMake language code - `gersemi` might be able to format some particular cases of invalid code but it's not guaranteed and it shouldn't be relied upon. Be warned though it's not production ready so the changes to code might be destructive and you should always have a backup (version control helps a lot).

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
