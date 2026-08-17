"""Пилотный прогон генерации правдоподобных неверных вариантов ответа.

Берёт несколько вопросов из telegram_bot/rst.db (реальная база вопросов),
просит Gemini сгенерировать 4 варианта неверных ответов, похожих по теме и
формулировке на правильный (а не случайные определения других терминов),
и печатает результат для ручной проверки — ничего не сохраняет в базу.
"""

import json
import sqlite3
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent.parent
BOT_DB = PROJECT_ROOT / "telegram_bot" / "rst.db"

sys.path.insert(0, str(BACKEND_DIR))

import httpx  # noqa: E402

from app.config import settings  # noqa: E402

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"

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
    resp = httpx.post(
        GEMINI_URL,
        headers={"Content-Type": "application/json", "X-goog-api-key": settings.gemini_api_key},
        json={
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": 3000, "temperature": 0.7},
        },
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()
    text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(text)


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    conn = sqlite3.connect(BOT_DB)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT id, section, subsection, question, answer FROM questions ORDER BY RANDOM() LIMIT ?", (limit,)
    ).fetchall()
    conn.close()

    for r in rows:
        print("=" * 80)
        print(f"ID {r['id']} | {r['section']} / {r['subsection']}")
        print(f"Вопрос: {r['question']}")
        print(f"Правильный: {r['answer']}")
        try:
            wrongs = generate_distractors(r["section"], r["subsection"], r["question"], r["answer"])
            for k in ("wrong1", "wrong2", "wrong3", "wrong4"):
                print(f"  {k}: {wrongs.get(k)}")
        except Exception as e:
            print(f"  ОШИБКА: {e}")


if __name__ == "__main__":
    main()
