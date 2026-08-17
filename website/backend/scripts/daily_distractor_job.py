"""Ежедневная порция перегенерации дистракторов + синхронизация на сайт.

Вызывается из launchd (см. установку в разговоре/README). Берёт следующую
пачку необработанных вопросов, обновляет telegram_bot/rst.db и сразу
прогоняет import_questions.py, чтобы сайт увидел новые варианты без ручных
действий.
"""

import runpy
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
DAILY_BATCH_SIZE = 12

sys.argv = ["regenerate_distractors.py", "--daily-batch", str(DAILY_BATCH_SIZE)]
runpy.run_path(str(SCRIPTS_DIR / "regenerate_distractors.py"), run_name="__main__")

sys.argv = ["import_questions.py"]
runpy.run_path(str(SCRIPTS_DIR / "import_questions.py"), run_name="__main__")
