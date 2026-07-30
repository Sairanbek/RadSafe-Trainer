import asyncio

import handlers.start
import handlers.menu
import handlers.topics
import handlers.test
import handlers.admin

from loader import bot, dp


async def main():

    await dp.start_polling(bot)



if __name__ == "__main__":
    asyncio.run(main())