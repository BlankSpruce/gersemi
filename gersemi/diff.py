from difflib import unified_diff
from pathlib import Path
from gersemi.utils import fromfile, tofile

try:
    from colorama import Fore, Style, init  # type: ignore

    init(strip=False)

    def colorize(diff):
        for line in diff:
            if line.startswith("+++") or line.startswith("---"):
                yield f"{Style.BRIGHT}{Fore.WHITE}{line}{Style.RESET_ALL}"
            elif line.startswith("@@"):
                yield f"{Fore.CYAN}{line}{Fore.RESET}"
            elif line.startswith("+"):
                yield f"{Fore.GREEN}{line}{Fore.RESET}"
            elif line.startswith("-"):
                yield f"{Fore.RED}{line}{Fore.RESET}"
            else:
                yield line

except ImportError:

    def colorize(diff):
        yield from diff


def get_diff(path: Path, should_colorize: bool, before: str, after: str) -> str:
    result = unified_diff(
        a=f"{before}\n".splitlines(keepends=True),
        b=f"{after}\n".splitlines(keepends=True),
        fromfile=fromfile(path),
        tofile=tofile(path),
        n=5,
    )
    if should_colorize:
        result = colorize(result)
    return "".join(result)
