from contextlib import contextmanager
from functools import partial
from pathlib import Path
import sys
import lark
from gersemi.exceptions import ASTMismatch


SUCCESS = 0
FAIL = 1
INTERNAL_ERROR = 123


error = partial(print, file=sys.stderr)


def standard_stream_open(mode):
    if mode is None or mode == "" or "r" in mode:
        return sys.stdin
    return sys.stdout


@contextmanager
def smart_open(filename, mode, *args, **kwargs):
    if filename == Path("-"):
        try:
            yield standard_stream_open(mode)
        finally:
            pass
    else:
        try:
            fh = open(filename, mode, *args, **kwargs)
            yield fh
        finally:
            fh.close()


class Runner:  # pylint: disable=too-few-public-methods
    def __init__(self, formatter, args):
        self.formatter = formatter
        self.args = args

    def _check_formatting(self, before, after, filename):
        if before != after:
            error(f"{filename} would be reformatted")
            return FAIL
        return SUCCESS

    def _print(self, code, sink):
        print(code, file=sink, end="")

    def _run_on_single_file(self, file_to_format):
        with smart_open(file_to_format, "r") as f:
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
            with smart_open(file_to_format, "w") as f:
                self._print(formatted_code, sink=f)
        else:
            self._print(formatted_code, sink=sys.stdout)

        return SUCCESS

    def run(self):
        return max(map(self._run_on_single_file, self.args.files))
