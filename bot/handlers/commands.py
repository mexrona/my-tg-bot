from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.config import Settings
from bot.services.afk_state import AfkState
from bot.services.inbox import build_inbox_text_chunks
from bot.services.keyboards import clear_history_confirm_keyboard, inbox_actions_keyboard
from bot.services.status_text import VISITOR_WELCOME
from bot.services.storage import Storage

router = Router()


def _is_owner(message: Message, settings: Settings) -> bool:
    return message.from_user is not None and message.from_user.id == settings.owner_id


def _is_owner_user(user_id: int | None, settings: Settings) -> bool:
    return user_id is not None and user_id == settings.owner_id


@router.message(Command("start"))
async def start(message: Message, settings: Settings, afk_state: AfkState) -> None:
    if not _is_owner(message, settings):
        await message.answer(VISITOR_WELCOME)
        return

    if afk_state.is_enabled():
        status = "не в сети 🔴"
    else:
        status = "в сети 🟢"

    await message.answer(
        "Бот отложенных сообщений запущен.\n\n"
        f"Ваш статус (только для вас): {status}\n\n"
        "Команды:\n"
        "/inbox — сообщения и статистика\n"
        "/clear — очистить всю историю\n"
        "/afk_on — отметить «в сети»\n"
        "/afk_off — отметить «не в сети»\n"
        "/status — текущий статус"
    )


@router.message(Command("inbox"))
async def inbox(
    message: Message,
    settings: Settings,
    storage: Storage,
) -> None:
    if not _is_owner(message, settings):
        return

    stats = storage.get_stats()
    unreplied = storage.get_all_unreplied()
    text_chunks = build_inbox_text_chunks(stats, unreplied)

    for index, chunk in enumerate(text_chunks):
        is_last = index == len(text_chunks) - 1
        reply_markup = None
        if is_last and unreplied:
            reply_markup = inbox_actions_keyboard([item.id for item in unreplied])
        await message.answer(chunk, reply_markup=reply_markup)


@router.message(Command("clear"))
async def clear_history(
    message: Message,
    settings: Settings,
    storage: Storage,
) -> None:
    if not _is_owner(message, settings):
        return

    stats = storage.get_stats()
    if stats.total == 0:
        await message.answer("История уже пуста.")
        return

    await message.answer(
        "Удалить всю историю сообщений?\n\n"
        f"Всего сообщений: {stats.total}\n"
        f"Без ответа: {stats.unreplied}\n\n"
        "Это действие нельзя отменить.",
        reply_markup=clear_history_confirm_keyboard(),
    )


@router.callback_query(F.data == "clear_history:yes")
async def clear_history_confirm(
    callback: CallbackQuery,
    settings: Settings,
    storage: Storage,
) -> None:
    if callback.from_user is None or not _is_owner_user(callback.from_user.id, settings):
        await callback.answer("Недоступно", show_alert=True)
        return

    deleted = storage.clear_messages()
    if callback.message:
        await callback.message.edit_text(f"История очищена. Удалено сообщений: {deleted}.")
    await callback.answer()


@router.callback_query(F.data == "clear_history:no")
async def clear_history_cancel(callback: CallbackQuery, settings: Settings) -> None:
    if callback.from_user is None or not _is_owner_user(callback.from_user.id, settings):
        await callback.answer("Недоступно", show_alert=True)
        return

    if callback.message:
        await callback.message.edit_text("Очистка отменена.")
    await callback.answer()


@router.message(Command("status"))
async def status(message: Message, settings: Settings, afk_state: AfkState) -> None:
    if not _is_owner(message, settings):
        return

    if afk_state.is_enabled():
        await message.answer("Ваш статус: не в сети 🔴")
    else:
        await message.answer("Ваш статус: в сети 🟢")


@router.message(Command("afk_on"))
async def afk_on(message: Message, settings: Settings, afk_state: AfkState) -> None:
    if not _is_owner(message, settings):
        return

    afk_state.disable()
    await message.answer("Статус обновлён: в сети 🟢")


@router.message(Command("afk_off"))
async def afk_off(message: Message, settings: Settings, afk_state: AfkState) -> None:
    if not _is_owner(message, settings):
        return

    afk_state.enable()
    await message.answer("Статус обновлён: не в сети 🔴")
