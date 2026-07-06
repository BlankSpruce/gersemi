from pathlib import Path
from typing import Sequence, Tuple
from gersemi.utils import fromfile

Position = Tuple[int, int]


def unknown_command_warning(
    command_name: str,
    positions: Sequence[Position],
    filepath: Path,
) -> str:
    filepath = fromfile(filepath)
    return "\n".join(
        [
            f"Warning: unknown command '{command_name}' used at:",
            *(f"{filepath}:{line}:{column}" for line, column in positions),
            "",
        ]
    )


def wrong_formatting_warning(filepath: Path) -> str:
    return f"{fromfile(filepath)} would be reformatted"
