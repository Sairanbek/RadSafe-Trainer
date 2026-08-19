"""Перегенерирует неверные варианты ответа (дистракторы) для банка вопросов.

Правильные ответы не трогает. Работает напрямую с банком вопросов бота —
это источник истины (website/backend/rst_web.db собирается из него через
scripts/import_questions.py). Путь настраивается через BOT_DB_PATH.

## Почему запросы пакетные

Бесплатная квота Gemini — ~20 запросов в день на проект, и она общая с живым
ИИ-ассистентом на сайте. Раньше скрипт делал один запрос на один вопрос, то
есть за день обрабатывал ~12 вопросов и весь банк из 436 занял бы ~36 дней.
Теперь в один запрос уходит сразу BATCH_SIZE вопросов, и та же квота даёт
~150 вопросов в день — весь банк проходится за 3 дня.

Если модель вернула битый или обрезанный JSON, пакет автоматически делится
пополам и части повторяются отдельно: одна плохая генерация не тратит квоту
на весь пакет и не роняет остальные вопросы.

Использование:
    python scripts/regenerate_distractors.py --status          # прогресс, без запросов к API
    python scripts/regenerate_distractors.py --daily-batch 150 # следующие 150 необработанных (для cron)
    python scripts/regenerate_distractors.py --limit 16        # первые 16 вопросов (проверка качества)
    python scripts/regenerate_distractors.py --ids 5,318,155   # конкретные id (повтор неудачных)
    python scripts/regenerate_distractors.py                   # весь банк разом
    python scripts/regenerate_distractors.py --batch-size 4    # мельче пакет, если модель часто обрезает ответ
"""

import argparse
import json
import sqlite3
import sys
import time
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(BACKEND_DIR))

import httpx  # noqa: E402

from app.config import settings  # noqa: E402

# Банк вопросов — источник истины; путь настраивается через BOT_DB_PATH.
BOT_DB = settings.bot_db

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"
DELAY_BETWEEN_CALLS = 2.0
MAX_RETRIES = 5

# Сколько вопросов кладём в один запрос. Больше — экономнее по квоте, но выше
# риск, что модель обрежет ответ на середине JSON (тогда пакет делится пополам).
DEFAULT_BATCH_SIZE = 8

# Запас выходных токенов на один вопрос (4 варианта плюс разметка JSON).
TOKENS_PER_QUESTION = 1200

PROMPT_HEADER = """Ты помогаешь составить экзаменационный тест по радиационной безопасности \
для аттестации в Казахстане. Ниже несколько вопросов, для каждого дан правильный ответ \
(взят из реального текста нормативного документа). Для КАЖДОГО вопроса нужно придумать \
4 НЕВЕРНЫХ варианта ответа для теста с выбором одного из пяти вариантов.

ВАЖНО — как делать неверные варианты:
- Бери за основу формулировку и структуру ПРАВИЛЬНОГО ответа и меняй в ней конкретные \
факты: числа, сроки, пороговые значения, ответственных лиц/органы, условия, область \
применения. НЕ придумывай новые факты из воздуха и не бери определения других терминов.
- Каждый неверный вариант должен быть похож по теме и стилю на правильный настолько, \
чтобы отличить его мог только тот, кто действительно знает точную формулировку нормы.
- Варианты не должны дублировать друг друга по сути и не должны совпадать с правильным.
- Длина каждого варианта — примерно как у правильного ответа.

Вопросы:
"""

PROMPT_FOOTER = """
Ответь СТРОГО одним JSON-объектом без markdown-разметки, где ключ — id вопроса \
(строкой), а значение — объект с четырьмя вариантами. Ничего кроме JSON.

Формат:
{"<id>": {"wrong1": "...", "wrong2": "...", "wrong3": "...", "wrong4": "..."}}
"""

WRONG_KEYS = ("wrong1", "wrong2", "wrong3", "wrong4")


