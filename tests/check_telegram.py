import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from aiogram import Bot

from bot.config import load_settings
from bot.services.bot_commands import setup_bot_commands


async def check_telegram() -> None:
    settings = load_settings()
    bot = Bot(token=settings.bot_token)
    try:
        me = await bot.get_me()
        print(f"Bot OK: @{me.username} (id={me.id})")
        await setup_bot_commands(bot, settings.owner_id)
        print("Commands registered OK")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(check_telegram())
