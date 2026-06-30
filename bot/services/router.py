from aiogram import Router

from bot.handlers import commands, delete, messages, replies


def setup_routers() -> Router:
    root = Router()
    root.include_router(commands.router)
    root.include_router(delete.router)
    root.include_router(replies.router)
    root.include_router(messages.router)
    return root