def _build_prompt(rows) -> str:
    parts = [PROMPT_HEADER]
    for r in rows:
        parts.append(
            f"\n--- id={r['id']}\n"
            f"Раздел: {r['section']} / {r['subsection'] or ''}\n"
            f"Вопрос: {r['question']}\n"
            f"Правильный ответ: {r['answer']}\n"
        )
    parts.append(PROMPT_FOOTER)
    return "".join(parts)


def _call_gemini(prompt: str, max_output_tokens: int) -> str:
    """Один запрос к модели с ретраями на 429/503. Возвращает текст ответа."""
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            resp = httpx.post(
                GEMINI_URL,
                headers={"Content-Type": "application/json", "X-goog-api-key": settings.gemini_api_key},
                json={
                    "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "maxOutputTokens": max_output_tokens,
                        "temperature": 0.7,
                        "responseMimeType": "application/json",
                    },
                },
                timeout=180,
            )
            if resp.status_code in (429, 503):
                raise httpx.HTTPStatusError("квота или перегрузка", request=resp.request, response=resp)
            resp.raise_for_status()
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception as e:  # noqa: BLE001
            last_error = e
            wait = 2 ** attempt
            print(f"    попытка {attempt + 1}/{MAX_RETRIES} не удалась ({e}), жду {wait}с")
            time.sleep(wait)

    raise RuntimeError(f"не удалось получить ответ после {MAX_RETRIES} попыток: {last_error}")


def _validate(wrongs: dict, answer: str) -> dict:
    """Проверяет один набор вариантов. Бросает ValueError, если набор негодный."""
    cleaned = {}
    for key in WRONG_KEYS:
        value = wrongs.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"пустой или нестроковый {key}")
        cleaned[key] = value.strip()

    # Модель иногда возвращает правильный ответ в числе неверных — такой вопрос
    # стал бы неразрешимым, поэтому набор целиком считаем негодным.
    normalized_answer = answer.strip().casefold()
    if any(v.casefold() == normalized_answer for v in cleaned.values()):
        raise ValueError("один из вариантов совпадает с правильным ответом")

    if len({v.casefold() for v in cleaned.values()}) != len(WRONG_KEYS):
        raise ValueError("варианты дублируют друг друга")

    return cleaned


def _parse_response(text: str, rows) -> dict[int, dict]:
    """Разбирает ответ модели в {id вопроса: варианты}. Негодные наборы отбрасывает."""
    text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    parsed = json.loads(text)  # битый/обрезанный JSON -> ValueError у вызывающего
    if not isinstance(parsed, dict):
        raise ValueError("ожидался JSON-объект, пришло что-то другое")

    answers = {r["id"]: r["answer"] for r in rows}
    result = {}
    for key, wrongs in parsed.items():
        try:
            qid = int(key)
        except (TypeError, ValueError):
            continue
        if qid not in answers or not isinstance(wrongs, dict):
            continue
        try:
            result[qid] = _validate(wrongs, answers[qid])
        except ValueError as e:
            print(f"    id={qid}: отбракован ({e})")

    return result


def generate_for_batch(rows) -> dict[int, dict]:
    """Варианты для пакета вопросов. При битом ответе делит пакет пополам."""
    if not rows:
        return {}

    max_tokens = TOKENS_PER_QUESTION * len(rows)
    try:
        text = _call_gemini(_build_prompt(rows), max_tokens)
        return _parse_response(text, rows)
    except (json.JSONDecodeError, ValueError, RuntimeError) as e:
        if len(rows) == 1:
            print(f"  ПРОПУЩЕН id={rows[0]['id']}: {e}")
            return {}
        half = len(rows) // 2
        print(f"  ответ не разобран ({e}) — делю пакет {len(rows)} -> {half} + {len(rows) - half}")
        time.sleep(DELAY_BETWEEN_CALLS)
        first = generate_for_batch(rows[:half])
        time.sleep(DELAY_BETWEEN_CALLS)
        second = generate_for_batch(rows[half:])
        return {**first, **second}


