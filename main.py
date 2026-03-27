"""Telegram Desktop Pet — main entry point."""

import sys
import os
import platform
import traceback
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QIcon, QPixmap, QPainter, QColor
from PySide6.QtWidgets import (
    QApplication, QMenu, QSystemTrayIcon, QMessageBox, QInputDialog,
)

from pet_window import PetState, PetWidget
from chat_bubble import ChatBubble, InputDialog
from tg_client import TelegramThread
from setup_dialog import SetupDialog


def get_app_dir() -> Path:
    """Get the directory where the executable/script lives."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent


def _write_config(config_path: Path, config: dict):
    """Write config dict as TOML."""
    tg = config["telegram"]
    pet = config["pet"]
    content = (
        "[telegram]\n"
        f"api_id = {tg['api_id']}\n"
        f'api_hash = "{tg["api_hash"]}"\n'
        f'phone = "{tg["phone"]}"\n'
        f'bot_username = "{tg["bot_username"]}"\n'
        "\n[pet]\n"
        f"size = {pet['size']}\n"
        f"bubble_max_width = {pet['bubble_max_width']}\n"
        f"bubble_timeout = {pet['bubble_timeout']}\n"
    )
    config_path.write_text(content, encoding="utf-8")


def _read_toml(config_path: Path) -> dict:
    if sys.version_info >= (3, 11):
        import tomllib
    else:
        try:
            import tomli as tomllib
        except ImportError:
            import tomllib
    with open(config_path, "rb") as f:
        return tomllib.load(f)


def load_config() -> dict:
    config_path = get_app_dir() / "config.toml"

    if config_path.exists():
        return _read_toml(config_path)

    # First run — show setup dialog
    dialog = SetupDialog()
    if dialog.exec() != SetupDialog.DialogCode.Accepted:
        sys.exit(0)

    config = dialog.get_config()
    _write_config(config_path, config)
    return config


def create_tray_icon() -> QPixmap:
    """Generate a simple tray icon programmatically."""
    px = QPixmap(32, 32)
    px.fill(Qt.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing)
    p.setBrush(QColor(100, 180, 255))
    p.setPen(Qt.NoPen)
    p.drawRoundedRect(2, 2, 28, 28, 12, 12)
    # eyes
    p.setBrush(QColor(40, 40, 60))
    p.drawEllipse(8, 10, 5, 6)
    p.drawEllipse(19, 10, 5, 6)
    # mouth
    p.setBrush(Qt.NoBrush)
    from PySide6.QtGui import QPen, QPainterPath
    p.setPen(QPen(QColor(40, 40, 60), 1.5))
    path = QPainterPath()
    path.moveTo(12, 20)
    path.quadTo(16, 24, 20, 20)
    p.drawPath(path)
    p.end()
    return px


class TelegramPetApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        config = load_config()
        tg_cfg = config["telegram"]
        pet_cfg = config.get("pet", {})

        pet_size = pet_cfg.get("size", 120)
        self.bubble_max_width = pet_cfg.get("bubble_max_width", 300)
        self.bubble_timeout = pet_cfg.get("bubble_timeout", 15)

        # ── pet widget ──
        self.pet = PetWidget(pet_size)
        self.pet.mouseDoubleClickEvent = self._on_double_click
        # right-click menu on pet
        self.pet.setContextMenuPolicy(Qt.CustomContextMenu)
        self.pet.customContextMenuRequested.connect(self._show_context_menu)

        # ── system tray ──
        self.tray = QSystemTrayIcon(QIcon(create_tray_icon()), self.app)
        tray_menu = QMenu()
        tray_menu.addAction("Send Message", self._open_input)
        tray_menu.addSeparator()
        tray_menu.addAction("Show/Hide", self._toggle_pet)
        tray_menu.addAction("Settings", self._open_settings)
        tray_menu.addSeparator()
        tray_menu.addAction("Quit", self._quit)
        self.tray.setContextMenu(tray_menu)
        self.tray.setToolTip("Telegram Pet")
        self.tray.activated.connect(self._on_tray_activated)
        self.tray.show()

        # ── telegram client ──
        self.tg = TelegramThread(
            api_id=tg_cfg["api_id"],
            api_hash=tg_cfg["api_hash"],
            phone=tg_cfg["phone"],
            bot_username=tg_cfg["bot_username"],
        )
        self.tg.connected.connect(self._on_connected)
        self.tg.message_received.connect(self._on_message)
        self.tg.error.connect(self._on_error)
        self.tg.code_requested.connect(self._on_code_requested)

        # ── state ──
        self._bubbles: list[ChatBubble] = []
        self._input_dialog: InputDialog | None = None

    def run(self) -> int:
        self.pet.show()
        self.tg.start()
        return self.app.exec()

    # ── slots ─────────────────────────────────────────────────────

    def _on_connected(self):
        self._show_bubble("Connected to Telegram")
        self.pet.state = PetState.HAPPY
        QTimer.singleShot(3000, lambda: setattr(self.pet, 'state', PetState.IDLE))

    def _on_message(self, text: str):
        self.pet.state = PetState.TALKING
        self._show_bubble(text)
        QTimer.singleShot(4000, lambda: setattr(self.pet, 'state', PetState.IDLE))

    def _on_error(self, msg: str):
        self._show_bubble(f"Error: {msg}")

    def _on_code_requested(self):
        """Telethon needs a verification code — ask via GUI dialog."""
        code, ok = QInputDialog.getText(
            None, "Telegram Verification",
            "Please enter the Telegram verification code:",
        )
        self.tg.provide_code(code if ok else "")

    def _on_double_click(self, event):
        self._open_input()

    def _show_context_menu(self, pos):
        menu = QMenu()
        menu.addAction("Send Message", self._open_input)
        menu.addSeparator()
        menu.addAction("Quit", self._quit)
        menu.exec(self.pet.mapToGlobal(pos))

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._toggle_pet()

    # ── actions ───────────────────────────────────────────────────

    def _open_input(self):
        if self._input_dialog and self._input_dialog.isVisible():
            self._input_dialog.close()
            return
        self._input_dialog = InputDialog()
        self._input_dialog.message_sent.connect(self._send_message)
        self._input_dialog.show_near(self.pet.pos(), self.pet.width())

    def _send_message(self, text: str):
        self.pet.state = PetState.THINKING
        self.tg.send_message(text)

    def _show_bubble(self, text: str, timeout: int | None = None):
        # close old bubbles
        for b in self._bubbles:
            b.close()
        self._bubbles.clear()

        bubble = ChatBubble(
            text,
            max_width=self.bubble_max_width,
            timeout=timeout or self.bubble_timeout,
        )
        bubble.show_near(self.pet.pos(), self.pet.width())
        self._bubbles.append(bubble)

    def _toggle_pet(self):
        if self.pet.isVisible():
            self.pet.hide()
        else:
            self.pet.show()

    def _open_settings(self):
        config_path = get_app_dir() / "config.toml"
        current = _read_toml(config_path) if config_path.exists() else {}
        dialog = SetupDialog(defaults=current)
        if dialog.exec() == SetupDialog.DialogCode.Accepted:
            config = dialog.get_config()
            _write_config(config_path, config)
            QMessageBox.information(
                None, "Telegram Pet",
                "Settings saved. Please restart the app for changes to take effect.",
            )

    def _quit(self):
        self.tg.stop()
        self.tray.hide()
        self.app.quit()


def main():
    try:
        pet_app = TelegramPetApp()
        sys.exit(pet_app.run())
    except Exception:
        # In windowed mode, show errors as a message box
        app = QApplication.instance() or QApplication(sys.argv)
        QMessageBox.critical(
            None, "Telegram Pet - Error",
            traceback.format_exc(),
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
