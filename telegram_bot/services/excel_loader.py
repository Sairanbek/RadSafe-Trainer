from pathlib import Path
import re

from openpyxl import load_workbook

from database.models import Question


def load_questions(file_path=None):
    """
    Загружает вопросы из Excel.

    Поддерживает:
    - многострочные ответы;
    - удаление номеров вопросов;
    - автоматический поиск файла.
    """

    print("НОВАЯ ВЕРСИЯ excel_loader")

    if file_path is None:
        project_root = Path(__file__).resolve().parents[2]

        file_path = (
            project_root
            / "questions"
            / "radiation_safety"
            / "Перечень тестов для аттестации по РБ.xlsx"
        )

    workbook = load_workbook(file_path, data_only=True)
    sheet = workbook.active

    questions = []

    current_question = None
    current_answer = []

    question_id = 1

    for row in sheet.iter_rows(values_only=True):

        if not row:
            continue

        cell = row[0]

        if cell is None:
            continue

        text = str(cell).strip()

        if text == "":
            continue

        # пропускаем заголовок
        if text.startswith("Перечень тестовых"):
            continue

        # новая строка вопроса
        if re.match(r"^\d+\.", text):

            # сохраняем предыдущий вопрос
            if current_question is not None:

                questions.append(
                    Question(
                        id=question_id,
                        question=current_question,
                        answer="\n".join(current_answer).strip()
                    )
                )

                question_id += 1

            # убираем номер вопроса
            current_question = re.sub(r"^\d+\.\s*", "", text)

            current_answer = []

        else:

            current_answer.append(text)

    # сохраняем последний вопрос

    if current_question is not None:

        questions.append(
            Question(
                id=question_id,
                question=current_question,
                answer="\n".join(current_answer).strip()
            )
        )

    print(f"Загружено вопросов: {len(questions)}")

    return questions