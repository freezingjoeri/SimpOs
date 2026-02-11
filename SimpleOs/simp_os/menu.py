from __future__ import annotations

"""
Simple arrow-key menu helper.

Gebruikt de pijltjestoetsen (omhoog/omlaag) en ENTER om een optie te kiezen.
"""

from typing import Iterable, List

from readchar import key, readkey

from .utils import PRIMARY, SYSTEM, clear_screen, print_colored


def select_menu(title: str, options: Iterable[str]) -> int | None:
    """
    Toon een menu en laat de gebruiker met pijltjes + ENTER kiezen.

    Returns:
        index (0-based) van de gekozen optie, of None als geannuleerd.
    """
    opts: List[str] = list(options)
    if not opts:
        return None

    index = 0
    while True:
        clear_screen()
        print_colored(title, color=PRIMARY)
        print()

        for i, opt in enumerate(opts):
            prefix = "➤ " if i == index else "  "
            color = PRIMARY if i == index else SYSTEM
            print_colored(f"{prefix}{opt}", color=color)

        print()
        print_colored("Gebruik ↑/↓ en ENTER. Druk op q om te annuleren.", color=SYSTEM)

        k = readkey()
        if k in (key.UP, "w"):
            index = (index - 1) % len(opts)
        elif k in (key.DOWN, "s"):
            index = (index + 1) % len(opts)
        elif k in (key.ENTER, "\n", "\r"):
            return index
        elif k in (key.ESC, "q"):
            return None

