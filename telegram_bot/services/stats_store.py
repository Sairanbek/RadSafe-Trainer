import json
from pathlib import Path
from threading import Lock

_LOCK = Lock()


def _store_path():
    project_root = Path(__file__).resolve().parents[1]
    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir / "stats.json"


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


def record_answer(user_id: int, section: str, is_correct: bool):
    with _LOCK:
        data = _load()
        key = str(user_id)
        user_stats = data.get(key, {})
        section_stats = user_stats.get(section, {"asked": 0, "correct": 0})

        section_stats["asked"] += 1
        if is_correct:
            section_stats["correct"] += 1

        user_stats[section] = section_stats
        data[key] = user_stats
        _save(data)


def get_stats(user_id: int):
    data = _load()
    return data.get(str(user_id), {})