def _select_rows(conn, args):
    if args.ids:
        ids = [int(x) for x in args.ids.split(",")]
        placeholders = ",".join("?" * len(ids))
        return conn.execute(
            f"SELECT id, section, subsection, question, answer FROM questions "
            f"WHERE id IN ({placeholders}) ORDER BY id",
            ids,
        ).fetchall()

    if args.daily_batch:
        return conn.execute(
            "SELECT id, section, subsection, question, answer FROM questions "
            "WHERE distractors_regenerated_at IS NULL ORDER BY id LIMIT ?",
            (args.daily_batch,),
        ).fetchall()

    query = "SELECT id, section, subsection, question, answer FROM questions ORDER BY id"
    if args.limit:
        query += " LIMIT ?"
        return conn.execute(query, (args.limit,)).fetchall()
    return conn.execute(query).fetchall()


def print_status(conn, batch_size: int) -> None:
    total, done = conn.execute(
        "SELECT COUNT(*), COALESCE(SUM(distractors_regenerated_at IS NOT NULL), 0) FROM questions"
    ).fetchone()
    remaining = total - done
    percent = (done / total * 100) if total else 0.0

    print(f"База вопросов: {BOT_DB}")
    print(f"Всего вопросов:        {total}")
    print(f"Дистракторы обновлены: {done} ({percent:.1f}%)")
    print(f"Осталось:              {remaining}")
    if remaining:
        requests_needed = -(-remaining // batch_size)  # округление вверх
        print(f"Нужно запросов к Gemini (пакет по {batch_size}): ~{requests_needed}")
        print(f"При квоте ~20 запросов в день это ~{-(-requests_needed // 20)} дн.")


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
    parser.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        help=f"сколько вопросов кладём в один запрос к Gemini (по умолчанию {DEFAULT_BATCH_SIZE})",
    )
    parser.add_argument("--status", action="store_true", help="только показать прогресс, без запросов")
    args = parser.parse_args()

    if not BOT_DB.exists():
        print(f"Не найдена база вопросов: {BOT_DB}")
        sys.exit(1)

    if args.batch_size < 1:
        print("--batch-size должен быть не меньше 1")
        sys.exit(1)

    conn = sqlite3.connect(BOT_DB)
    conn.row_factory = sqlite3.Row

    if args.status:
        print_status(conn, args.batch_size)
        conn.close()
        return

    if not settings.gemini_api_key:
        print("Не задан GEMINI_API_KEY — генерировать варианты нечем.")
        sys.exit(1)

    rows = _select_rows(conn, args)
    total = len(rows)
    batches = [rows[i:i + args.batch_size] for i in range(0, total, args.batch_size)]
    print(f"Вопросов к обработке: {total}, пакетов по {args.batch_size}: {len(batches)}")

    saved_ids = set()
    for i, batch in enumerate(batches, 1):
        ids = [r["id"] for r in batch]
        print(f"[пакет {i}/{len(batches)}] id: {', '.join(map(str, ids))}")

        wrongs_by_id = generate_for_batch(batch)
        for qid, wrongs in wrongs_by_id.items():
            conn.execute(
                "UPDATE questions SET wrong1=?, wrong2=?, wrong3=?, wrong4=?, "
                "distractors_regenerated_at=datetime('now') WHERE id=?",
                (wrongs["wrong1"], wrongs["wrong2"], wrongs["wrong3"], wrongs["wrong4"], qid),
            )
            saved_ids.add(qid)
        conn.commit()
        print(f"  сохранено {len(wrongs_by_id)}/{len(batch)}")

        if i < len(batches):
            time.sleep(DELAY_BETWEEN_CALLS)

    failed_ids = [r["id"] for r in rows if r["id"] not in saved_ids]

    print("\n" + "=" * 60)
    print(f"Готово. Обработано в этом запуске: {len(saved_ids)}/{total}")
    if failed_ids:
        print(f"Не удалось (повторить через --ids): {','.join(map(str, failed_ids))}")
    print()
    print_status(conn, args.batch_size)
    conn.close()


if __name__ == "__main__":
    main()
