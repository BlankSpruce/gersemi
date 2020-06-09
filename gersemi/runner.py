from contextlib import contextmanager
from dataclasses import dataclass
from difflib import unified_diff
from functools import lru_cache, partial
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


def _print(txt, sink):
    print(txt, file=sink, end="")


def get_files(paths):
    def get_files_from_single_path(path):
        if path.is_dir():
            return chain(path.rglob("CMakeLists.txt"), path.rglob("*.cmake"),)
        return [path]

    for path in paths:
        for item in get_files_from_single_path(path):
            yield item


def has_custom_command_definition(code):
    lowercased = code.lower()
    has_function_definition = "function" in lowercased and "endfunction" in lowercased
    has_macro_definition = "macro" in lowercased and "endmacro" in lowercased
    return has_function_definition or has_macro_definition


def save_read(filepath):
    try:
        with smart_open(filepath, "r") as f:
            return f.read()
    except UnicodeDecodeError as exception:
        error(f"File {fromfile(filepath)} can't be read: ", exception)
        return None


def generate_specialized_dumpers(bare_parser, paths):
    parser = create_parser_with_postprocessing(bare_parser)
    result = dict()
    for filepath in get_files(paths):
        code = save_read(filepath)
        if code is None or not has_custom_command_definition(code):
            continue

        try:
            parse_tree = parser.parse(code)
            result.update(generate_custom_command_dumpers(parse_tree))
        except ParsingError as exception:
            error(f"{fromfile(filepath)}{exception}")
        except lark.exceptions.VisitError as exception:
            error(
                f"Runtime error when interpretting {fromfile(filepath)}: ", exception,
            )
    return result


@dataclass
class FormattedFile:
    before: str
    after: str
    newlines_style: str
    path: Path


def format_file(path, formatter):
    with smart_open(path, "r", newline="") as f:
        code = f.read()

    newlines_style = get_newlines_style(code)
    code = translate_newlines_to_line_feed(code)
    return FormattedFile(
        before=code,
        after=formatter.format(code),
        newlines_style=newlines_style,
        path=path,
    )


def show_diff(formatted_file):
    diff = unified_diff(
        a=f"{formatted_file.before}\n".splitlines(keepends=True),
        b=f"{formatted_file.after}\n".splitlines(keepends=True),
        fromfile=fromfile(formatted_file.path),
        tofile=tofile(formatted_file.path),
        n=5,
    )
    _print("".join(diff), sink=sys.stdout)
    return SUCCESS


def check_formatting(formatted_file):
    if formatted_file.before != formatted_file.after:
        error(f"{fromfile(formatted_file.path)} would be reformatted")
        return FAIL
    return SUCCESS


def format_in_place(formatted_file):
    with smart_open(
        formatted_file.path, "w", newline=formatted_file.newlines_style
    ) as f:
        _print(formatted_file.after, sink=f)
    return SUCCESS


def format_and_print_to_stdout(formatted_file):
    _print(formatted_file.after, sink=sys.stdout)
    return SUCCESS


def select_executor(args):
    if args.show_diff:
        return show_diff
    if args.check_formatting:
        return check_formatting
    if args.in_place:
        return format_in_place
    return format_and_print_to_stdout


def execute_on_single_file(file_to_format, formatter, execute):
    try:
        formatted_file = format_file(file_to_format, formatter)
        return execute(formatted_file)
    except ParsingError as exception:
        error(f"{fromfile(file_to_format)}{exception}")
    except ASTMismatch:
        error(
            f"Failed to format {fromfile(file_to_format)}: AST mismatch after formatting"
        )
    except lark.exceptions.VisitError as exception:
        error(f"Runtime error when formatting {fromfile(file_to_format)}: ", exception)
    return INTERNAL_ERROR


def run(args):
    bare_parser = create_parser()
    formatter = create_formatter(
        bare_parser,
        args.format_safely,
        args.line_length,
        generate_specialized_dumpers(bare_parser, args.sources),
    )
    run_on_single_file = partial(
        execute_on_single_file, formatter=formatter, execute=select_executor(args)
    )
    return max(map(run_on_single_file, get_files(args.sources)))
