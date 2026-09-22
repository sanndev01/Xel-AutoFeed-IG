from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config.json"
OUTPUT_DIR = ROOT / "output"

DEFAULT = {
    "instagram": {"enabled": False, "username": "", "session_file": "session.json"},
    "grid": {"rasio": "3:4"},
    "upload": {"jeda_min": 30, "jeda_max": 75},
}


def baca_config() -> dict:
    """Baca config.json, nilai yang hilang diisi default."""
    config = {kunci: dict(nilai) for kunci, nilai in DEFAULT.items()}

    if CONFIG_PATH.is_file():
        try:
            dari_file = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise ValueError("Format config.json tidak valid.") from error

        for kunci, nilai in dari_file.items():
            if isinstance(nilai, dict):
                config.setdefault(kunci, {}).update(nilai)
            else:
                config[kunci] = nilai

    return config


def simpan_config(config: dict) -> None:
    CONFIG_PATH.write_text(
        json.dumps(config, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def path_sesi() -> Path:
    nama = baca_config()["instagram"].get("session_file") or "session.json"
    return ROOT / nama


def status_instagram() -> bool:
    ig = baca_config()["instagram"]
    return bool(ig.get("enabled") and ig.get("username"))
