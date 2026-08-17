"""Проверяет банк вопросов на изменения в первоисточниках на adilet.zan.kz.

НЕ переписывает вопросы автоматически — юридическая точность требует, чтобы
любое изменение проверил человек. Скрипт только скачивает текущий текст
документа, сравнивает с прошлым снимком (law_snapshots/) и пишет отчёт:
что не менялось, а что изменилось с прошлой проверки (с diff).

adilet.zan.kz отдаёт неполную цепочку TLS-сертификатов (нет промежуточного
сертификата) — обычные http-библиотеки Python (httpx/requests) с этим не
справляются, а `curl` — справляется (использует системную проверку через
Keychain на macOS, которая умеет дотягивать недостающий сертификат).
Поэтому качаем страницы через `curl`, а не httpx.

Использование:
    python scripts/scrape_adilet.py

Как добавить источник: впиши exact-совпадающее название раздела (как в
telegram_bot/rst.db, колонка section) и адрес документа на adilet.zan.kz
в SOURCES ниже.
"""

import hashlib
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
SNAPSHOTS_DIR = BACKEND_DIR / "law_snapshots"

sys.path.insert(0, str(BACKEND_DIR))

from app.mailer import send_source_change_alert  # noqa: E402

# Раздел (как в telegram_bot/rst.db) -> адрес документа на adilet.zan.kz.
# None = источник ещё не сопоставлен с конкретным документом на adilet.zan.kz
# (не гадаем — не тот документ хуже, чем отсутствие проверки).
SOURCES: dict[str, str | None] = {
    "ЗРК «О радиационной безопасности населения»": "https://adilet.zan.kz/rus/docs/Z980000219_",
    "ЗРК «Об использовании атомной энергии»": "https://adilet.zan.kz/rus/docs/Z970000093_",
    "СЭТОРБ 2019 (Сан. правила по радиац. безопасности)": "https://adilet.zan.kz/rus/docs/V1900018920",
    "СЭТРОО 260 (Сан. правила по рентген. оборудованию)": "https://adilet.zan.kz/rus/docs/V1500011204",
    "Правила физзащиты ядерных материалов и установок": "https://adilet.zan.kz/rus/docs/V1600013498",
    # Пока не сопоставлены — нужна проверка точного документа перед добавлением:
    "Гигиенические нормативы (ГН 155)": None,
    "Правила гос. учёта источников излучения": None,
    "Правила гос. учёта ядерных материалов": None,
    "Правила организации инспекций МАГАТЭ": None,
    "Правила повышения квалификации персонала": None,
    "Правила транспортировки радиоактивных веществ и отходов": None,
    "Правила транспортировки ядерных материалов": None,
    "Правила физзащиты источников излучения (ИИИ и ПХ)": None,
    "Соглашение РК—МАГАТЭ о гарантиях (1994)": None,
    "Конвенция о физ. защите ядерного материала": None,
    "Без указания источника": None,
}


def _slug(section: str) -> str:
    return re.sub(r"[^a-zA-Zа-яА-Я0-9]+", "_", section).strip("_")


def fetch(url: str) -> str:
    result = subprocess.run(
        ["curl", "-sL", "--max-time", "30", url],
        capture_output=True,
        text=True,
        check=True,
    )
    html = result.stdout
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def main():
    SNAPSHOTS_DIR.mkdir(exist_ok=True)
    report_lines = [f"# Проверка источников — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}", ""]
    changed_sections: list[str] = []

    for section, url in SOURCES.items():
        print(f"{section}: ", end="")
        if url is None:
            print("нет сопоставленного документа — пропуск")
            report_lines.append(f"- ⚪ **{section}** — источник не сопоставлен, проверка невозможна")
            continue

        snapshot_path = SNAPSHOTS_DIR / f"{_slug(section)}.txt"
        try:
            new_text = fetch(url)
        except Exception as e:  # noqa: BLE001
            print(f"ОШИБКА загрузки: {e}")
            report_lines.append(f"- 🔴 **{section}** — не удалось загрузить {url}: {e}")
            continue

        new_hash = hashlib.sha256(new_text.encode("utf-8")).hexdigest()

        if snapshot_path.exists():
            old_text = snapshot_path.read_text(encoding="utf-8")
            old_hash = hashlib.sha256(old_text.encode("utf-8")).hexdigest()
            if old_hash == new_hash:
                print("без изменений")
                report_lines.append(f"- 🟢 **{section}** — без изменений ({url})")
                continue
            else:
                print("ИЗМЕНИЛСЯ — нужна проверка человеком")
                report_lines.append(
                    f"- 🟡 **{section}** — текст документа изменился с прошлой проверки, "
                    f"нужно вручную сверить вопросы этого раздела с новым текстом: {url}"
                )
                changed_sections.append(section)
        else:
            print("первый снимок сохранён")
            report_lines.append(f"- 🆕 **{section}** — первый снимок сохранён ({url})")

        snapshot_path.write_text(new_text, encoding="utf-8")

    report_path = SNAPSHOTS_DIR / f"report_{datetime.now(timezone.utc).strftime('%Y%m%d')}.md"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    print(f"\nОтчёт: {report_path}")

    if changed_sections:
        try:
            send_source_change_alert(changed_sections)
            print("Уведомление на email отправлено.")
        except Exception as e:  # noqa: BLE001
            print(f"Не удалось отправить email-уведомление: {e}")


if __name__ == "__main__":
    main()
