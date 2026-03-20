"""
rogue_overlay.py - ROGUE System Tray / Overlay UI
Lightweight desktop indicator showing ROGUE status.
Uses PyQt5 system tray if available, falls back to terminal display.
Part of the ROGUE Local AI Overlay stack.
"""

import logging
import os
import threading
from typing import Optional

logger = logging.getLogger(__name__)

try:
    from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
    from PyQt5.QtGui import QIcon, QPixmap, QColor
    from PyQt5.QtCore import Qt, QTimer
    HAS_QT = True
except ImportError:
    HAS_QT = False
    logger.info("PyQt5 not available - using terminal overlay mode")


def _make_icon(color: str = "#00ff88", size: int = 22) -> "QIcon":
    """Generate a simple colored circle icon for the tray."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    from PyQt5.QtGui import QPainter
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QColor(color))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(2, 2, size - 4, size - 4)
    painter.end()
    return QIcon(pixmap)


class TerminalOverlay:
    """Fallback overlay that prints status to terminal."""

    def __init__(self):
        self.status = "OFFLINE"
        self.model = "none"

    def set_status(self, status: str, model: str = "", message: str = "") -> None:
        self.status = status
        self.model = model
        color = "\033[92m" if status == "ACTIVE" else "\033[93m" if status == "THINKING" else "\033[90m"
        reset = "\033[0m"
        msg = f"{color}[ROGUE:{status}]{reset} model={model or 'none'}"
        if message:
            msg += f" | {message[:80]}"
        print(msg)

    def show(self) -> None:
        print("[ROGUE] Terminal overlay active (no Qt)")

    def hide(self) -> None:
        pass


class QtOverlay:
    """System tray overlay using PyQt5."""

    def __init__(self, app: "QApplication"):
        self.app = app
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(_make_icon("#555555"))
        self.tray.setToolTip("ROGUE — Offline AI Overlay")

        menu = QMenu()
        self.status_action = QAction("Status: OFFLINE")
        self.status_action.setEnabled(False)
        menu.addAction(self.status_action)
        menu.addSeparator()

        quit_action = QAction("Quit ROGUE")
        quit_action.triggered.connect(self.app.quit)
        menu.addAction(quit_action)

        self.tray.setContextMenu(menu)

    def set_status(self, status: str, model: str = "", message: str = "") -> None:
        color_map = {
            "ACTIVE": "#00ff88",
            "THINKING": "#ffaa00",
            "LISTENING": "#00aaff",
            "OFFLINE": "#555555",
            "ERROR": "#ff4444",
        }
        color = color_map.get(status, "#888888")
        self.tray.setIcon(_make_icon(color))
        label = f"ROGUE: {status}"
        if model:
            label += f" | {model}"
        self.tray.setToolTip(label)
        self.status_action.setText(label)
        if message:
            self.tray.showMessage("ROGUE", message[:100], QSystemTrayIcon.Information, 2000)

    def show(self) -> None:
        self.tray.show()

    def hide(self) -> None:
        self.tray.hide()


class RogueOverlay:
    """
    Main overlay controller — picks Qt or terminal backend automatically.
    Thread-safe status updates.
    """

    def __init__(self):
        self._backend = None
        self._lock = threading.Lock()
        self._initialized = False

    def init(self) -> None:
        if self._initialized:
            return
        if HAS_QT and os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"):
            try:
                app = QApplication.instance() or QApplication([])
                self._backend = QtOverlay(app)
                logger.info("ROGUE overlay: Qt tray mode")
            except Exception as e:
                logger.warning(f"Qt tray failed: {e}, falling back to terminal")
                self._backend = TerminalOverlay()
        else:
            self._backend = TerminalOverlay()
            logger.info("ROGUE overlay: terminal mode")
        self._backend.show()
        self._initialized = True

    def set_status(self, status: str, model: str = "", message: str = "") -> None:
        if not self._initialized:
            self.init()
        with self._lock:
            try:
                self._backend.set_status(status, model, message)
            except Exception as e:
                logger.error(f"Overlay status update failed: {e}")

    def active(self, model: str = "", message: str = "") -> None:
        self.set_status("ACTIVE", model, message)

    def thinking(self, model: str = "", message: str = "") -> None:
        self.set_status("THINKING", model, message)

    def listening(self) -> None:
        self.set_status("LISTENING")

    def offline(self) -> None:
        self.set_status("OFFLINE")

    def error(self, message: str = "") -> None:
        self.set_status("ERROR", message=message)


# Singleton
overlay = RogueOverlay()
