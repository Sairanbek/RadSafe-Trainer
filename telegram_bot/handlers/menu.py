from aiogram import F
from aiogram.types import Message

from loader import dp
from services.stats_store import get_stats


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

    # сортировка от самого слабого раздела к самому сильному
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


@dp.message(F.text == "ℹ️ О программе")
async def about(message: Message):
    await message.answer(
        "🛡 RST\n"
        "Radiation Safety Trainer\n\n"
        "Версия: 0.2\n"
        "Разработка: Сайранбек Бурабаев"
    )