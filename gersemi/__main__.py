import argparse
import pathlib
import sys
from gersemi.formatter import create_formatter
from gersemi.parser import create_parser
from gersemi.runner import Runner, error, SUCCESS, FAIL


def create_argparser():
    parser = argparse.ArgumentParser(description="Tool to format CMake code")
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
        "--unsafe",
        dest="format_safely",
        default=True,
        action="store_false",
        help="Skip default sanity checks",
    )
    parser.add_argument(
        dest="files",
        metavar="file",
        nargs="*",
        type=pathlib.Path,
        help="File to format. If - is provided input is taken from stdin instead",
    )
    return parser


def main():
    argparser = create_argparser()
    args = argparser.parse_args()

    formatter = create_formatter(create_parser(), args.format_safely)

    if len(args.files) == 0:
        sys.exit(SUCCESS)

    if pathlib.Path("-") in args.files and len(args.files) != 1:
        error("Don't mix stdin with file input")
        sys.exit(FAIL)

    sys.exit(Runner(formatter, args).run())


if __name__ == "__main__":
    main()
