"""Тонкая обёртка над Google Gemini API (бесплатный тариф).

Промпты ограничивают ассистента темой радиационной безопасности и
подготовки к аттестации — на несвязанные вопросы он вежливо отказывает.
"""

import httpx

from app.config import settings
from app.models import Question

GEMINI_MODEL = "gemini-flash-latest"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

SYSTEM_SCOPE = (
    "Ты — ассистент внутри RST (RadSafe Trainer), тренажёра подготовки к аттестации "
    "по радиационной безопасности в Казахстане. Отвечай по-русски, кратко и по делу. "
    "Если вопрос не связан с радиационной безопасностью, атомной энергией или "
    "подготовкой к аттестации — вежливо скажи, что помогаешь только с этой темой."
)


class GeminiError(RuntimeError):
    pass


def _call_gemini(system_instruction: str, contents: list[dict], max_output_tokens: int = 1200) -> str:
    try:
        resp = httpx.post(
            GEMINI_URL,
            headers={
                "Content-Type": "application/json",
                "X-goog-api-key": settings.gemini_api_key,
            },
            json={
                "system_instruction": {"parts": [{"text": system_instruction}]},
                "contents": contents,
                "generationConfig": {
                    "maxOutputTokens": max_output_tokens,
                    "temperature": 0.4,
                },
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (httpx.HTTPError, KeyError, IndexError) as e:
        raise GeminiError("Ассистент временно недоступен") from e


def explain_answer(question: Question, chosen_text: str | None) -> str:
    correct_text = question.answer

    prompt = (
        f"Вопрос: {question.question}\n\n"
        f"Правильный ответ: {correct_text}\n"
    )
    if chosen_text and chosen_text != correct_text:
        prompt += f"Пользователь выбрал: {chosen_text}\n"
    prompt += "\nОбъясни коротко (2-4 предложения), почему это правильный ответ."

    return _call_gemini(SYSTEM_SCOPE, [{"role": "user", "parts": [{"text": prompt}]}])


def chat_reply(history: list[dict], message: str) -> str:
    contents = [
        {"role": "model" if h["role"] == "model" else "user", "parts": [{"text": h["text"]}]}
        for h in history[-10:]
    ]
    contents.append({"role": "user", "parts": [{"text": message}]})
    return _call_gemini(SYSTEM_SCOPE, contents)


def study_plan(sections: list[dict], tests_count: int, average_percent: int, mistakes_count: int) -> str:
    lines = [f"Пройдено тестов: {tests_count}", f"Средний результат: {average_percent}%", f"Ошибок на повторении: {mistakes_count}", "", "Статистика по разделам:"]
    for s in sections:
        lines.append(f"- {s['section']}: {s['correct']}/{s['asked']} ({s['percent']}%)")

    prompt = (
        "На основе статистики пользователя составь короткий персональный план подготовки "
        "к аттестации (буллеты, на каких разделах сосредоточиться в первую очередь):\n\n"
        + "\n".join(lines)
    )
    return _call_gemini(SYSTEM_SCOPE, [{"role": "user", "parts": [{"text": prompt}]}])
