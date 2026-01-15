from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

import yaml


def get_repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Loads YAML config.

    Priority:
      1) explicit --config path
      2) repo_root/config.yaml (local, ignored by git)
      3) repo_root/config.example.yaml (committed)

    Returns a plain dict.
    """
    repo_root = get_repo_root()

    if config_path:
        path = Path(config_path).expanduser().resolve()
    else:
        local = repo_root / "config.yaml"
        example = repo_root / "config.example.yaml"
        path = local if local.exists() else example

    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    return data
