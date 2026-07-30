import asyncio

import handlers.start
import handlers.menu
import handlers.topics
import handlers.test
import handlers.admin

from loader import bot, dp
from handlers.test import timer_checker


async def main():

    print("🚀 RST бот запущен")

    # запуск проверки таймера аттестации
    asyncio.create_task(timer_checker())

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())