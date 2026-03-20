"""
tts.py - ROGUE Text-to-Speech Module
Supports Piper TTS (offline, primary) with espeak fallback.
Part of the ROGUE Local AI Overlay stack.
"""

import os
import subprocess
import tempfile
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

PIPER_PATH = os.getenv("PIPER_PATH", "/usr/local/bin/piper")
PIPER_MODEL = os.getenv("PIPER_MODEL", "en_US-lessac-medium")
PIPER_MODELS_DIR = os.getenv("PIPER_MODELS_DIR", str(Path.home() / ".local/share/piper/models"))
TTS_BACKEND = os.getenv("TTS_BACKEND", "piper")  # piper | espeak | none


def _check_piper() -> bool:
    return Path(PIPER_PATH).exists()


def _speak_piper(text: str) -> bool:
    model_path = Path(PIPER_MODELS_DIR) / f"{PIPER_MODEL}.onnx"
    if not model_path.exists():
        logger.warning(f"Piper model not found: {model_path}")
        return False
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name
        proc = subprocess.run(
            [PIPER_PATH, "--model", str(model_path), "--output_file", tmp_path],
            input=text.encode(),
            capture_output=True,
            timeout=30,
        )
        if proc.returncode != 0:
            logger.error(f"Piper failed: {proc.stderr.decode()}")
            return False
        subprocess.run(["aplay", "-q", tmp_path], check=True, timeout=60)
        Path(tmp_path).unlink(missing_ok=True)
        return True
    except Exception as e:
        logger.error(f"Piper TTS error: {e}")
        return False


def _speak_espeak(text: str) -> bool:
    try:
        subprocess.run(["espeak", "-s", "150", text], check=True, timeout=30)
        return True
    except Exception as e:
        logger.error(f"espeak error: {e}")
        return False


class TTSEngine:
    """
    Text-to-speech engine with offline-first priority.
    Priority: Piper -> espeak -> log-only fallback
    """

    def __init__(self):
        self.backend = TTS_BACKEND
        self.piper_available = _check_piper()
        logger.info(f"TTS initialized: backend={self.backend}, piper={self.piper_available}")

    def speak(self, text: str) -> bool:
        if not text or not text.strip():
            return True
        text = text.strip()
        logger.debug(f"TTS speak: {text[:80]}...")

        if self.backend == "none":
            logger.info(f"[TTS-MUTED] {text}")
            return True

        if self.backend == "piper" and self.piper_available:
            if _speak_piper(text):
                return True
            logger.warning("Piper failed, falling back to espeak")

        if _speak_espeak(text):
            return True

        logger.warning(f"All TTS backends failed. Text: {text[:100]}")
        return False

    def speak_async(self, text: str) -> None:
        import threading
        t = threading.Thread(target=self.speak, args=(text,), daemon=True)
        t.start()

    def status(self) -> dict:
        return {
            "backend": self.backend,
            "piper_available": self.piper_available,
            "piper_path": PIPER_PATH,
            "piper_model": PIPER_MODEL,
        }


# Singleton
tts_engine = TTSEngine()
