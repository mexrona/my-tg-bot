from aiogram import Bot, F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from bot.config import Settings
from bot.services.inbox import user_label
from bot.services.status_text import owner_reply_prompt, owner_reply_sent, user_reply_text
from bot.services.storage import Storage

router = Router()


class ReplyState(StatesGroup):
    waiting_text = State()


def _is_owner(user_id: int | None, settings: Settings) -> bool:
    return user_id is not None and user_id == settings.owner_id


@router.callback_query(F.data.startswith("reply:"))
async def start_reply(
    callback: CallbackQuery,
    state: FSMContext,
    settings: Settings,
    storage: Storage,
) -> None:
    if callback.from_user is None or not _is_owner(callback.from_user.id, settings):
        await callback.answer("Недоступно", show_alert=True)
        return

    if callback.data is None:
        return

    message_id = int(callback.data.removeprefix("reply:"))
    stored = storage.get_message(message_id)
    if stored is None:
        await callback.answer("Сообщение не найдено", show_alert=True)
        return

    if stored.replied_at is not None:
        await callback.answer("На это сообщение уже ответили", show_alert=True)
        return

    await state.set_state(ReplyState.waiting_text)
    await state.update_data(message_id=message_id, user_id=stored.user_id)

    label = user_label(stored.username, stored.user_id)
    if callback.message:
        await callback.message.answer(
            owner_reply_prompt(message_id, label, stored.text),
        )
    await callback.answer(f"Вопрос #{message_id}")


@router.message(StateFilter(ReplyState.waiting_text))
async def send_reply(
    message: Message,
    state: FSMContext,
    bot: Bot,
    settings: Settings,
    storage: Storage,
) -> None:
    if message.from_user is None or not _is_owner(message.from_user.id, settings):
        return

    if not message.text:
        await message.answer("Отправьте текстовый ответ.")
        return

    data = await state.get_data()
    message_id = data.get("message_id")
    user_id = data.get("user_id")

    if message_id is None or user_id is None:
        await state.clear()
        await message.answer("Не удалось найти сообщение. Нажмите «Ответить» снова.")
        return

    stored = storage.get_message(int(message_id))
    if stored is None or stored.replied_at is not None:
        await state.clear()
        await message.answer("Сообщение уже обработано.")
        return

    label = user_label(stored.username, stored.user_id)
    await bot.send_message(
        chat_id=int(user_id),
        text=user_reply_text(int(message_id), message.text),
    )
    storage.mark_replied(int(message_id))
    await state.clear()
    await message.answer(owner_reply_sent(int(message_id), label))
