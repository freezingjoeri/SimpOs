from __future__ import annotations

import time
from pathlib import Path

from .ai import SimpAI
from .auth import AuthManager
from .command_parser import CommandParser
from .config import SimpConfig, load_config, save_config
from .menu import select_menu
from .security import SecurityManager
from .utils import PRIMARY, SYSTEM, clear_screen, print_colored, type_out


class SimpKernel:
    VERSION = "v0.1 Alpha"

    def __init__(self) -> None:
        self.cfg: SimpConfig = load_config()
        self.security = SecurityManager()
        self.auth = AuthManager(self.cfg, self.security)
        self.ai = SimpAI(self.cfg)
        self.start_time: float = time.time()

    # --- core lifecycle -------------------------------------------------

    def boot(self) -> None:
        """
        Boot sequence: logo, diagnostics, login, command loop.
        """
        while True:
            try:
                self._boot_once()
                break
            except SystemExit as exc:
                if str(exc) == "REBOOT":
                    # Loop again to reboot
                    continue
                # Real shutdown
                break

    def _boot_once(self) -> None:
        clear_screen()
        self._show_logo()
        self._first_run_setup_if_needed()
        self._run_boot_sequence()

        # Login loop
        user = None
        while user is None:
            user = self.auth.login()

        parser = CommandParser(
            cfg=self.cfg,
            ai=self.ai,
            auth=self.auth,
            security=self.security,
            get_uptime=self._uptime_str,
        )
        self._home_screen(parser)

    def shutdown(self) -> None:
        print_colored("SimpOs is now shutting down...", color=SYSTEM)

    # --- helpers --------------------------------------------------------

    def _show_logo(self) -> None:
        """
        Toon het ASCII‑logo uit simp_logo.txt.

        Je kunt dat bestand zelf aanpassen zonder code te wijzigen.
        """
        logo_path = Path(__file__).resolve().parents[1] / "simp_logo.txt"
        if logo_path.exists():
            for line in logo_path.read_text(encoding="utf-8").splitlines():
                print_colored(line, color=PRIMARY)
        else:
            # Fallback logo als het bestand ontbreekt
            fallback = [
                r"=== SimpOs ===",
            ]
            for line in fallback:
                print_colored(line, color=PRIMARY)
        print_colored(f"--- {self.VERSION} ---", color=PRIMARY)
        print()

    def _run_boot_sequence(self) -> None:
        steps = [
            ("Loading kernel modules", True),
            ("Initializing memory manager", True),
            ("Mounting virtual file systems", True),
            ("Checking AI module", True),
            ("Checking network interfaces", True),
        ]
        for label, ok in steps:
            type_out(f"{label}...", delay=0.01, end="")
            time.sleep(0.2)
            status = "[OK]" if ok else "[FAIL]"
            print_colored(status, color=SYSTEM)
            time.sleep(0.1)

        print()
        print_colored("System ready. Press ENTER to continue to login.", color=SYSTEM)
        input()

    def _uptime_str(self) -> str:
        seconds = int(time.time() - self.start_time)
        mins, secs = divmod(seconds, 60)
        hrs, mins = divmod(mins, 60)
        return f"{hrs:02d}:{mins:02d}:{secs:02d}"

    def _command_loop(self, parser: CommandParser) -> None:
        while True:
            user = self.auth.current_user
            prompt_user = user.username if user else "?"
            try:
                line = input(f"{prompt_user}@SimpOs:~$ ")
            except EOFError:
                break

            cmd = line.strip().lower()
            if cmd == "shutdown":
                break
            if cmd == "home":
                # terug naar home menu
                return

            cont = parser.handle_line(line)
            if not cont:
                break

    def _home_screen(self, parser: CommandParser) -> None:
        """
        Interactive home screen met logo en hoofdopties.
        """
        while True:
            clear_screen()
            self._show_logo()
            owner = self.cfg.owner_name or "User"
            print_colored(f"Welcome, {owner}. Use ↑/↓ and ENTER.", color=SYSTEM)

            options = [
                "Open command line",
                "Apps",
                "Settings",
                "Admin tools",
                "AI console",
                "Shutdown",
                "Reboot",
            ]
            choice = select_menu("--- Home ---", options)
            if choice is None:
                # q/ESC -> open command line, maar blijf in home-loop
                self._command_loop(parser)
                continue

            selected = options[choice]
            if selected == "Open command line":
                self._command_loop(parser)
                continue
            elif selected == "Apps":
                parser._cmd_apps([])  # type: ignore[attr-defined]
            elif selected == "Settings":
                parser._cmd_settings([])  # type: ignore[attr-defined]
            elif selected == "Admin tools":
                parser._cmd_admin([])  # type: ignore[attr-defined]
            elif selected == "AI console":
                parser._cmd_ai([])  # type: ignore[attr-defined]
            elif selected == "Shutdown":
                return
            elif selected == "Reboot":
                raise SystemExit("REBOOT")

    def _first_run_setup_if_needed(self) -> None:
        """
        Eerste keer dat SimpOs draait: basisprofiel en admin-code instellen.
        """
        if self.cfg.first_run_completed:
            return

        print_colored("=== First time setup ===", color=SYSTEM)
        owner = input("Your name (owner of this system): ").strip() or "owner"

        while True:
            new_code = input("Choose admin code (leave empty to keep default): ").strip()
            if not new_code:
                new_code = self.cfg.admin_code
            confirm = input("Confirm admin code: ").strip()
            if new_code != confirm:
                print_colored("Codes do not match, try again.", color=SYSTEM)
                continue
            self.cfg.admin_code = new_code
            break

        self.cfg.owner_name = owner
        self.cfg.first_run_completed = True
        save_config(self.cfg)

        print_colored(
            "Setup complete. You can change settings later via 'admin' and 'settings'.",
            color=SYSTEM,
        )
        input("Press ENTER to continue booting...")

