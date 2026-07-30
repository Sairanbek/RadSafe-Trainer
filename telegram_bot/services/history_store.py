import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

_LOCK = Lock()
MAX_ENTRIES_PER_USER = 50


def _store_path():
    project_root = Path(__file__).resolve().parents[1]
    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir / "history.json"


def _load():
    path = _store_path()
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def _save(data):
    path = _store_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def add_session(user_id: int, mode: str, section: str, total: int, correct: int, wrong: int):
    with _LOCK:
        data = _load()
        key = str(user_id)
        entries = data.get(key, [])

        percent = round(correct / total * 100) if total else 0

        entries.append({
            "date": datetime.now(timezone.utc).isoformat(timespec="minutes"),
            "mode": mode,
            "section": section,
            "total": total,
            "correct": correct,
            "wrong": wrong,
            "percent": percent,
        })

        entries = entries[-MAX_ENTRIES_PER_USER:]
        data[key] = entries
        _save(data)


def get_history(user_id: int, limit: int = 10):
    data = _load()
    entries = data.get(str(user_id), [])
    return list(reversed(entries))[:limit]