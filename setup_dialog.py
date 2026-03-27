"""First-run setup dialog for configuring Telegram credentials."""

import platform

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIntValidator
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)


class SetupDialog(QDialog):
    """Configuration dialog shown on first run or when config is missing."""

    def __init__(self, defaults: dict | None = None):
        super().__init__()
        defaults = defaults or {}
        tg = defaults.get("telegram", {})
        pet = defaults.get("pet", {})

        self.setWindowTitle("Telegram Pet - Setup")
        self.setFixedSize(540, 480)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # ── title ──
        title = QLabel("Telegram Pet")
        title.setFont(QFont("Segoe UI" if platform.system() == "Windows" else "PingFang SC", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("First-run setup / Configure your Telegram connection")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #666; font-size: 12px; margin-bottom: 6px;")
        layout.addWidget(subtitle)

        # ── telegram group ──
        tg_group = QGroupBox("Telegram")
        tg_form = QFormLayout(tg_group)
        tg_form.setLabelAlignment(Qt.AlignRight)
        tg_form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        self.api_id_input = QLineEdit(str(tg.get("api_id", "")))
        self.api_id_input.setPlaceholderText("e.g. 12345678")
        self.api_id_input.setValidator(QIntValidator(0, 999999999))
        self.api_id_input.setMinimumHeight(32)
        tg_form.addRow("API ID:", self.api_id_input)

        self.api_hash_input = QLineEdit(str(tg.get("api_hash", "")))
        self.api_hash_input.setPlaceholderText("e.g. a1b2c3d4e5f6...")
        self.api_hash_input.setMinimumHeight(32)
        tg_form.addRow("API Hash:", self.api_hash_input)

        self.phone_input = QLineEdit(str(tg.get("phone", "")))
        self.phone_input.setPlaceholderText("e.g. +8613800138000")
        self.phone_input.setMinimumHeight(32)
        tg_form.addRow("Phone:", self.phone_input)

        self.bot_input = QLineEdit(str(tg.get("bot_username", "")))
        self.bot_input.setPlaceholderText("Bot username without @")
        self.bot_input.setMinimumHeight(32)
        tg_form.addRow("Bot Username:", self.bot_input)

        api_link = QLabel('<a href="https://my.telegram.org/apps">Get API ID & Hash from my.telegram.org</a>')
        api_link.setOpenExternalLinks(True)
        api_link.setStyleSheet("font-size: 11px; margin-top: 2px;")
        tg_form.addRow("", api_link)

        layout.addWidget(tg_group)

        # ── pet group ──
        pet_group = QGroupBox("Pet Settings")
        pet_form = QFormLayout(pet_group)
        pet_form.setLabelAlignment(Qt.AlignRight)

        self.size_spin = QSpinBox()
        self.size_spin.setRange(60, 300)
        self.size_spin.setValue(pet.get("size", 120))
        self.size_spin.setSuffix(" px")
        pet_form.addRow("Pet Size:", self.size_spin)

        self.bubble_width_spin = QSpinBox()
        self.bubble_width_spin.setRange(150, 600)
        self.bubble_width_spin.setValue(pet.get("bubble_max_width", 300))
        self.bubble_width_spin.setSuffix(" px")
        pet_form.addRow("Bubble Width:", self.bubble_width_spin)

        self.bubble_timeout_spin = QSpinBox()
        self.bubble_timeout_spin.setRange(3, 120)
        self.bubble_timeout_spin.setValue(pet.get("bubble_timeout", 15))
        self.bubble_timeout_spin.setSuffix(" s")
        pet_form.addRow("Bubble Timeout:", self.bubble_timeout_spin)

        layout.addWidget(pet_group)

        # ── buttons ──
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        save_btn = QPushButton("Save && Start")
        save_btn.setFixedSize(120, 34)
        save_btn.setStyleSheet("""
            QPushButton {
                background: #4a9eff; color: white;
                border: none; border-radius: 6px;
                font-size: 13px; font-weight: bold;
            }
            QPushButton:hover { background: #3a8eef; }
        """)
        save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedSize(80, 34)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #e0e0e0; color: #333;
                border: none; border-radius: 6px; font-size: 13px;
            }
            QPushButton:hover { background: #d0d0d0; }
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

        # ── global style ──
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ccc;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 14px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 4px;
            }
            QLineEdit {
                padding: 6px 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 13px;
                min-width: 280px;
            }
            QSpinBox {
                padding: 6px 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 13px;
            }
            QLineEdit:focus, QSpinBox:focus {
                border-color: #4a9eff;
            }
        """)

    def _on_save(self):
        api_id = self.api_id_input.text().strip()
        api_hash = self.api_hash_input.text().strip()
        phone = self.phone_input.text().strip()
        bot = self.bot_input.text().strip()

        missing = []
        if not api_id:
            missing.append("API ID")
        if not api_hash:
            missing.append("API Hash")
        if not phone:
            missing.append("Phone")
        if not bot:
            missing.append("Bot Username")

        if missing:
            QMessageBox.warning(self, "Missing Fields", f"Please fill in: {', '.join(missing)}")
            return

        self.accept()

    def get_config(self) -> dict:
        return {
            "telegram": {
                "api_id": int(self.api_id_input.text().strip()),
                "api_hash": self.api_hash_input.text().strip(),
                "phone": self.phone_input.text().strip(),
                "bot_username": self.bot_input.text().strip().lstrip("@"),
            },
            "pet": {
                "size": self.size_spin.value(),
                "bubble_max_width": self.bubble_width_spin.value(),
                "bubble_timeout": self.bubble_timeout_spin.value(),
            },
        }
