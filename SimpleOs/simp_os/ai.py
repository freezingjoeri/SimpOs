from __future__ import annotations

from dataclasses import dataclass

from .config import SimpConfig, save_config
from .utils import AI_COLOR, ERROR, SYSTEM, print_colored


@dataclass
class AiStatus:
    mode: str
    last_action: str | None = None
    online_available: bool = False


class SimpAI:
    """
    Integrated AI module.

    Online capabilities are intentionally left as hooks, so the user can plug in
    their own API of choice.
    """

    def __init__(self, cfg: SimpConfig) -> None:
        self.cfg = cfg
        self.status = AiStatus(
            mode=cfg.ai_mode,
            last_action=None,
            online_available=bool(cfg.api_key and cfg.allow_online_ai),
        )

    # --- public API -----------------------------------------------------

    def show_status(self) -> None:
        print_colored("--- SimpAI status ---", color=SYSTEM)
        print_colored(f"Mode          : {self.status.mode}", color=SYSTEM)
        print_colored(
            f"Online allowed: {self.cfg.allow_online_ai} "
            f"(api_key={'set' if self.cfg.api_key else 'missing'})",
            color=SYSTEM,
        )
        print_colored(
            f"Last action   : {self.status.last_action or '-'}",
            color=SYSTEM,
        )

    def set_mode(self, mode: str) -> None:
        if mode not in {"local", "online"}:
            print_colored("Unknown AI mode. Use 'local' or 'online'.", color=ERROR)
            return

        if mode == "online" and not (self.cfg.allow_online_ai and self.cfg.api_key):
            print_colored(
                "Online mode not available. Admin must enable it and set API key.",
                color=ERROR,
            )
            return

        self.cfg.ai_mode = mode
        save_config(self.cfg)
        self.status.mode = mode
        self.status.last_action = f"Switched mode to {mode}"
        print_colored(f"SimpAI mode set to {mode}.", color=AI_COLOR)

    def ask(self, question: str) -> None:
        """
        Answer a question in the current mode.
        """
        if self.cfg.ai_mode == "online":
            self._handle_online(question)
        else:
            self._handle_local(question)

    # --- offline / online handlers --------------------------------------

    def _handle_local(self, question: str) -> None:
        """
        Very small built-in knowledge base.
        Extend or replace as you like.
        """
        q_lower = question.lower()
        if "help" in q_lower and "command" in q_lower:
            answer = (
                "In SimpOs you can type 'help' to list commands. "
                "Use 'status' for system info and 'ai status' for AI info."
            )
        elif "simpai" in q_lower:
            answer = (
                "SimpAI is the integrated assistant. It can run fully offline "
                "or, if enabled by an admin, connect to an online API."
            )
        else:
            answer = (
                "Offline mode: I only know a few things.\n"
                "Configure an online API and switch to 'ai online' "
                "for more powerful answers."
            )

        self.status.last_action = "local_answer"
        print_colored(answer, color=AI_COLOR)

    def _handle_online(self, question: str) -> None:
        """
        Online mode hook.

        This is where you plug in your own AI API (OpenAI, etc.).
        For now we just print a placeholder so you can see where to add code.
        """
        if not (self.cfg.allow_online_ai and self.cfg.api_key):
            print_colored(
                "ACCESS DENIED – ADMIN CODE REQUIRED or API key missing.",
                color=ERROR,
            )
            return

        # Placeholder behaviour
        print_colored(
            "[ONLINE AI] This is a placeholder. "
            "Implement your own API call in simp_os/ai.py:_handle_online().",
            color=AI_COLOR,
        )
        self.status.last_action = "online_placeholder"

