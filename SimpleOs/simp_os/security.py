from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List

from .utils import ERROR, SYSTEM, print_colored


@dataclass
class SecurityLogEntry:
    timestamp: str
    user: str
    event: str


class SecurityManager:
    def __init__(self) -> None:
        self.failed_logins: int = 0
        self.logs: List[SecurityLogEntry] = []

    def log(self, user: str, event: str) -> None:
        entry = SecurityLogEntry(
            timestamp=datetime.utcnow().isoformat(timespec="seconds") + "Z",
            user=user,
            event=event,
        )
        self.logs.append(entry)

    def record_failed_login(self, username: str) -> None:
        self.failed_logins += 1
        self.log(username, "failed_login")
        print_colored(
            f"[SECURITY] Failed login attempts: {self.failed_logins}",
            color=ERROR,
        )

    def show_logs(self) -> None:
        if not self.logs:
            print_colored("[SECURITY] No logs yet.", color=SYSTEM)
            return
        print_colored("--- Security logs ---", color=SYSTEM)
        for entry in self.logs:
            print_colored(
                f"{entry.timestamp} | user={entry.user} | {entry.event}",
                color=SYSTEM,
            )

