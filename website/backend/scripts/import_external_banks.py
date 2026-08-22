"""Импорт банков вопросов по другим направлениям (радиология, госслужба).

Радиационная безопасность идёт своим путём: Excel -> telegram_bot/rst.db ->
import_questions.py. Остальные направления лежат в репозитории готовыми JSON
(questions/<направление>/questions.json) и заливаются этим скриптом.

Скрипт идемпотентный: id вопросов вычисляются детерминированно из направления
и текста вопроса, поэтому повторный запуск обновляет те же строки, а не плодит
дубликаты. Диапазоны id разнесены по направлениям, чтобы не столкнуться с
банком радиационной безопасности (там id 1..N из Excel).

Использование (из website/backend, с активированным .venv):
    python scripts/import_external_banks.py            # залить всё
    python scripts/import_external_banks.py --dry-run  # только показать, что будет
"""

import argparse
import json
import sys
from pathlib import Path

from sqlalchemy import func

BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent.parent

sys.path.insert(0, str(BACKEND_DIR))

from app import models  # noqa: E402,F401
from app.database import Base, SessionLocal, engine, run_migrations  # noqa: E402
from app.models import DEFAULT_MODULE, Question  # noqa: E402

# Направление -> (файл с вопросами, начало диапазона id).
# Шаг между началами — 100 000, столько вопросов в одном направлении не будет.
BANKS = {
    "Радиология": (PROJECT_ROOT / "questions" / "radiology" / "questions.json", 100_000),
    "Госслужба (Корпус Б)": (PROJECT_ROOT / "questions" / "civil_service" / "questions.json", 200_000),
}

REQUIRED = ("module", "section", "question", "answer", "wrong1", "wrong2", "wrong3")


def load_bank(path: Path) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"Файл банка не найден: {path}")
    rows = json.loads(path.read_text())
    if not isinstance(rows, list):
        raise SystemExit(f"Ожидался список вопросов: {path}")
    return rows


def validate(rows: list[dict], module: str) -> None:
    for i, r in enumerate(rows):
        missing = [f for f in REQUIRED if not str(r.get(f) or "").strip()]
        if missing:
            raise SystemExit(f"[{module}] вопрос #{i}: не заполнено {missing}")
        if r["module"] != module:
            raise SystemExit(f"[{module}] вопрос #{i}: чужое направление {r['module']!r}")


def check_section_names_unique(banks: dict[str, list[dict]], db) -> None:
    """Разделы должны быть уникальны в пределах всей базы.

    Таблица stats хранит только (user_id, section) без направления, поэтому
    одинаковые названия разделов в двух направлениях смешали бы статистику.
    """
    owner: dict[str, str] = {}
    for row in db.query(Question.section, Question.module).distinct().all():
        section, module = row
        if module not in banks:  # существующие направления, которые не трогаем
            owner[section] = module

    for module, rows in banks.items():
        for r in rows:
            section = r["section"]
            other = owner.get(section)
            if other is not None and other != module:
                raise SystemExit(
                    f"Раздел {section!r} есть и в {other!r}, и в {module!r}. "
                    "Названия разделов должны быть уникальны — переименуйте один из них."
                )
            owner[section] = module


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="ничего не писать в базу")
    args = parser.parse_args()

    Base.metadata.create_all(bind=engine)
    run_migrations()

    banks = {module: load_bank(path) for module, (path, _) in BANKS.items()}
    for module, rows in banks.items():
        validate(rows, module)

    db = SessionLocal()
    try:
        check_section_names_unique(banks, db)

        total_new = total_updated = 0
        for module, rows in banks.items():
            start_id = BANKS[module][1]
            new = updated = 0

            for offset, r in enumerate(rows):
                qid = start_id + offset
                existing = db.get(Question, qid)
                values = dict(
                    module=module,
                    section=r["section"],
                    subsection=r.get("subsection") or "",
                    question=r["question"],
                    answer=r["answer"],
                    wrong1=r["wrong1"],
                    wrong2=r["wrong2"],
                    wrong3=r["wrong3"],
                    wrong4=r.get("wrong4") or "",
                    explanation=r.get("explanation") or None,
                    source=r.get("source") or None,
                )
                if existing is None:
                    db.add(Question(id=qid, **values))
                    new += 1
                else:
                    for k, v in values.items():
                        setattr(existing, k, v)
                    updated += 1

            print(f"{module}: новых {new}, обновлено {updated}, всего в файле {len(rows)}")
            total_new += new
            total_updated += updated

        if args.dry_run:
            db.rollback()
            print("\n--dry-run: изменения откачены, база не тронута")
            return

        db.commit()
        print(f"\nГотово: добавлено {total_new}, обновлено {total_updated}")

        print("\nВ базе сейчас:")
        for module, count in db.query(Question.module, func.count(Question.id)).group_by(
            Question.module
        ).order_by(func.count(Question.id).desc()).all():
            print(f"  {module or DEFAULT_MODULE}: {count}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
