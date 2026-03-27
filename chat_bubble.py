"""Chat bubble (bot reply) and input dialog for the desktop pet."""

import platform

from PySide6.QtCore import QPoint, QPropertyAnimation, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class ChatBubble(QWidget):
    """Floating speech bubble that appears near the pet."""

    def __init__(self, text: str, max_width: int = 300, timeout: int = 15):
        super().__init__()
        self._text = text
        self._max_width = max_width

        flags = (
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
        )
        if platform.system() == "Darwin":
            flags |= Qt.SubWindow
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        # calculate size based on text
        font = QFont("Microsoft YaHei" if platform.system() == "Windows" else "PingFang SC", 11)
        from PySide6.QtGui import QFontMetrics
        fm = QFontMetrics(font)
        text_rect = fm.boundingRect(0, 0, max_width - 28, 10000, Qt.TextWordWrap, text)
        w = min(max_width, text_rect.width() + 32)
        h = text_rect.height() + 32 + 12  # +12 for tail
        self.setFixedSize(max(w, 60), max(h, 50))
        self._font = font

        # auto-dismiss
        if timeout > 0:
            QTimer.singleShot(timeout * 1000, self.close)

    def show_near(self, pet_pos: QPoint, pet_size: int):
        """Position the bubble above the pet."""
        x = pet_pos.x() + pet_size // 2 - self.width() // 2
        y = pet_pos.y() - self.height() + 5
        # keep on screen
        screen = QApplication.primaryScreen().availableGeometry()
        x = max(5, min(x, screen.width() - self.width() - 5))
        y = max(5, y)
        self.move(x, y)
        self.show()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        tail_h = 10

        # bubble body
        bg = QColor(255, 255, 255, 240)
        border = QColor(180, 180, 180)
        path = QPainterPath()
        body_rect = (2, 2, w - 4, h - tail_h - 4)
        path.addRoundedRect(*body_rect, 12, 12)

        # tail (small triangle pointing down-center)
        cx = w // 2
        path.moveTo(cx - 6, h - tail_h - 2)
        path.lineTo(cx, h - 2)
        path.lineTo(cx + 6, h - tail_h - 2)

        p.setBrush(bg)
        p.setPen(QPen(border, 1.5))
        p.drawPath(path)

        # text
        p.setPen(QColor(30, 30, 30))
        p.setFont(self._font)
        text_rect = (14, 10, w - 28, h - tail_h - 20)
        p.drawText(*text_rect, Qt.TextWordWrap | Qt.AlignLeft | Qt.AlignTop, self._text)
        p.end()

    def mousePressEvent(self, event):
        self.close()


class InputDialog(QWidget):
    """Compact input box for sending messages to the bot."""

    message_sent = Signal(str)

    def __init__(self):
        super().__init__()
        flags = (
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
        )
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(340, 100)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        self._input = QTextEdit()
        self._input.setPlaceholderText("输入消息，Ctrl+Enter 发送...")
        self._input.setStyleSheet("""
            QTextEdit {
                background: rgba(255,255,255,230);
                border: 1.5px solid #bbb;
                border-radius: 8px;
                padding: 6px;
                font-size: 13px;
            }
        """)
        layout.addWidget(self._input)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        send_btn = QPushButton("发送")
        send_btn.setFixedSize(60, 28)
        send_btn.setStyleSheet("""
            QPushButton {
                background: #4a9eff;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 12px;
            }
            QPushButton:hover { background: #3a8eef; }
        """)
        send_btn.clicked.connect(self._on_send)
        btn_layout.addWidget(send_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.setFixedSize(60, 28)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #e0e0e0;
                color: #333;
                border: none;
                border-radius: 6px;
                font-size: 12px;
            }
            QPushButton:hover { background: #d0d0d0; }
        """)
        cancel_btn.clicked.connect(self.close)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return and event.modifiers() & Qt.ControlModifier:
            self._on_send()
        elif event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)

    def _on_send(self):
        text = self._input.toPlainText().strip()
        if text:
            self.message_sent.emit(text)
            self._input.clear()
            self.close()

    def show_near(self, pet_pos: QPoint, pet_size: int):
        x = pet_pos.x() + pet_size // 2 - self.width() // 2
        y = pet_pos.y() - self.height() - 10
        screen = QApplication.primaryScreen().availableGeometry()
        x = max(5, min(x, screen.width() - self.width() - 5))
        y = max(5, y)
        self.move(x, y)
        self.show()
        self._input.setFocus()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(QColor(245, 245, 245, 230))
        p.setPen(QPen(QColor(180, 180, 180), 1.5))
        p.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 12, 12)
        p.end()
