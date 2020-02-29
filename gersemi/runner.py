from contextlib import contextmanager
from functools import lru_cache, partial
from difflib import unified_diff
from itertools import chain
from pathlib import Path
import sys
import lark
from gersemi.exceptions import ASTMismatch, ParsingError
from gersemi.formatter import create_formatter
from gersemi.custom_command_dumper_generator import generate_custom_command_dumpers
from gersemi.parser import create_parser, create_parser_with_postprocessing


SUCCESS = 0
FAIL = 1
INTERNAL_ERROR = 123


error = partial(print, file=sys.stderr)


class StdinWrapper:  # pylint: disable=too-few-public-methods
    @staticmethod
    @lru_cache(maxsize=None)
    def read():
        return sys.stdin.read()


def standard_stream_open(mode):
    if mode is None or mode == "" or "r" in mode:
        return StdinWrapper()
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


def fromfile(path):
    return "<stdin>" if path == Path("-") else str(path)


def tofile(path):
    return "<stdout>" if path == Path("-") else str(path)


def get_newlines_style(code):
    crlf = "\r\n"
    if crlf in code:
        return crlf

    return "\n"


def translate_newlines_to_line_feed(code):
    return code.replace("\r\n", "\n").replace("\r", "\n")


class Runner:  # pylint: disable=too-few-public-methods
    def __init__(self, args):
        self.args = args
        self.bare_parser = create_parser()
        self.parser = create_parser_with_postprocessing(self.bare_parser)
        self.formatter = create_formatter(
            self.bare_parser,
            self.args.format_safely,
            self.args.line_length,
            self._generate_custom_command_dumpers(self.args.sources),
        )

    def _check_formatting(self, before, after, path):
        if before != after:
            error(f"{fromfile(path)} would be reformatted")
            return FAIL
        return SUCCESS

    def _show_diff(self, before, after, path):
        diff = unified_diff(
            a=f"{before}\n".splitlines(keepends=True),
            b=f"{after}\n".splitlines(keepends=True),
            fromfile=fromfile(path),
            tofile=tofile(path),
            n=5,
        )
        self._print("".join(diff), sink=sys.stdout)
        return SUCCESS

    def _print(self, txt, sink):
        print(txt, file=sink, end="")

    def _run_on_single_file(self, file_to_format):
        with smart_open(file_to_format, "r", newline="") as f:
            code_to_format = f.read()

        newlines_style = get_newlines_style(code_to_format)
        code_to_format = translate_newlines_to_line_feed(code_to_format)

        try:
            formatted_code = self.formatter.format(code_to_format)
        except ParsingError as exception:
            error(f"{fromfile(file_to_format)}{exception}")
            return INTERNAL_ERROR
        except ASTMismatch:
            error(
                f"Failed to format {fromfile(file_to_format)}: AST mismatch after formatting"
            )
            return INTERNAL_ERROR
        except lark.exceptions.VisitError as exception:
            error(f"Runtime error when formatting {file_to_format}: ", exception)
            return INTERNAL_ERROR

        if self.args.show_diff:
            return self._show_diff(
                before=code_to_format, after=formatted_code, path=file_to_format
            )

        if self.args.check_formatting:
            return self._check_formatting(
                before=code_to_format, after=formatted_code, path=file_to_format
            )

        if self.args.in_place:
            with smart_open(file_to_format, "w", newline=newlines_style) as f:
                self._print(formatted_code, sink=f)
        else:
            self._print(formatted_code, sink=sys.stdout)

        return SUCCESS

    def _get_files_to_format(self, path):
        if path.is_dir():
            return chain(path.rglob("CMakeLists.txt"), path.rglob("*.cmake"),)
        return [path]

    def _generate_custom_command_dumpers(self, paths):
        result = dict()

        for path in paths:
            for filepath in self._get_files_to_format(path):
                with smart_open(filepath, "r") as f:
                    code = f.read()

                    parse_tree = self.parser.parse(code)
                    result.update(generate_custom_command_dumpers(parse_tree))
        return result

    def _run_on_single_path(self, path):
        return max(map(self._run_on_single_file, self._get_files_to_format(path)))

    def run(self):
        return max(map(self._run_on_single_path, self.args.sources))
