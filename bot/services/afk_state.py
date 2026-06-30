from bot.services.storage import Storage

AFK_KEY = "afk_enabled"


class AfkState:
    def __init__(self, storage: Storage) -> None:
        self._storage = storage

    def is_enabled(self) -> bool:
        return self._storage.get_setting(AFK_KEY, "0") == "1"

    def enable(self) -> None:
        self._storage.set_setting(AFK_KEY, "1")

    def disable(self) -> None:
        self._storage.set_setting(AFK_KEY, "0")
