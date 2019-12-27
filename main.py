from formatter.parser import create_parser
from formatter.formatter import create_formatter
import argparse
import sys
import lark


def create_argparser():
    parser = argparse.ArgumentParser(description="Tool to format CMake code")
    parser.add_argument(
        dest="files",
        default=[sys.stdin],
        metavar="file",
        nargs="*",
        type=argparse.FileType("r"),
        help="file to format",
    )
    return parser


def main():
    argparser = create_argparser()
    args = argparser.parse_args()

    formatter = create_formatter(create_parser())

    for file_to_format in args.files:
        try:
            print(formatter.format(file_to_format.read()))
        except lark.UnexpectedInput:
            print(f"Invalid CMake file: {file_to_format.name}", file=sys.stderr)
            sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
