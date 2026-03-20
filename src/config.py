"""
ROGUE — Central Configuration
Loads all settings from environment variables with sane defaults.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(Path(__file__).parent.parent / ".env")


class Config:
    # ── Ollama ────────────────────────────────────────────────────────────────
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
    OLLAMA_DEFAULT_MODEL: str = os.getenv("OLLAMA_DEFAULT_MODEL", "phi3:mini")
    OLLAMA_VISION_MODEL: str = os.getenv("OLLAMA_VISION_MODEL", "llava")
    OLLAMA_CHAT_MODEL: str = os.getenv("OLLAMA_CHAT_MODEL", "mistral")
    OLLAMA_TIMEOUT: int = int(os.getenv("OLLAMA_TIMEOUT", "60"))

    # ── Whisper ───────────────────────────────────────────────────────────────
    WHISPER_BIN: str = os.path.expanduser(
        os.getenv("WHISPER_BIN", "~/whisper.cpp/main")
    )
    WHISPER_MODEL: str = os.path.expanduser(
        os.getenv("WHISPER_MODEL", "~/whisper.cpp/models/ggml-base.en.bin")
    )
    WHISPER_LANGUAGE: str = os.getenv("WHISPER_LANGUAGE", "en")

    # ── Piper TTS ─────────────────────────────────────────────────────────────
    PIPER_BIN: str = os.path.expanduser(
        os.getenv("PIPER_BIN", "~/piper/piper")
    )
    PIPER_VOICE: str = os.path.expanduser(
        os.getenv("PIPER_VOICE", "~/piper/voices/en_US-lessac-medium.onnx")
    )

    # ── Overlay UI ────────────────────────────────────────────────────────────
    OVERLAY_HOTKEY: str = os.getenv("OVERLAY_HOTKEY", "ctrl+space")
    OVERLAY_OPACITY: float = float(os.getenv("OVERLAY_OPACITY", "0.92"))
    OVERLAY_ALWAYS_ON_TOP: bool = os.getenv("OVERLAY_ALWAYS_ON_TOP", "true").lower() == "true"
    OVERLAY_ENABLE: bool = os.getenv("OVERLAY_ENABLE", "false").lower() == "true"

    # ── Screen Capture ────────────────────────────────────────────────────────
    SCREEN_CAPTURE_ENABLE: bool = os.getenv("SCREEN_CAPTURE_ENABLE", "true").lower() == "true"
    SCREEN_CAPTURE_MONITOR: int = int(os.getenv("SCREEN_CAPTURE_MONITOR", "1"))

    # ── Audio Server ──────────────────────────────────────────────────────────
    AUDIO_SERVER_HOST: str = os.getenv("AUDIO_SERVER_HOST", "0.0.0.0")
    AUDIO_SERVER_PORT: int = int(os.getenv("AUDIO_SERVER_PORT", "8765"))
    AUDIO_SAMPLE_RATE: int = int(os.getenv("AUDIO_SAMPLE_RATE", "16000"))
    AUDIO_CHANNELS: int = int(os.getenv("AUDIO_CHANNELS", "1"))

    # ── Network ───────────────────────────────────────────────────────────────
    UBUNTU_TAILSCALE_IP: str = os.getenv("UBUNTU_TAILSCALE_IP", "100.x.x.x")
    UBUNTU_LOCAL_IP: str = os.getenv("UBUNTU_LOCAL_IP", "192.168.x.x")

    # ── AZ System ─────────────────────────────────────────────────────────────
    AZ_MODE: str = os.getenv("AZ_MODE", "local")
    AZ_TENANT_ID: str = os.getenv("AZ_TENANT_ID", "zpo")
    AZ_SECURE_SESSION: bool = os.getenv("AZ_SECURE_SESSION", "false").lower() == "true"

    # ── Logging ───────────────────────────────────────────────────────────────
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR: Path = Path(os.getenv("LOG_DIR", "./logs"))


# Singleton
config = Config()
