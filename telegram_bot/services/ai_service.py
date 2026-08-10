"""Тонкая обёртка над Google Gemini API (бесплатный тариф) для бота.

Промпты ограничивают ассистента темой радиационной безопасности и
подготовки к аттестации — на несвязанные вопросы он вежливо отказывает.
"""

import aiohttp

from config import GEMINI_API_KEY
from database.models import Question

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


async def _call_gemini(system_instruction: str, contents: list[dict], max_output_tokens: int = 1200) -> str:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                GEMINI_URL,
                headers={
                    "Content-Type": "application/json",
                    "X-goog-api-key": GEMINI_API_KEY,
                },
                json={
                    "system_instruction": {"parts": [{"text": system_instruction}]},
                    "contents": contents,
                    "generationConfig": {
                        "maxOutputTokens": max_output_tokens,
                        "temperature": 0.4,
                    },
                },
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (aiohttp.ClientError, KeyError, IndexError) as e:
        raise GeminiError("Ассистент временно недоступен") from e


async def explain_answer(question: Question, chosen_text: str | None) -> str:
    correct_text = question.answer

    prompt = f"Вопрос: {question.question}\n\nПравильный ответ: {correct_text}\n"
    if chosen_text and chosen_text != correct_text:
        prompt += f"Пользователь выбрал: {chosen_text}\n"
    prompt += "\nОбъясни коротко (2-4 предложения), почему это правильный ответ."

    return await _call_gemini(SYSTEM_SCOPE, [{"role": "user", "parts": [{"text": prompt}]}])


async def chat_reply(history: list[dict], message: str) -> str:
    contents = [
        {"role": "model" if h["role"] == "model" else "user", "parts": [{"text": h["text"]}]}
        for h in history[-10:]
    ]
    contents.append({"role": "user", "parts": [{"text": message}]})
    return await _call_gemini(SYSTEM_SCOPE, contents)


async def study_plan(stats: dict, history: list[dict]) -> str:
    lines = ["Статистика по разделам:"]
    for section, s in stats.items():
        asked = s.get("asked", 0)
        correct = s.get("correct", 0)
        percent = round(correct / asked * 100) if asked else 0
        lines.append(f"- {section}: {correct}/{asked} ({percent}%)")

    lines.append("")
    lines.append(f"Пройдено тестов (последние): {len(history)}")

    prompt = (
        "На основе статистики пользователя составь короткий персональный план подготовки "
        "к аттестации (буллеты, на каких разделах сосредоточиться в первую очередь):\n\n"
        + "\n".join(lines)
    )
    return await _call_gemini(SYSTEM_SCOPE, [{"role": "user", "parts": [{"text": prompt}]}])
