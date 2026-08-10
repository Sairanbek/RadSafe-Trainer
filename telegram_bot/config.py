from pathlib import Path

from dotenv import load_dotenv
import os

# Абсолютный путь, чтобы .env находился независимо от того, откуда запущен бот.
load_dotenv(Path(__file__).resolve().parent / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_NAME = os.getenv("DATABASE_NAME")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
