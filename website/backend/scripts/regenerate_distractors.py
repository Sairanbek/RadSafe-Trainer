"""Перегенерирует неверные варианты ответа для всего банка вопросов.

Правильные ответы не трогает. Работает напрямую с telegram_bot/rst.db —
это источник истины для вопросов (website/backend/rst_web.db собирается из
неё через scripts/import_questions.py).

Бесплатная квота Gemini на этот проект — 20 запросов в день на модель, и она
общая с живым ИИ-ассистентом на сайте. Поэтому по умолчанию скрипт берёт
только НЕобработанные вопросы (колонка distractors_regenerated_at IS NULL)
небольшими порциями — так за несколько недель обработает весь банк, не
отжирая всю дневную квоту у реальных пользователей чата.

Использование:
    python scripts/regenerate_distractors.py --daily-batch 12  # следующие необработанные 12 (для cron)
    python scripts/regenerate_distractors.py --limit 20         # все вопросы, первые 20 (проверка)
    python scripts/regenerate_distractors.py --ids 5,318,155    # конкретные id (повтор неудачных)
    python scripts/regenerate_distractors.py                    # вообще все вопросы разом
"""

import argparse
import json
import sqlite3
import sys
import time
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent.parent
BOT_DB = PROJECT_ROOT / "telegram_bot" / "rst.db"

sys.path.insert(0, str(BACKEND_DIR))

import httpx  # noqa: E402

from app.config import settings  # noqa: E402

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"
DELAY_BETWEEN_CALLS = 2.0
MAX_RETRIES = 5

PROMPT_TEMPLATE = """Ты помогаешь составить экзаменационный тест по радиационной безопасности \
для аттестации в Казахстане. Дан вопрос и правильный ответ (взят из реального текста \
нормативного документа). Нужно придумать 4 НЕВЕРНЫХ варианта ответа для теста с выбором \
одного из пяти вариантов.

ВАЖНО — как делать неверные варианты:
- Бери за основу формулировку и структуру ПРАВИЛЬНОГО ответа и меняй в ней конкретные \
факты: числа, сроки, пороговые значения, ответственных лиц/органы, условия, область \
применения. НЕ придумывай новые факты из воздуха и не бери определения других терминов.
- Каждый неверный вариант должен быть похож по теме и стилю на правильный настолько, \
чтобы отличить его мог только тот, кто действительно знает точную формулировку нормы.
- Варианты не должны дублировать друг друга по сути.
- Длина каждого варианта — примерно как у правильного ответа.

Раздел: {section} / {subsection}
Вопрос: {question}
Правильный ответ: {answer}

Ответь СТРОГО в формате JSON без markdown-разметки:
{{"wrong1": "...", "wrong2": "...", "wrong3": "...", "wrong4": "..."}}
"""


def generate_distractors(section: str, subsection: str, question: str, answer: str) -> dict:
    prompt = PROMPT_TEMPLATE.format(section=section, subsection=subsection, question=question, answer=answer)

    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            resp = httpx.post(
                GEMINI_URL,
                headers={"Content-Type": "application/json", "X-goog-api-key": settings.gemini_api_key},
                json={
                    "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                    "generationConfig": {"maxOutputTokens": 3000, "temperature": 0.7},
                },
                timeout=60,
            )
            if resp.status_code in (429, 503):
                raise httpx.HTTPStatusError("retryable", request=resp.request, response=resp)
            resp.raise_for_status()
            data = resp.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            parsed = json.loads(text)
            for key in ("wrong1", "wrong2", "wrong3", "wrong4"):
                if not parsed.get(key):
                    raise ValueError(f"пустой {key} в ответе модели")
            return parsed
        except Exception as e:  # noqa: BLE001
            last_error = e
            wait = 2 ** attempt
            print(f"    попытка {attempt + 1}/{MAX_RETRIES} не удалась ({e}), жду {wait}с")
            time.sleep(wait)

    raise RuntimeError(f"не удалось получить варианты после {MAX_RETRIES} попыток: {last_error}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--ids", type=str, default=None, help="через запятую")
    parser.add_argument(
        "--daily-batch",
        type=int,
        default=None,
        help="взять только N ещё не обработанных вопросов (distractors_regenerated_at IS NULL)",
    )
    args = parser.parse_args()

    conn = sqlite3.connect(BOT_DB)
    conn.row_factory = sqlite3.Row

    if args.ids:
        ids = [int(x) for x in args.ids.split(",")]
        placeholders = ",".join("?" * len(ids))
        rows = conn.execute(
            f"SELECT id, section, subsection, question, answer FROM questions WHERE id IN ({placeholders}) ORDER BY id",
            ids,
        ).fetchall()
    elif args.daily_batch:
        rows = conn.execute(
            "SELECT id, section, subsection, question, answer FROM questions "
            "WHERE distractors_regenerated_at IS NULL ORDER BY id LIMIT ?",
            (args.daily_batch,),
        ).fetchall()
    else:
        query = "SELECT id, section, subsection, question, answer FROM questions ORDER BY id"
        if args.limit:
            query += f" LIMIT {args.limit}"
        rows = conn.execute(query).fetchall()

    total = len(rows)
    failed_ids = []
    print(f"Всего вопросов к обработке: {total}")

    for i, r in enumerate(rows, 1):
        print(f"[{i}/{total}] id={r['id']}: {r['question'][:70]}")
        try:
            wrongs = generate_distractors(r["section"], r["subsection"] or "", r["question"], r["answer"])
            conn.execute(
                "UPDATE questions SET wrong1=?, wrong2=?, wrong3=?, wrong4=?, "
                "distractors_regenerated_at=datetime('now') WHERE id=?",
                (wrongs["wrong1"], wrongs["wrong2"], wrongs["wrong3"], wrongs["wrong4"], r["id"]),
            )
            conn.commit()
        except Exception as e:  # noqa: BLE001
            print(f"  ПРОПУЩЕН id={r['id']}: {e}")
            failed_ids.append(r["id"])

        time.sleep(DELAY_BETWEEN_CALLS)

    conn.close()

    remaining = sqlite3.connect(BOT_DB).execute(
        "SELECT COUNT(*) FROM questions WHERE distractors_regenerated_at IS NULL"
    ).fetchone()[0]

    print("\n" + "=" * 60)
    print(f"Готово. Обработано в этом запуске: {total - len(failed_ids)}/{total}")
    print(f"Осталось необработанных вопросов всего: {remaining}")
    if failed_ids:
        print(f"Не удалось (повторить через --ids): {','.join(map(str, failed_ids))}")


if __name__ == "__main__":
    main()
