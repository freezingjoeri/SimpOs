from __future__ import annotations

from typing import Callable, Dict, List
import subprocess
from pathlib import Path

from .ai import SimpAI
from .auth import AuthManager, User
from .config import SimpConfig, save_config, CONFIG_FILE
from .security import SecurityManager
from .system_info import show_system_info
from .utils import ERROR, PRIMARY, SYSTEM, clear_screen, print_colored


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
        self._register("apps", self._cmd_apps)
        self._register("home", lambda args: None)  # handled in kernel
        self._register("reset", self._cmd_reset)
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
                "home": "Return to home menu.",
                "reset": "Factory reset (clear config).",
                "apps": "Open apps manager.",
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
        print_colored("--- Admin menu ---", color=PRIMARY)
        print_colored("1) Show security logs", color=PRIMARY)
        print_colored("2) Set API key", color=PRIMARY)
        print_colored("3) Toggle online AI allowed", color=PRIMARY)
        print_colored("4) Show current config", color=PRIMARY)
        choice = input("Select option (ENTER to cancel): ").strip()
        if not choice:
            return
        if choice == "1":
            self.security.show_logs()
        elif choice == "2":
            key = input("New API key (empty to clear): ").strip()
            self.cfg.api_key = key or None
            save_config(self.cfg)
            print_colored("API key updated.", color=SYSTEM)
        elif choice == "3":
            self.cfg.allow_online_ai = not self.cfg.allow_online_ai
            save_config(self.cfg)
            print_colored(
                f"Online AI allowed: {self.cfg.allow_online_ai}",
                color=SYSTEM,
            )
        elif choice == "4":
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
        - Check for updates
        - Update from GitHub
        - Factory reset
        """
        print_colored("--- Settings ---", color=PRIMARY)
        print_colored("1) Server / OS info", color=PRIMARY)
        print_colored("2) Check for updates", color=PRIMARY)
        print_colored("3) Update from GitHub", color=PRIMARY)
        print_colored("4) Factory reset (clear config)", color=PRIMARY)
        choice = input("Select option (ENTER to cancel): ").strip()

        if not choice:
            return
        if choice == "1":
            show_system_info()
        elif choice == "2":
            self._settings_check_updates()
        elif choice == "3":
            self._settings_update()
        elif choice == "4":
            self._settings_reset()

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

    def _settings_check_updates(self) -> None:
        """
        Check of GitHub bereikbaar is en of er nieuwe commits zijn.
        """
        print_colored("Checking for updates...", color=SYSTEM)
        repo_dir = Path(__file__).resolve().parents[1]
        git_dir = repo_dir / ".git"
        if not git_dir.exists():
            print_colored(
                "This installation is not a Git clone. Cannot check for updates.",
                color=ERROR,
            )
            return

        try:
            # Haal laatste info binnen maar wijzig niets lokaal
            subprocess.run(
                ["git", "fetch", "--quiet"],
                cwd=str(repo_dir),
                check=True,
            )
        except subprocess.CalledProcessError:
            print_colored(
                "Could not reach Git remote. Check network or GitHub URL.",
                color=ERROR,
            )
            return

        # Vergelijk lokale HEAD met origin
        try:
            local = (
                subprocess.check_output(
                    ["git", "rev-parse", "HEAD"],
                    cwd=str(repo_dir),
                )
                .decode()
                .strip()
            )
            remote = (
                subprocess.check_output(
                    ["git", "rev-parse", "@{u}"],
                    cwd=str(repo_dir),
                )
                .decode()
                .strip()
            )
        except subprocess.CalledProcessError:
            print_colored(
                "Cannot compare with remote branch. Maybe no upstream is set.",
                color=ERROR,
            )
            return

        if local == remote:
            print_colored("You are up to date. No updates available.", color=SYSTEM)
        else:
            print_colored(
                "New updates are available. Run 'settings' → 'Update from GitHub' to apply them.",
                color=SYSTEM,
            )

    def _cmd_apps(self, args: List[str]) -> None:
        """
        Simple apps manager:
        - List apps in the 'apps' directory
        - Run an app
        - Install new app via custom shell command (advanced)
        """
        apps_dir = Path(__file__).resolve().parents[1] / "apps"
        apps_dir.mkdir(exist_ok=True)

        while True:
            print_colored("--- Apps ---", color=PRIMARY)
            files = sorted(
                [p for p in apps_dir.iterdir() if p.is_file() and not p.name.startswith(".")]
            )
            if not files:
                print_colored("No apps installed yet.", color=SYSTEM)
            else:
                print_colored("Installed apps:", color=SYSTEM)
                for idx, f in enumerate(files, start=1):
                    print_colored(f"{idx}) {f.name}", color=SYSTEM)

            print_colored("", color=SYSTEM)
            print_colored("a) Add/install app (run custom command in apps folder)", color=PRIMARY)
            print_colored("q) Back", color=PRIMARY)
            choice = input("Choose app number, 'a' or 'q': ").strip().lower()

            if choice == "q" or choice == "":
                break
            if choice == "a":
                print_colored(
                    "Custom install command will run in the 'apps' folder.",
                    color=SYSTEM,
                )
                cmd = input("Enter shell command (or ENTER to cancel): ").strip()
                if not cmd:
                    continue
                try:
                    subprocess.run(cmd, cwd=str(apps_dir), shell=True, check=True)
                    print_colored("Command finished. Check the app list above.", color=SYSTEM)
                except subprocess.CalledProcessError:
                    print_colored("Install command failed.", color=ERROR)
                continue

            # Try to run selected app
            try:
                idx = int(choice) - 1
            except ValueError:
                print_colored("Invalid choice.", color=ERROR)
                continue

            if idx < 0 or idx >= len(files):
                print_colored("Invalid app number.", color=ERROR)
                continue

            app_path = files[idx]
            print_colored(f"Running app: {app_path.name}", color=SYSTEM)

            try:
                if app_path.suffix == ".py":
                    subprocess.run(
                        ["python", str(app_path)],
                        cwd=str(apps_dir),
                        check=True,
                    )
                else:
                    subprocess.run(
                        ["bash", str(app_path)],
                        cwd=str(apps_dir),
                        check=True,
                    )
            except subprocess.CalledProcessError:
                print_colored("App exited with an error.", color=ERROR)

    def _settings_reset(self) -> None:
        """
        Factory reset: verwijdert config zodat first-time-setup opnieuw draait.
        """
        # Extra beveiliging: vereis expliciete admin-code
        print_colored("Admin verification required for factory reset.", color=ERROR)
        code = input("Enter admin code: ").strip()
        if code != self.cfg.admin_code:
            print_colored("Invalid admin code. Reset aborted.", color=ERROR)
            return

        print_colored(
            "This will delete SimpOs configuration (simp_config.json).",
            color=ERROR,
        )
        confirm = input("Type 'RESET' to confirm: ").strip()
        if confirm != "RESET":
            print_colored("Reset cancelled.", color=SYSTEM)
            return

        try:
            if CONFIG_FILE.exists():
                CONFIG_FILE.unlink()
        except OSError:
            print_colored(
                "Could not delete config file. Check permissions.",
                color=ERROR,
            )
            return

        print_colored(
            "Factory reset complete. Restart SimpOs to run first-time setup again.",
            color=SYSTEM,
        )

    def _cmd_reset(self, args: List[str]) -> None:
        """Direct command variant van factory reset."""
        self._settings_reset()

    def _stub_future(self, args: List[str]) -> None:
        print_colored(
            "[FUTURE] This command is reserved for the simulated file system.",
            color=SYSTEM,
        )

