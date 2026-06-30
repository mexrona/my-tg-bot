from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from bot.config import Settings
from bot.services.afk_state import AfkState
from bot.services.storage import Storage


class InjectMiddleware(BaseMiddleware):
    def __init__(
        self,
        settings: Settings,
        storage: Storage,
        afk_state: AfkState,
    ) -> None:
        self.settings = settings
        self.storage = storage
        self.afk_state = afk_state

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        data["settings"] = self.settings
        data["storage"] = self.storage
        data["afk_state"] = self.afk_state
        return await handler(event, data)
