from pathlib import Path
from gersemi.formatted_file import FormattedFile
from gersemi.formatter import Formatter
from gersemi.utils import smart_open


def get_newlines_style(code: str) -> str:
    crlf = "\r\n"
    if crlf in code:
        return crlf

    return "\n"


def translate_newlines_to_line_feed(code: str) -> str:
    return code.replace("\r\n", "\n").replace("\r", "\n")


def format_file(path: Path, formatter: Formatter) -> FormattedFile:
    with smart_open(path, "r", newline="") as f:
        code = f.read()

    newlines_style = get_newlines_style(code)
    code = translate_newlines_to_line_feed(code)
    formatted_code, warnings = formatter.format(code)

    return FormattedFile(
        before=code,
        after=formatted_code,
        newlines_style=newlines_style,
        path=path,
        warnings=warnings,
    )
