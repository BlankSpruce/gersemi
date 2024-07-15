from dataclasses import dataclass
from typing import Iterable, Tuple


Position = Tuple[int, int]


@dataclass
class UnknownCommandWarning:
    command_name: str
    positions: Iterable[Position]

    def get_message(self, filepath: str) -> str:
        return "\n".join(
            [
                f"Warning: unknown command '{self.command_name}' used at:",
                *(f"{filepath}:{line}:{column}" for line, column in self.positions),
                "",
            ]
        )


class WrongFormattingWarning:
    def get_message(self, filepath: str) -> str:
        return f"{filepath} would be reformatted"


FormatterWarning = UnknownCommandWarning | WrongFormattingWarning
FormatterWarnings = Iterable[FormatterWarning]
