import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

_LOCK = Lock()


def _store_path():
    project_root = Path(__file__).resolve().parents[1]
    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir / "users.json"


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


def register_visit(user_id: int, first_name: str, username: str):
    with _LOCK:
        data = _load()
        key = str(user_id)
        now = datetime.now(timezone.utc).isoformat(timespec="minutes")

        user = data.get(key)
        if user is None:
            data[key] = {
                "first_name": first_name,
                "username": username,
                "first_seen": now,
                "last_seen": now,
                "visits": 1,
            }
        else:
            user["first_name"] = first_name
            user["username"] = username
            user["last_seen"] = now
            user["visits"] = user.get("visits", 0) + 1

        _save(data)


def get_admin_stats():
    data = _load()
    total = len(data)

    now = datetime.now(timezone.utc)
    active_7d = 0
    active_today = 0

    for user in data.values():
        last_seen = datetime.fromisoformat(user["last_seen"])
        delta_days = (now - last_seen).days
        if delta_days == 0:
            active_today += 1
        if delta_days <= 7:
            active_7d += 1

    return {
        "total": total,
        "active_today": active_today,
        "active_7d": active_7d,
    }