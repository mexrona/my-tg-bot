from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def message_actions_keyboard(message_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Ответить",
                    callback_data=f"reply:{message_id}",
                ),
                InlineKeyboardButton(
                    text="Удалить",
                    callback_data=f"delete:{message_id}",
                ),
            ]
        ]
    )


def inbox_actions_keyboard(
    message_ids: list[int],
    max_items: int = 25,
) -> InlineKeyboardMarkup | None:
    if not message_ids:
        return None

    rows = []
    for message_id in message_ids[:max_items]:
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"Ответить #{message_id}",
                    callback_data=f"reply:{message_id}",
                ),
                InlineKeyboardButton(
                    text=f"Удалить #{message_id}",
                    callback_data=f"delete:{message_id}",
                ),
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def clear_history_confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Да, удалить всё",
                    callback_data="clear_history:yes",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Отмена",
                    callback_data="clear_history:no",
                )
            ],
        ]
    )
