from dataclasses import dataclass
from pathlib import Path
from typing import Union
from lark.exceptions import VisitError as LarkVisitError
from gersemi.exceptions import ParsingError
from gersemi.formatter import Formatter
from gersemi.utils import smart_open


@dataclass
class FormattedFile:
    before: str
    after: str
    newlines_style: str
    path: Path


@dataclass
class Error:
    exception: Exception
    path: Path


Result = Union[FormattedFile, Error]


def get_newlines_style(code: str) -> str:
    crlf = "\r\n"
    if crlf in code:
        return crlf

    return "\n"


def translate_newlines_to_line_feed(code: str) -> str:
    return code.replace("\r\n", "\n").replace("\r", "\n")


def format_file_impl(path: Path, formatter: Formatter) -> FormattedFile:
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


def format_file(path: Path, formatter: Formatter) -> Result:
    try:
        return format_file_impl(path, formatter)
    except (UnicodeError, ParsingError, LarkVisitError) as exception:
        return Error(exception, path)
