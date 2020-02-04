import argparse
from functools import partial
import pathlib
import sys
import lark
from gersemi.exceptions import ASTMismatch
from gersemi.formatter import create_formatter
from gersemi.parser import create_parser


SUCCESS = 0
REFORMATTING_REQUIRED = 1
INTERNAL_ERROR = 123


error = partial(print, file=sys.stderr)


def create_argparser():
    parser = argparse.ArgumentParser(description="Tool to format CMake code")
    parser.add_argument(
        "-c",
        "--check",
        dest="check_formatting",
        default=False,
        action="store_true",
        help="Check if files require reformatting. "
        "Return 0 when there's nothing to reformat, "
        "return 1 when some files would be reformatted",
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
        help="File to format. If no files are provided input is taken from stdin",
    )
    return parser


class Runner:  # pylint: disable=too-few-public-methods
    def __init__(self, formatter, args):
        self.formatter = formatter
        self.args = args

    def _check_formatting(self, before, after, filename):
        if before != after:
            error(f"{filename} would be reformatted")
            return REFORMATTING_REQUIRED
        return SUCCESS

    def _print(self, code, sink):
        print(code, file=sink, end="")


class StdinRunner(Runner):  # pylint: disable=too-few-public-methods
    def run(self):
        code_to_format = sys.stdin.read()
        try:
            formatted_code = self.formatter.format(code_to_format)
        except lark.UnexpectedInput as exception:
            # TODO detailed error description with match_examples
            error("Failed to parse: ", exception)
            return INTERNAL_ERROR
        except ASTMismatch:
            error("Failed to format: AST mismatch after formatting")
            return INTERNAL_ERROR

        if self.args.check_formatting:
            return self._check_formatting(
                before=code_to_format, after=formatted_code, filename="<stdin>"
            )

        self._print(formatted_code, sys.stdout)
        return SUCCESS


class FilesRunner(Runner):  # pylint: disable=too-few-public-methods
    def _run_on_single_file(self, file_to_format):
        with open(file_to_format, "r") as f:
            code_to_format = f.read()

        try:
            formatted_code = self.formatter.format(code_to_format)
        except lark.UnexpectedInput as exception:
            # TODO detailed error description with match_examples
            error("Failed to parse: ", exception)
            return INTERNAL_ERROR
        except ASTMismatch:
            error("Failed to format: AST mismatch after formatting")
            return INTERNAL_ERROR

        if self.args.check_formatting:
            return self._check_formatting(
                before=code_to_format, after=formatted_code, filename=file_to_format
            )

        if self.args.in_place:
            with open(file_to_format, "w") as f:
                self._print(formatted_code, sink=f)
        else:
            self._print(formatted_code, sink=sys.stdout)

        return SUCCESS

    def run(self):
        return max(map(self._run_on_single_file, self.args.files))


def main():
    argparser = create_argparser()
    args = argparser.parse_args()

    formatter = create_formatter(create_parser(), args.format_safely)

    if len(args.files) == 0:
        runner = StdinRunner(formatter, args)
    else:
        runner = FilesRunner(formatter, args)

    sys.exit(runner.run())


if __name__ == "__main__":
    main()
