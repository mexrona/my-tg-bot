import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import load_settings
from bot.services.afk_state import AfkState
from bot.services.bot_commands import setup_bot_commands
from bot.services.middleware import InjectMiddleware
from bot.services.router import setup_routers
from bot.services.storage import Storage


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    settings = load_settings()
    storage = Storage(settings.db_path)
    afk_state = AfkState(storage)

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())
    dp.update.middleware(
        InjectMiddleware(settings=settings, storage=storage, afk_state=afk_state)
    )
    dp.include_router(setup_routers())

    await setup_bot_commands(bot, settings.owner_id)

    logging.info("Bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
