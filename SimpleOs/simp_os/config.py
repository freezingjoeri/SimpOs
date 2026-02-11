from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path

CONFIG_FILE = Path("simp_config.json")


@dataclass
class SimpConfig:
    admin_code: str = "changeme-admin"
    ai_mode: str = "local"  # "local" or "online"
    api_key: str | None = None
    allow_online_ai: bool = False
    update_repo_url: str | None = None
    owner_name: str | None = None
    first_run_completed: bool = False


def load_config() -> SimpConfig:
    if not CONFIG_FILE.exists():
        cfg = SimpConfig()
        save_config(cfg)
        return cfg

    try:
        data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except Exception:
        # Fallback to defaults on parse error
        cfg = SimpConfig()
        save_config(cfg)
        return cfg

    return SimpConfig(
        admin_code=data.get("admin_code", "changeme-admin"),
        ai_mode=data.get("ai_mode", "local"),
        api_key=data.get("api_key"),
        allow_online_ai=bool(data.get("allow_online_ai", False)),
        update_repo_url=data.get("update_repo_url"),
        owner_name=data.get("owner_name"),
        first_run_completed=bool(data.get("first_run_completed", False)),
    )


def save_config(cfg: SimpConfig) -> None:
    CONFIG_FILE.write_text(
        json.dumps(asdict(cfg), indent=2),
        encoding="utf-8",
    )

