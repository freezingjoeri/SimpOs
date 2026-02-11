import os
import sys
import time
from typing import Iterable

try:
    # Optional, improves Windows colour support
    import colorama

    colorama.just_fix_windows_console()
except Exception:
    colorama = None  # type: ignore


class Colors:
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    RESET = "\033[0m"

    BOLD = "\033[1m"


PRIMARY = Colors.GREEN  # neon green style
SYSTEM = Colors.CYAN
ERROR = Colors.RED
AI_COLOR = Colors.MAGENTA  # purple-ish


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def type_out(
    text: str,
    delay: float = 0.02,
    end: str = "\n",
    color: str | None = None,
) -> None:
    """
    Simple typing animation.
    """
    if color:
        sys.stdout.write(color)
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write(end)
    if color:
        sys.stdout.write(Colors.RESET)
    sys.stdout.flush()


def print_colored(text: str, color: str = PRIMARY, end: str = "\n") -> None:
    sys.stdout.write(f"{color}{text}{Colors.RESET}{end}")
    sys.stdout.flush()


def print_lines(lines: Iterable[str], color: str = PRIMARY) -> None:
    for line in lines:
        print_colored(line, color=color)

