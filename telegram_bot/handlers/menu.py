from aiogram import F
from aiogram.types import Message

from loader import dp
from services.stats_store import get_stats
from services.history_store import get_history


@dp.message(F.text == "📊 Моя статистика")
async def statistics(message: Message):
    user_id = message.from_user.id
    stats = get_stats(user_id)

    if not stats:
        await message.answer("📊 Пока нет данных. Пройди хотя бы один тест!")
        return

    rows = []
    for section, s in stats.items():
        asked = s["asked"]
        correct = s["correct"]
        percent = round(correct / asked * 100) if asked else 0
        rows.append((section, asked, correct, percent))

    rows.sort(key=lambda r: r[3])

    lines = ["📊 Статистика по разделам:\n"]
    for section, asked, correct, percent in rows:
        emoji = "🔴" if percent < 50 else "🟡" if percent < 80 else "🟢"
        lines.append(f"{emoji} {section}\n   {correct}/{asked} ({percent}%)\n")

    total_asked = sum(r[1] for r in rows)
    total_correct = sum(r[2] for r in rows)
    total_percent = round(total_correct / total_asked * 100) if total_asked else 0
    lines.append(f"\nИтого: {total_correct}/{total_asked} ({total_percent}%)")

    await message.answer("\n".join(lines))


@dp.message(F.text == "🕘 История тестов")
async def history(message: Message):
    user_id = message.from_user.id
    entries = get_history(user_id, limit=10)

    if not entries:
        await message.answer("🕓 Пока нет пройденных тестов.")
        return

    lines = ["🕓 Последние тесты:\n"]
    for e in entries:
        date_str = e["date"][:16].replace("T", " ")
        section = e["section"]
        mode_label = "🔁 ошибки" if e["mode"] == "mistakes" else section
        emoji = "🔴" if e["percent"] < 50 else "🟡" if e["percent"] < 80 else "🟢"
        lines.append(
            f"{emoji} {date_str} — {mode_label}\n"
            f"   {e['correct']}/{e['total']} ({e['percent']}%)\n"
        )

    await message.answer("\n".join(lines))


@dp.message(F.text == "ℹ️ О программе")
async def about(message: Message):
    await message.answer(
        "🛡 RST\n"
        "Radiation Safety Trainer\n\n"
        "Версия: 0.3\n"
        "Разработка: Бурабаев Сайранбек"
    )