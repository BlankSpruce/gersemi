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
usage: gersemi [-h] [-c] [-i] [-l INTEGER] [--diff] [--unsafe] [src [src ...]]

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
  --diff                Show diff on stdout for each formatted file instead
  --unsafe              Skip default sanity checks
```

## Formatting

The key goal is for the tool to "just work" and to have as little configuration as possible so that you don't have to worry about fine-tuning formatter to your needs - as long as you embrace the `gersemi` style of formatting, similarly as `black` or `gofmt` do their job. Currently only line length can be changed with `80` as default value - this default might be subject to change as project progresses. Currently the basic assumption is that code to format is valid CMake language code - `gersemi` might be able to format some particular cases of invalid code but it's not guaranteed and it shouldn't be relied upon. Be warned though it's not production ready so the changes to code might be destructive and you should always have a backup (version control helps a lot).

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
