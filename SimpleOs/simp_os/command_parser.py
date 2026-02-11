from __future__ import annotations

from typing import Callable, Dict, List
import subprocess
from pathlib import Path

from .ai import SimpAI
from .auth import AuthManager, User
from .config import SimpConfig, save_config
from .security import SecurityManager
from .system_info import show_system_info
from .utils import ERROR, PRIMARY, SYSTEM, clear_screen, print_colored
from .menu import select_menu


CommandHandler = Callable[[List[str]], None]


class CommandParser:
    def __init__(
        self,
        cfg: SimpConfig,
        ai: SimpAI,
        auth: AuthManager,
        security: SecurityManager,
        get_uptime: Callable[[], str],
    ) -> None:
        self.cfg = cfg
        self.ai = ai
        self.auth = auth
        self.security = security
        self.get_uptime = get_uptime
        self._commands: Dict[str, CommandHandler] = {}
        self._register_builtin_commands()

    # --- core -----------------------------------------------------------

    def _register(self, name: str, handler: CommandHandler) -> None:
        self._commands[name] = handler

    def handle_line(self, line: str) -> bool:
        """
        Parse a command line.

        Returns False if the kernel should shutdown, True otherwise.
        """
        line = line.strip()
        if not line:
            return True

        parts = line.split()
        cmd, args = parts[0].lower(), parts[1:]
        handler = self._commands.get(cmd)
        if not handler:
            print_colored(f"Unknown command: {cmd}", color=ERROR)
            return True

        if cmd == "shutdown":
            # handled here to allow clean exit
            return False

        handler(args)
        return True

    # --- built-in commands ---------------------------------------------

    def _register_builtin_commands(self) -> None:
        self._register("help", self._cmd_help)
        self._register("clear", self._cmd_clear)
        self._register("status", self._cmd_status)
        self._register("ai", self._cmd_ai)
        self._register("netstat", self._cmd_netstat)
        self._register("whoami", self._cmd_whoami)
        self._register("shutdown", lambda args: None)
        self._register("reboot", self._cmd_reboot)
        self._register("admin", self._cmd_admin)
        self._register("settings", self._cmd_settings)
        # Future expansion (stubs)
        self._register("mkdir", self._stub_future)
        self._register("touch", self._stub_future)
        self._register("ls", self._stub_future)

    # --- individual handlers -------------------------------------------

    def _cmd_help(self, args: List[str]) -> None:
        print_colored("Available commands:", color=PRIMARY)
        for name in sorted(self._commands.keys()):
            desc = {
                "help": "Show this help message.",
                "clear": "Clear the screen.",
                "status": "Show system status.",
                "ai": "Interact with SimpAI (ai local|online|status).",
                "netstat": "Show simulated network status.",
                "whoami": "Show current user.",
                "shutdown": "Power off SimpOs.",
                "reboot": "Reboot SimpOs.",
                "admin": "Admin tools (requires admin).",
                "mkdir": "[FUTURE] create directory.",
                "touch": "[FUTURE] create file.",
                "ls": "[FUTURE] list files.",
            }.get(name, "")
            print_colored(f"  {name:<10} {desc}", color=PRIMARY)

    def _cmd_clear(self, args: List[str]) -> None:
        clear_screen()

    def _cmd_status(self, args: List[str]) -> None:
        user: User | None = self.auth.current_user
        print_colored("--- System status ---", color=SYSTEM)
        print_colored(f"User   : {user.username if user else 'none'}", color=SYSTEM)
        print_colored(
            f"Priv   : {'admin' if (user and user.is_admin) else 'user'}",
            color=SYSTEM,
        )
        print_colored(f"Uptime : {self.get_uptime()}", color=SYSTEM)
        print_colored("Network: ONLINE (simulated)", color=SYSTEM)
        print_colored(f"AI mode: {self.cfg.ai_mode}", color=SYSTEM)

    def _cmd_ai(self, args: List[str]) -> None:
        if not args:
            question = input("SimpAI> ")
            self.ai.ask(question)
            return

        sub = args[0].lower()
        if sub == "local":
            self.ai.set_mode("local")
        elif sub == "online":
            # Admin gate will be enforced via config changes (admin command)
            self.ai.set_mode("online")
        elif sub == "status":
            self.ai.show_status()
        else:
            print_colored(
                "Usage: ai [local|online|status] or just 'ai' to ask a question.",
                color=ERROR,
            )

    def _cmd_netstat(self, args: List[str]) -> None:
        print_colored("--- Netstat (simulated) ---", color=SYSTEM)
        print_colored("Interface   Status   IP", color=SYSTEM)
        print_colored("lo          UP       127.0.0.1", color=SYSTEM)
        print_colored("eth0        UP       10.0.2.15", color=SYSTEM)
        print_colored("", color=SYSTEM)
        print_colored("Active connections:", color=SYSTEM)
        print_colored("tcp  0  0  10.0.2.15:1337  10.0.2.2:22  ESTABLISHED", color=SYSTEM)

    def _cmd_whoami(self, args: List[str]) -> None:
        user: User | None = self.auth.current_user
        if not user:
            print_colored("Not logged in.", color=ERROR)
            return
        print_colored(
            f"{user.username} ({'admin' if user.is_admin else 'user'})",
            color=PRIMARY,
        )

    def _cmd_reboot(self, args: List[str]) -> None:
        # The kernel will handle this by returning a special flag.
        raise SystemExit("REBOOT")  # handled by kernel loop

    def _cmd_admin(self, args: List[str]) -> None:
        if not self.auth.require_admin():
            return

        choice = select_menu(
            "--- Admin menu ---",
            [
                "Show security logs",
                "Set API key",
                "Toggle online AI allowed",
                "Show current config",
            ],
        )
        if choice is None:
            return
        if choice == 0:
            self.security.show_logs()
        elif choice == 1:
            key = input("New API key (empty to clear): ").strip()
            self.cfg.api_key = key or None
            save_config(self.cfg)
            print_colored("API key updated.", color=SYSTEM)
        elif choice == 2:
            self.cfg.allow_online_ai = not self.cfg.allow_online_ai
            save_config(self.cfg)
            print_colored(
                f"Online AI allowed: {self.cfg.allow_online_ai}",
                color=SYSTEM,
            )
        elif choice == 3:
            print_colored(
                f"admin_code       : (hidden)",
                color=SYSTEM,
            )
            print_colored(f"ai_mode          : {self.cfg.ai_mode}", color=SYSTEM)
            print_colored(
                f"api_key          : {'set' if self.cfg.api_key else 'not set'}",
                color=SYSTEM,
            )
            print_colored(
                f"allow_online_ai  : {self.cfg.allow_online_ai}",
                color=SYSTEM,
            )

    def _cmd_settings(self, args: List[str]) -> None:
        """
        Settings menu:
        - Server/OS info
        - Update from GitHub
        """
        choice = select_menu(
            "--- Settings ---",
            [
                "Server / OS info",
                "Update from GitHub",
            ],
        )

        if choice is None:
            return
        if choice == 0:
            show_system_info()
        elif choice == 1:
            self._settings_update()

    def _settings_update(self) -> None:
        """
        Update SimpOs code from a GitHub repo using git pull.
        Keeps config/data files (zoals simp_config.json) intact.
        """
        if not self.auth.require_admin():
            return

        current = self.cfg.update_repo_url or "https://github.com/freezingjoeri/SimpOs.git"
        print_colored(
            f"Current GitHub URL: {current}",
            color=SYSTEM,
        )
        url = input("GitHub repo URL (ENTER to keep current): ").strip() or current
        self.cfg.update_repo_url = url
        save_config(self.cfg)

        repo_dir = Path(__file__).resolve().parents[1]
        git_dir = repo_dir / ".git"
        if not git_dir.exists():
            print_colored(
                "This installation is not a Git clone. Update via GitHub is not possible here.",
                color=ERROR,
            )
            return

        print_colored(f"Updating from {url} ...", color=SYSTEM)
        try:
            subprocess.run(
                ["git", "remote", "set-url", "origin", url],
                cwd=str(repo_dir),
                check=True,
            )
            subprocess.run(
                ["git", "pull", "--ff-only"],
                cwd=str(repo_dir),
                check=True,
            )
        except subprocess.CalledProcessError:
            print_colored(
                "Update failed. Check the GitHub URL and network connection.",
                color=ERROR,
            )
            return

        print_colored(
            "Update complete. Restart SimpOs (reboot/shutdown) to use the new version.",
            color=SYSTEM,
        )

    def _stub_future(self, args: List[str]) -> None:
        print_colored(
            "[FUTURE] This command is reserved for the simulated file system.",
            color=SYSTEM,
        )

