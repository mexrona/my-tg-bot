from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.config import Settings
from bot.services.storage import Storage

router = Router()


def _is_owner_user(user_id: int | None, settings: Settings) -> bool:
    return user_id is not None and user_id == settings.owner_id


@router.callback_query(F.data.startswith("delete:"))
async def delete_message_callback(
    callback: CallbackQuery,
    settings: Settings,
    storage: Storage,
) -> None:
    if callback.from_user is None or not _is_owner_user(callback.from_user.id, settings):
        await callback.answer("Недоступно", show_alert=True)
        return

    if callback.data is None:
        return

    message_id = int(callback.data.removeprefix("delete:"))
    stored = storage.get_message(message_id)
    if stored is None:
        await callback.answer("Сообщение не найдено", show_alert=True)
        return

    storage.delete_message(message_id)

    if (
        callback.message
        and callback.message.text
        and callback.message.text.startswith("Новое сообщение #")
    ):
        await callback.message.edit_text(
            f"{callback.message.text}\n\n🗑 Сообщение #{message_id} удалено из inbox."
        )

    await callback.answer(f"Сообщение #{message_id} удалено")
