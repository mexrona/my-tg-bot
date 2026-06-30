FAQ_KEYWORDS = (
    "что ты делаешь",
    "кто ты",
    "цена",
    "сколько стоит",
)

FAQ_REPLY = (
    "Занимаюсь разработкой Telegram-ботов и сайтов.\n\n"
    "Отвечаю с небольшой задержкой — опишите, пожалуйста, вашу задачу, "
    "и я обязательно вернусь с ответом."
)


def match_faq(text: str) -> bool:
    normalized = text.strip().lower()
    return any(keyword in normalized for keyword in FAQ_KEYWORDS)


def get_faq_reply() -> str:
    return FAQ_REPLY
