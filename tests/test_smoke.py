"""Smoke tests for bot logic (no Telegram API required)."""
import gc
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bot.services.afk_state import AfkState
from bot.services.inbox import build_inbox_text_chunks, format_unreplied_item
from bot.services.storage import Storage

TEST_DB = Path(__file__).parent / "_smoke_test.db"


def _storage() -> Storage:
    if TEST_DB.exists():
        TEST_DB.unlink()
    return Storage(str(TEST_DB))


def _cleanup_storage(storage: Storage) -> None:
    del storage
    gc.collect()
    if TEST_DB.exists():
        TEST_DB.unlink()


def test_storage_lifecycle() -> None:
    storage = _storage()
    try:
        msg1 = storage.save_message(111, "alice", "Привет")
        msg2 = storage.save_message(222, None, "Сколько стоит?")
        assert msg1 == 1 and msg2 == 2

        stats = storage.get_stats()
        assert stats.total == 2 and stats.replied == 0 and stats.unreplied == 2

        unreplied = storage.get_all_unreplied()
        assert len(unreplied) == 2
        assert unreplied[0].id == msg1

        assert storage.mark_replied(msg1) is True
        stats = storage.get_stats()
        assert stats.replied == 1 and stats.unreplied == 1

        assert storage.delete_message(msg2) is True
        stats = storage.get_stats()
        assert stats.total == 1 and stats.unreplied == 0

        deleted = storage.clear_messages()
        assert deleted == 1
        assert storage.get_stats().total == 0

        msg3 = storage.save_message(333, "bob", "Новое")
        assert msg3 == 1, "ID counter should reset after clear"
    finally:
        _cleanup_storage(storage)


def test_afk_state() -> None:
    storage = _storage()
    try:
        afk = AfkState(storage)

        assert afk.is_enabled() is False  # default: в сети

        afk.enable()
        assert afk.is_enabled() is True

        afk.disable()
        assert afk.is_enabled() is False
    finally:
        _cleanup_storage(storage)


def test_afk_commands_mapping() -> None:
    """/afk_on = в сети, /afk_off = не в сети (owner UX)."""
    storage = _storage()
    try:
        afk = AfkState(storage)

        afk.disable()  # afk_on handler
        assert afk.is_enabled() is False

        afk.enable()  # afk_off handler
        assert afk.is_enabled() is True
    finally:
        _cleanup_storage(storage)


def test_inbox_formatting() -> None:
    from bot.services.storage import InboxStats, StoredMessage

    stats = InboxStats(total=2, replied=1, unreplied=1)
    items = [
        StoredMessage(
            id=5,
            user_id=99,
            username="testuser",
            text="Длинный текст сообщения для проверки обрезки preview",
            created_at=datetime.now().isoformat(timespec="seconds"),
            replied_at=None,
        )
    ]
    chunks = build_inbox_text_chunks(stats, items)
    assert len(chunks) == 1
    assert "#5 @testuser" in chunks[0]
    assert "Без ответа (1)" in chunks[0]
    assert "…" in format_unreplied_item(items[0]) or len(items[0].text) <= 40


def test_imports() -> None:
    from bot.handlers import commands, delete, messages, replies
    from bot.main import main
    from bot.services.router import setup_routers

    router = setup_routers()
    assert router is not None
    assert commands.router is not None
    assert delete.router is not None
    assert replies.router is not None
    assert messages.router is not None
    assert callable(main)


if __name__ == "__main__":
    test_storage_lifecycle()
    test_afk_state()
    test_afk_commands_mapping()
    test_inbox_formatting()
    test_imports()
    print("All smoke tests passed.")
