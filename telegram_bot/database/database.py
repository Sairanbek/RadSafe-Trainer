import aiosqlite

DATABASE_NAME = "rst.db"


async def create_database():
    async with aiosqlite.connect(DATABASE_NAME) as db:

        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            full_name TEXT,
            username TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        await db.commit()