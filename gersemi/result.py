from pathlib import Path
from gersemi.exceptions import ASTMismatch, ParsingError
from gersemi.utils import fromfile

ERROR_MESSAGE_TEMPLATES = {
    ASTMismatch: "{path}: AST mismatch after formatting",
    ParsingError: "{path}:{exception}",
    UnicodeDecodeError: "{path}: file can't be read: {exception}",
}
FALLBACK_ERROR_MESSAGE_TEMPLATE = "{path}: runtime error, {exception}"


def get_error_message(exception: Exception, path: Path) -> str:
    message = FALLBACK_ERROR_MESSAGE_TEMPLATE
    for exception_type, template in ERROR_MESSAGE_TEMPLATES.items():
        if isinstance(exception, exception_type):
            message = template
            break
    return message.format(path=fromfile(path), exception=exception)
