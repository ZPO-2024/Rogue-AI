"""
ROGUE - Local AI Overlay
Offline-first Ubuntu AI assistant with voice, screen awareness,
and hardware integration.

Part of the ZeroPoint Operations / Split Reality Concepts stack.
"""

__version__ = "0.1.0"
__author__ = "ZeroPoint Operations"

from .config import config
from .ollama_client import ollama_client
from .screen_capture import screen_capture
from .pc_control import pc_controller
from .tts import tts_engine
from .rogue_overlay import overlay

__all__ = [
    "config",
    "ollama_client",
    "screen_capture",
    "pc_controller",
    "tts_engine",
    "overlay",
]
