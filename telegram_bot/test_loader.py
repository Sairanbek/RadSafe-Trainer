from services.excel_loader import load_questions

questions = load_questions(
    "../questions/radiation_safety/Перечень тестов для аттестации по РБ.xlsx"
)

print(f"Всего вопросов: {len(questions)}")

print()
print(questions[0])