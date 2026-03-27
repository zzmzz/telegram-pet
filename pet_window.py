"""Desktop pet transparent window with painted character and animations."""

import math
import platform

from PySide6.QtCore import (
    QPoint,
    QPropertyAnimation,
    QRect,
    QSize,
    Qt,
    QTimer,
    Property,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QCursor,
    QFont,
    QPainter,
    QPainterPath,
    QPen,
    QScreen,
)
from PySide6.QtWidgets import QApplication, QWidget


class PetState:
    IDLE = "idle"
    THINKING = "thinking"
    TALKING = "talking"
    HAPPY = "happy"


class PetWidget(QWidget):
    """Transparent, always-on-top, draggable desktop pet."""

    def __init__(self, size: int = 120):
        super().__init__()
        self._size = size
        self._state = PetState.IDLE
        self._frame = 0.0  # animation frame counter
        self._drag_pos: QPoint | None = None

        # window flags: frameless, always on top, transparent
        flags = (
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool  # hide from taskbar
        )
        if platform.system() == "Darwin":
            flags |= Qt.SubWindow  # needed on macOS for transparency
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setFixedSize(size, size)

        # position: bottom-right of primary screen
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(screen.width() - size - 60, screen.height() - size - 60)

        # animation timer (30 fps)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(33)

    # ── state ─────────────────────────────────────────────────────

    @property
    def state(self) -> str:
        return self._state

    @state.setter
    def state(self, value: str):
        self._state = value
        self.update()

    # ── animation tick ────────────────────────────────────────────

    def _tick(self):
        self._frame += 0.05
        self.update()

    # ── painting ──────────────────────────────────────────────────

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        s = self._size
        cx, cy = s // 2, s // 2

        # breathing / bobbing offset
        bob = math.sin(self._frame) * 3

        # ── body (round blob) ──
        body_color = {
            PetState.IDLE: QColor(100, 180, 255),
            PetState.THINKING: QColor(180, 160, 255),
            PetState.TALKING: QColor(100, 220, 180),
            PetState.HAPPY: QColor(255, 200, 100),
        }.get(self._state, QColor(100, 180, 255))

        # shadow
        p.setBrush(QColor(0, 0, 0, 30))
        p.setPen(Qt.NoPen)
        p.drawEllipse(cx - 35, cy + 25, 70, 16)

        # body
        p.setBrush(body_color)
        p.setPen(QPen(body_color.darker(120), 2))
        body_rect = QRect(cx - 40, int(cy - 38 + bob), 80, 76)
        p.drawRoundedRect(body_rect, 36, 36)

        # ── eyes ──
        ey = int(cy - 12 + bob)
        if self._state == PetState.THINKING:
            # looking-up eyes
            p.setBrush(QColor(40, 40, 60))
            p.setPen(Qt.NoPen)
            p.drawEllipse(cx - 16, ey - 6, 10, 10)
            p.drawEllipse(cx + 6, ey - 6, 10, 10)
            # pupils up
            p.setBrush(Qt.white)
            p.drawEllipse(cx - 13, ey - 6, 4, 4)
            p.drawEllipse(cx + 9, ey - 6, 4, 4)
        elif self._state == PetState.HAPPY:
            # happy closed eyes (arcs)
            p.setPen(QPen(QColor(40, 40, 60), 2.5))
            p.setBrush(Qt.NoBrush)
            p.drawArc(cx - 18, ey - 4, 14, 10, 0, 180 * 16)
            p.drawArc(cx + 4, ey - 4, 14, 10, 0, 180 * 16)
        else:
            # normal eyes
            p.setBrush(QColor(40, 40, 60))
            p.setPen(Qt.NoPen)
            p.drawEllipse(cx - 16, ey, 10, 12)
            p.drawEllipse(cx + 6, ey, 10, 12)
            # white highlights
            p.setBrush(Qt.white)
            p.drawEllipse(cx - 13, ey + 2, 4, 4)
            p.drawEllipse(cx + 9, ey + 2, 4, 4)

        # ── mouth ──
        my = int(cy + 10 + bob)
        p.setPen(QPen(QColor(40, 40, 60), 2))
        p.setBrush(Qt.NoBrush)
        if self._state == PetState.TALKING:
            # open mouth
            p.setBrush(QColor(40, 40, 60))
            p.drawEllipse(cx - 6, my, 12, 8)
        elif self._state == PetState.HAPPY:
            # wide smile
            path = QPainterPath()
            path.moveTo(cx - 10, my)
            path.quadTo(cx, my + 10, cx + 10, my)
            p.drawPath(path)
        else:
            # small smile
            path = QPainterPath()
            path.moveTo(cx - 6, my)
            path.quadTo(cx, my + 6, cx + 6, my)
            p.drawPath(path)

        # ── cheeks (blush) ──
        if self._state in (PetState.HAPPY, PetState.TALKING):
            p.setBrush(QColor(255, 150, 150, 80))
            p.setPen(Qt.NoPen)
            p.drawEllipse(cx - 30, int(cy + 2 + bob), 14, 8)
            p.drawEllipse(cx + 16, int(cy + 2 + bob), 14, 8)

        # ── thinking dots ──
        if self._state == PetState.THINKING:
            dot_phase = self._frame * 3
            for i in range(3):
                alpha = int(120 + 135 * math.sin(dot_phase + i * 1.2))
                p.setBrush(QColor(120, 100, 200, alpha))
                p.setPen(Qt.NoPen)
                p.drawEllipse(cx - 12 + i * 12, int(cy + 26 + bob), 6, 6)

        p.end()

    # ── dragging ──────────────────────────────────────────────────

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.pos()

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
