from itertools import repeat
from typing import Iterator


def prefix(text: str, prefixes: Iterator[str]) -> str:
    lines = []
    for p, line in zip(prefixes, text.split("\n")):
        if line == "":
            lines.append("")
        else:
            lines.append(p + line)
    return "\n".join(lines)


def indent(text: str, width: int) -> str:
    return prefix(text, prefixes=repeat(" " * width))
