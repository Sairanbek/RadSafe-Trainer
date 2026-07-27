from services.excel_loader import load_questions

questions = load_questions()


print(f"Всего вопросов: {len(questions)}")

print()
print(questions[0])