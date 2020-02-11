import argparse
import pathlib
import sys
from gersemi.formatter import create_formatter
from gersemi.parser import create_parser
from gersemi.runner import Runner, error, SUCCESS, FAIL


def create_argparser():
    parser = argparse.ArgumentParser(
        description="A formatter to make your CMake code the real treasure.",
        prog="gersemi",
    )
    parser.add_argument(
        "-c",
        "--check",
        dest="check_formatting",
        default=False,
        action="store_true",
        help=f"Check if files require reformatting. "
        f"Return {SUCCESS} when there's nothing to reformat, "
        f"return {FAIL} when some files would be reformatted",
    )
    parser.add_argument(
        "-i",
        "--in-place",
        dest="in_place",
        default=False,
        action="store_true",
        help="Format files in-place",
    )
    parser.add_argument(
        "-l",
        "--line-length",
        metavar="INTEGER",
        dest="line_length",
        default=80,
        type=int,
        help="Maximum line length in characters",
    )
    parser.add_argument(
        "--diff",
        dest="show_diff",
        default=False,
        action="store_true",
        help="Show diff on stdout for each formatted file instead",
    )
    parser.add_argument(
        "--unsafe",
        dest="format_safely",
        default=True,
        action="store_false",
        help="Skip default sanity checks",
    )
    parser.add_argument(
        dest="sources",
        metavar="src",
        nargs="*",
        type=pathlib.Path,
        help="File or directory to format. "
        "If only - is provided input is taken from stdin instead",
    )
    return parser


def main():
    argparser = create_argparser()
    args = argparser.parse_args()

    formatter = create_formatter(create_parser(), args.format_safely, args.line_length)

    if len(args.sources) == 0:
        sys.exit(SUCCESS)

    if pathlib.Path("-") in args.sources and len(args.sources) != 1:
        error("Don't mix stdin with file input")
        sys.exit(FAIL)

    sys.exit(Runner(formatter, args).run())


if __name__ == "__main__":
    main()
