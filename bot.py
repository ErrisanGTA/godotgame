import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.config import load_settings
from app.db import Database
from app.handlers.common import router


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    settings = load_settings()
    db = Database(settings.db_path)
    await db.init()

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    dp["db"] = db
    dp["settings"] = settings
    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
