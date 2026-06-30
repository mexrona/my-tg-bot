from aiogram import Bot, Router
from aiogram.types import Message

from bot.config import Settings
from bot.services.afk_state import AfkState
from bot.services.keyboards import message_actions_keyboard
from bot.services.status_text import MESSAGE_RECEIVED, owner_status_label
from bot.services.storage import Storage
from bot.utils.time import format_time

router = Router()


def _user_label(message: Message) -> str:
    user = message.from_user
    if user is None:
        return "unknown"
    if user.username:
        return f"@{user.username}"
    return str(user.id)


def _message_text(message: Message) -> str:
    if message.text:
        return message.text
    if message.caption:
        return message.caption
    return f"[{message.content_type}]"


def _build_owner_notification(message_id: int, message: Message, is_afk: bool) -> str:
    return (
        f"Новое сообщение #{message_id}:\n"
        f"User: {_user_label(message)}\n"
        f"Status: {owner_status_label(is_afk)}\n"
        "Text:\n"
        f'"{_message_text(message)}"\n'
        "Time:\n"
        f"{format_time()}"
    )


@router.message()
async def handle_incoming_message(
    message: Message,
    bot: Bot,
    settings: Settings,
    storage: Storage,
    afk_state: AfkState,
) -> None:
    if message.from_user is None:
        return

    if message.from_user.id == settings.owner_id:
        return

    text = _message_text(message)
    is_afk = afk_state.is_enabled()

    message_id = storage.save_message(
        user_id=message.from_user.id,
        username=message.from_user.username,
        text=text,
    )

    await bot.send_message(
        chat_id=settings.owner_id,
        text=_build_owner_notification(message_id, message, is_afk),
        reply_markup=message_actions_keyboard(message_id),
    )

    await message.answer(MESSAGE_RECEIVED)
