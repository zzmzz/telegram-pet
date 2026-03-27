"""Telegram client running in a background QThread via Telethon."""

import asyncio
import threading
from pathlib import Path
import sys

from PySide6.QtCore import QThread, Signal
from telethon import TelegramClient, events


def _get_session_dir() -> Path:
    """Session file lives next to the executable, not inside _MEIPASS."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent


class TelegramThread(QThread):
    """Runs Telethon event loop in a dedicated thread."""

    message_received = Signal(str)  # bot reply text
    connected = Signal()
    disconnected = Signal()
    error = Signal(str)
    code_requested = Signal()  # ask UI for verification code

    def __init__(self, api_id: int, api_hash: str, phone: str, bot_username: str):
        super().__init__()
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        self.bot_username = bot_username
        self._loop: asyncio.AbstractEventLoop | None = None
        self._client: TelegramClient | None = None
        self._bot_entity = None
        self._code_event = threading.Event()
        self._code_value = ""

    # ── public (called from main thread) ──────────────────────────

    def send_message(self, text: str):
        """Schedule a message send from any thread."""
        if self._loop and self._client:
            asyncio.run_coroutine_threadsafe(self._send(text), self._loop)

    def provide_code(self, code: str):
        """Called by UI after user enters verification code."""
        self._code_value = code
        self._code_event.set()

    def stop(self):
        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)
        self.wait(5000)

    # ── internal ──────────────────────────────────────────────────

    def _get_code(self):
        """Called by Telethon when it needs a verification code."""
        self._code_event.clear()
        self.code_requested.emit()  # ask UI to show input dialog
        self._code_event.wait(timeout=120)  # wait up to 2 minutes
        return self._code_value

    async def _send(self, text: str):
        try:
            if not self._bot_entity:
                self._bot_entity = await self._client.get_entity(self.bot_username)
            await self._client.send_message(self._bot_entity, text)
        except Exception as e:
            self.error.emit(f"Send failed: {e}")

    def run(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        session_path = str(_get_session_dir() / "telegram_pet_session")
        self._client = TelegramClient(session_path, self.api_id, self.api_hash)

        async def _main():
            await self._client.start(
                phone=self.phone,
                code_callback=self._get_code,
            )
            self._bot_entity = await self._client.get_entity(self.bot_username)
            self.connected.emit()

            @self._client.on(events.NewMessage(from_users=[self._bot_entity]))
            async def on_bot_reply(event):
                self.message_received.emit(event.message.text or "[Media message]")

            await self._client.run_until_disconnected()

        try:
            self._loop.run_until_complete(_main())
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.disconnected.emit()
