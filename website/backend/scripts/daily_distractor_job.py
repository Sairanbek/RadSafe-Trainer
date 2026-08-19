"""Ежедневная порция перегенерации дистракторов + синхронизация на сайт.

Вызывается из launchd (локально на Mac) или из cron на сервере — см. DEPLOY.md.
Берёт следующую пачку необработанных вопросов, обновляет банк вопросов бота и
сразу прогоняет import_questions.py, чтобы сайт увидел новые варианты без
ручных действий.

Размер порции. Дневная квота Gemini — ~20 запросов на проект, общая с живым
ИИ-ассистентом. regenerate_distractors.py кладёт в один запрос 8 вопросов
(BATCH_SIZE ниже), поэтому 64 вопроса = 8 запросов в день: банк из 436 вопросов
проходится примерно за неделю, а ~12 запросов остаётся живым пользователям чата.
Нужно быстрее и не жалко квоту ассистента — поднимите DAILY_BATCH_SIZE или
прогоните разом: `python scripts/regenerate_distractors.py`.
"""

import runpy
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
DAILY_BATCH_SIZE = 64
BATCH_SIZE = 8

sys.argv = [
    "regenerate_distractors.py",
    "--daily-batch",
    str(DAILY_BATCH_SIZE),
    "--batch-size",
    str(BATCH_SIZE),
]
runpy.run_path(str(SCRIPTS_DIR / "regenerate_distractors.py"), run_name="__main__")

sys.argv = ["import_questions.py"]
runpy.run_path(str(SCRIPTS_DIR / "import_questions.py"), run_name="__main__")
