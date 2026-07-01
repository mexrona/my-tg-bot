VISITOR_WELCOME = (
    "Привет! 👋\n\n"
    "Это бот для связи со мной.\n"
    "Напишите сюда ваш вопрос или задачу — я получу сообщение "
    "и обязательно отвечу, как только смогу."
)


def message_received(message_id: int) -> str:
    return (
        "Сообщение успешно отправлено ✅\n\n"
        f"Номер вашего вопроса: #{message_id}\n\n"
        "Я получила его и отвечу вам лично, как только смогу."
    )


def owner_reply_prompt(message_id: int, user_label: str, question_text: str) -> str:
    preview = " ".join(question_text.split())
    if len(preview) > 200:
        preview = preview[:199] + "…"
    return (
        f"<b>Ответ на вопрос #{message_id}</b>\n\n"
        f"Пользователь: {user_label}\n"
        f"Вопрос:\n«{preview}»\n\n"
        "Напишите ваш ответ:"
    )


def user_reply_text(message_id: int, question_text: str, answer_text: str) -> str:
    return (
        f"Ответ на ваш вопрос #{message_id}:\n"
        f"{question_text.strip()}\n\n"
        f"{answer_text.strip()}"
    )


def owner_reply_sent(message_id: int, user_label: str) -> str:
    return f"Ответ на вопрос #{message_id} отправлен пользователю {user_label}."


def owner_status_label(is_afk: bool) -> str:
    return "не в сети" if is_afk else "в сети"
