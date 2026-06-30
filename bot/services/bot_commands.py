from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat, BotCommandScopeDefault


async def setup_bot_commands(bot: Bot, owner_id: int) -> None:
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="О боте и как написать"),
        ],
        scope=BotCommandScopeDefault(),
    )

    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Панель управления"),
            BotCommand(command="inbox", description="Inbox и статистика"),
            BotCommand(command="clear", description="Очистить всю историю"),
            BotCommand(command="afk_on", description="Статус: в сети"),
            BotCommand(command="afk_off", description="Статус: не в сети"),
            BotCommand(command="status", description="Текущий статус"),
        ],
        scope=BotCommandScopeChat(chat_id=owner_id),
    )
