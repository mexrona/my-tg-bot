from datetime import datetime

from bot.services.storage import InboxStats, StoredMessage
from bot.utils.time import format_time


def user_label(username: str | None, user_id: int) -> str:
    if username:
        return f"@{username}"
    return f"id:{user_id}"


def truncate_text(text: str, limit: int = 40) -> str:
    one_line = " ".join(text.split())
    if len(one_line) <= limit:
        return one_line
    return one_line[: limit - 1] + "…"


def format_message_time(created_at: str) -> str:
    return format_time(datetime.fromisoformat(created_at))


def format_inbox_header(stats: InboxStats) -> str:
    return (
        "<b>Inbox</b>\n\n"
        f"Всего сообщений: {stats.total}\n"
        f"Отвечено: {stats.replied}\n"
        f"Без ответа: {stats.unreplied}"
    )


def format_unreplied_item(message: StoredMessage) -> str:
    label = user_label(message.username, message.user_id)
    preview = truncate_text(message.text)
    time_label = format_message_time(message.created_at)
    return f"#{message.id} {label} — «{preview}» — {time_label}"


def build_inbox_text_chunks(stats: InboxStats, unreplied: list[StoredMessage]) -> list[str]:
    header = format_inbox_header(stats)
    if not unreplied:
        return [f"{header}\n\nНет сообщений без ответа."]

    chunks: list[str] = []
    current = f"{header}\n\n<b>Без ответа ({len(unreplied)}):</b>"

    for item in unreplied:
        line = format_unreplied_item(item)
        candidate = f"{current}\n{line}"
        if len(candidate) > 3800:
            chunks.append(current)
            current = line
        else:
            current = candidate

    chunks.append(current)
    return chunks
