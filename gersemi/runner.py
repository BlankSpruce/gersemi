from contextlib import contextmanager
from functools import partial
from difflib import unified_diff
from itertools import chain
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
            if filename == Path("-"):
                error("<stdin> would be reformatted")
            else:
                error(f"{filename} would be reformatted")
            return FAIL
        return SUCCESS

    def _show_diff(self, before, after, filename):
        fromfile = "<stdin>" if filename == Path("-") else str(filename)
        tofile = "<stdout>" if filename == Path("-") else str(filename)
        diff = unified_diff(
            a=f"{before}\n".splitlines(keepends=True),
            b=f"{after}\n".splitlines(keepends=True),
            fromfile=fromfile,
            tofile=tofile,
            n=5,
        )
        self._print("".join(diff), sink=sys.stdout)
        return SUCCESS

    def _print(self, txt, sink):
        print(txt, file=sink, end="")

    def _run_on_single_file(self, file_to_format):
        with smart_open(file_to_format, "r") as f:
            code_to_format = f.read()

        try:
            formatted_code = self.formatter.format(code_to_format)
        except lark.UnexpectedInput as exception:
            # TODO detailed error description with match_examples
            error(f"Failed to parse {file_to_format}: ", exception)
            return INTERNAL_ERROR
        except ASTMismatch:
            error(f"Failed to format {file_to_format}: AST mismatch after formatting")
            return INTERNAL_ERROR
        except lark.exceptions.VisitError as exception:
            error(f"Runtime error when formatting {file_to_format}: ", exception)
            return INTERNAL_ERROR

        if self.args.show_diff:
            return self._show_diff(
                before=code_to_format, after=formatted_code, filename=file_to_format
            )

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

    def _run_on_single_path(self, path):
        if path.is_dir():
            files_to_format = chain(
                path.rglob("CMakeLists.txt"), path.rglob("*.cmake"),
            )
        else:
            files_to_format = [path]
        return max(map(self._run_on_single_file, files_to_format))

    def run(self):
        return max(map(self._run_on_single_path, self.args.sources))
