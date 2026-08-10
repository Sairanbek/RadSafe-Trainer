"""Делает пользователя сайта администратором по email.

Использование:
    python scripts/make_admin.py user@example.com
"""

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.database import SessionLocal  # noqa: E402
from app.models import User  # noqa: E402


def main():
    if len(sys.argv) != 2:
        print("Использование: python scripts/make_admin.py user@example.com")
        sys.exit(1)

    email = sys.argv[1].strip().lower()
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            print(f"Пользователь с email {email} не найден. Сначала зарегистрируйтесь на сайте.")
            sys.exit(1)

        user.is_admin = True
        db.add(user)
        db.commit()
        print(f"{email} теперь администратор.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
