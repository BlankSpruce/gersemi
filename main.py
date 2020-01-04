from formatter.parser import create_parser
from formatter.formatter import create_formatter
import argparse
import pathlib
import sys
import lark


def create_argparser():
    parser = argparse.ArgumentParser(description="Tool to format CMake code")
    parser.add_argument(
        "-i",
        "--in-place",
        dest="in_place",
        default=False,
        action="store_true",
        help="format files in-place",
    )
    parser.add_argument(
        dest="files",
        metavar="file",
        nargs="*",
        type=pathlib.Path,
        help="file to format",
    )
    return parser


def format_code(formatter, code, sink):
    try:
        print(formatter.format(code), file=sink)
    except lark.UnexpectedInput as exception:
        # TODO detailed error description with match_examples
        print(exception, file=sys.stderr)
        sys.exit(1)


def format_code_from_stdin(formatter):
    code = sys.stdin.read()
    format_code(formatter, code, sys.stdout)


def main():
    argparser = create_argparser()
    args = argparser.parse_args()

    formatter = create_formatter(create_parser())

    if len(args.files) == 0:
        format_code_from_stdin(formatter)
        return

    for file_to_format in args.files:
        with open(file_to_format, "r") as f:
            code = f.read()

        if args.in_place:
            with open(file_to_format, "w") as f:
                format_code(formatter, code, f)
        else:
            format_code(formatter, code, sys.stdout)


if __name__ == "__main__":
    main()
    sys.exit(0)
