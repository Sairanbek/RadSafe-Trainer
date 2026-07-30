import json
from pathlib import Path
from threading import Lock

_LOCK = Lock()


def _store_path():
    project_root = Path(__file__).resolve().parents[1]
    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir / "mistakes.json"


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


def add_mistake(user_id: int, question_id: int):
    with _LOCK:
        data = _load()
        key = str(user_id)
        ids = set(data.get(key, []))
        ids.add(question_id)
        data[key] = sorted(ids)
        _save(data)


def remove_mistake(user_id: int, question_id: int):
    with _LOCK:
        data = _load()
        key = str(user_id)
        ids = set(data.get(key, []))
        ids.discard(question_id)
        data[key] = sorted(ids)
        _save(data)


def get_mistake_ids(user_id: int):
    data = _load()
    return set(data.get(str(user_id), []))