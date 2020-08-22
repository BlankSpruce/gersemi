from dataclasses import astuple, dataclass
from pathlib import Path
from typing import Callable, TypeVar, Union
from gersemi.exceptions import ASTMismatch, ParsingError
from gersemi.utils import fromfile


T = TypeVar("T", covariant=True)


@dataclass
class Error:
    exception: Exception
    path: Path


Result = Union[T, Error]


def apply(function: Callable[..., T], path: Path, *args, **kwargs) -> Result[T]:
    try:
        return function(path, *args, **kwargs)
    except Exception as exception:  # pylint: disable=broad-except
        return Error(exception, path)


ERROR_MESSAGE_TEMPLATES = {
    ASTMismatch: "{path}: AST mismatch after formatting",
    ParsingError: "{path}:{exception}",
    UnicodeDecodeError: "{path}: file can't be read: {exception}",
}
FALLBACK_ERROR_MESSAGE_TEMPLATE = "{path}: runtime error, {exception}"


def get_error_message(error: Error) -> str:
    exception, path = astuple(error)
    message = FALLBACK_ERROR_MESSAGE_TEMPLATE
    for exception_type, template in ERROR_MESSAGE_TEMPLATES.items():
        if isinstance(exception, exception_type):
            message = template
            break
    return message.format(path=fromfile(path), exception=exception)
