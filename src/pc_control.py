"""
pc_control.py - ROGUE PC Control Module
Safety-gated mouse/keyboard automation. DISABLED by default.
Part of the ROGUE Local AI Overlay stack.
"""

import os
import logging

logger = logging.getLogger(__name__)

# SAFETY GATE: PC control is disabled by default
PC_CONTROL_ENABLED = os.getenv("ROGUE_PC_CONTROL", "false").lower() == "true"

try:
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1
    HAS_PYAUTOGUI = True
except ImportError:
    HAS_PYAUTOGUI = False
    logger.warning("pyautogui not available - PC control disabled")


class PCController:
    """Safety-gated PC automation controller."""

    def __init__(self):
        self.enabled = PC_CONTROL_ENABLED and HAS_PYAUTOGUI
        if self.enabled:
            logger.info("PCController initialized - CONTROL ENABLED")
        else:
            logger.info("PCController initialized - CONTROL DISABLED (safe mode)")

    def _check_enabled(self, action_name: str) -> bool:
        if not self.enabled:
            logger.warning(f"PC control blocked: {action_name} requested but control is disabled")
            return False
        return True

    def move_mouse(self, x: int, y: int, duration: float = 0.3) -> bool:
        if not self._check_enabled("move_mouse"):
            return False
        try:
            pyautogui.moveTo(x, y, duration=duration)
            return True
        except Exception as e:
            logger.error(f"Mouse move failed: {e}")
            return False

    def click(self, x: int = None, y: int = None, button: str = "left") -> bool:
        if not self._check_enabled("click"):
            return False
        try:
            if x is not None and y is not None:
                pyautogui.click(x, y, button=button)
            else:
                pyautogui.click(button=button)
            return True
        except Exception as e:
            logger.error(f"Click failed: {e}")
            return False

    def type_text(self, text: str, interval: float = 0.05) -> bool:
        if not self._check_enabled("type_text"):
            return False
        try:
            pyautogui.typewrite(text, interval=interval)
            return True
        except Exception as e:
            logger.error(f"Type failed: {e}")
            return False

    def hotkey(self, *keys) -> bool:
        if not self._check_enabled("hotkey"):
            return False
        try:
            pyautogui.hotkey(*keys)
            return True
        except Exception as e:
            logger.error(f"Hotkey failed: {e}")
            return False

    def scroll(self, clicks: int, x: int = None, y: int = None) -> bool:
        if not self._check_enabled("scroll"):
            return False
        try:
            if x is not None and y is not None:
                pyautogui.scroll(clicks, x=x, y=y)
            else:
                pyautogui.scroll(clicks)
            return True
        except Exception as e:
            logger.error(f"Scroll failed: {e}")
            return False

    def get_screen_size(self):
        if not HAS_PYAUTOGUI:
            return (1920, 1080)
        return pyautogui.size()

    def status(self) -> dict:
        return {
            "enabled": self.enabled,
            "pc_control_env": PC_CONTROL_ENABLED,
            "pyautogui_available": HAS_PYAUTOGUI,
            "failsafe": True,
        }


# Singleton
pc_controller = PCController()
