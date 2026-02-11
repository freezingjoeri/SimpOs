from __future__ import annotations

import os
import platform
import socket
from datetime import datetime

from .utils import SYSTEM, print_colored


def show_system_info() -> None:
    """
    Print server / OS info (host, distro, kernel, Python, etc.).
    Works on Ubuntu, andere Linuxen en ook op Windows.
    """
    print_colored("--- Server / OS info ---", color=SYSTEM)

    print_colored(f"Hostname      : {socket.gethostname()}", color=SYSTEM)
    print_colored(f"Platform      : {platform.system()} {platform.release()}", color=SYSTEM)
    print_colored(f"Kernel        : {platform.version()}", color=SYSTEM)
    print_colored(
        f"Architecture  : {platform.machine()} ({platform.processor() or 'unknown'})",
        color=SYSTEM,
    )
    print_colored(f"Python        : {platform.python_version()}", color=SYSTEM)

    # Extra info waar beschikbaar
    if hasattr(os, "getloadavg"):
        try:
            load1, load5, load15 = os.getloadavg()
            print_colored(
                f"Load average  : {load1:.2f} {load5:.2f} {load15:.2f}",
                color=SYSTEM,
            )
        except OSError:
            pass

    print_colored(f"Time (UTC)    : {datetime.utcnow().isoformat(timespec='seconds')}Z", color=SYSTEM)

