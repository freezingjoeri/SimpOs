from __future__ import annotations

from dataclasses import dataclass

from .config import SimpConfig
from .security import SecurityManager
from .utils import ERROR, PRIMARY, print_colored


@dataclass
class User:
    username: str
    is_admin: bool = False


class AuthManager:
    def __init__(self, cfg: SimpConfig, security: SecurityManager) -> None:
        self.cfg = cfg
        self.security = security
        self.current_user: User | None = None

    def login(self) -> User | None:
        print_colored("Login to SimpOs", color=PRIMARY)
        username = input("Username: ").strip() or "guest"
        is_admin = username.lower() == "admin"

        if is_admin:
            code = input("Admin code: ").strip()
            if code != self.cfg.admin_code:
                print_colored("Invalid admin code.", color=ERROR)
                self.security.record_failed_login(username)
                return None
            self.current_user = User(username="admin", is_admin=True)
            self.security.log("admin", "admin_login")
            return self.current_user

        # Normal user, no password for now
        self.current_user = User(username=username, is_admin=False)
        self.security.log(username, "user_login")
        return self.current_user

    def require_admin(self) -> bool:
        """
        Verify admin access for sensitive actions.
        """
        if self.current_user and self.current_user.is_admin:
            return True
        print_colored("ACCESS DENIED – ADMIN CODE REQUIRED", color=ERROR)
        return False

