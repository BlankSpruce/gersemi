import argparse
import pathlib
import sys
from lark import __version__ as lark_version
from gersemi.runner import run, error, SUCCESS, FAIL
from gersemi.__version__ import __title__, __version__


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
        "--definitions",
        dest="definitions",
        metavar="src",
        default=[],
        nargs="+",
        type=pathlib.Path,
        help="Files or directories containing custom command definitions (functions or macros). "
        "If only - is provided custom definitions, if there are any, are taken from stdin instead",
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
    parser.add_argument(
        "--version",
        dest="show_version",
        default=False,
        action="store_true",
        help="Show version.",
    )
    return parser


def is_stdin_mixed_with_file_input(sources):
    return pathlib.Path("-") in sources and len(sources) != 1


def show_version():
    print(f"{__title__} {__version__}")
    print(f"lark {lark_version}")
    print(f"Python {sys.version}")


def main():
    argparser = create_argparser()
    args = argparser.parse_args()

    if args.show_version:
        show_version()
        sys.exit(SUCCESS)

    if any(map(is_stdin_mixed_with_file_input, [args.sources, args.definitions])):
        error("Don't mix stdin with file input")
        sys.exit(FAIL)

    sys.exit(run(args))


if __name__ == "__main__":
    main()
