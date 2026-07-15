from openpyxl import load_workbook
from database.models import Question


def load_questions(file_path):

    workbook = load_workbook(file_path)
    sheet = workbook.active

    questions = []

    question_id = 1
    current_question = None

    for row in sheet.iter_rows(values_only=True):

        if not row:
            continue

        text = row[0]

        if text is None:
            continue

        text = str(text).strip()

        if text == "":
            continue

        # Пропускаем заголовок
        if text.startswith("Перечень тестовых"):
            continue

        # Если строка начинается с цифры и точки — это вопрос
        if text[:2].replace(".", "").isdigit() or (
            len(text) > 2 and text[0].isdigit() and "." in text
        ):

            current_question = text

        else:

            if current_question:

                questions.append(
                    Question(
                        id=question_id,
                        question=current_question,
                        answer=text
                    )
                )

                question_id += 1
                current_question = None

    return questions