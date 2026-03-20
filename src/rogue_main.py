"""
rogue_main.py - ROGUE Main Orchestrator
Entry point for the ROGUE Local AI Overlay.
Wires together: Ollama LLM, Whisper STT, Piper TTS, Screen Capture, PC Control, Overlay UI.
Part of the ROGUE Local AI Overlay stack.
"""

import asyncio
import logging
import os
import signal
import sys
from pathlib import Path

from .config import config
from .ollama_client import ollama_client
from .screen_capture import screen_capture
from .tts import tts_engine
from .rogue_overlay import overlay

logger = logging.getLogger(__name__)

ROGUE_VERSION = "0.1.0"


class RogueOrchestrator:
    """
    Main ROGUE orchestrator.
    Manages the main event loop, coordinates all subsystems,
    and handles graceful shutdown.
    """

    def __init__(self):
        self.running = False
        self._audio_server_task = None
        self._setup_logging()

    def _setup_logging(self) -> None:
        log_level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
            datefmt="%H:%M:%S",
        )

    def _setup_signals(self) -> None:
        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, self._handle_shutdown)

    def _handle_shutdown(self, signum, frame) -> None:
        logger.info(f"Shutdown signal received ({signum})")
        self.running = False
        overlay.offline()

    async def _run_audio_server(self) -> None:
        """Start the WebSocket audio server in background."""
        try:
            from .audio_server import run_server
            await run_server()
        except Exception as e:
            logger.error(f"Audio server error: {e}")

    async def _process_voice_input(self, transcript: str) -> None:
        """Handle a voice transcript - run through Ollama and speak response."""
        if not transcript.strip():
            return

        logger.info(f"Voice input: {transcript}")
        overlay.thinking(model=config.OLLAMA_MODEL)

        # Capture screen context if enabled
        context_image = None
        if config.SCREEN_CAPTURE_ENABLED:
            context_image = screen_capture.capture()

        # Build system prompt
        system_prompt = [
            "You are ROGUE, an offline-first AI assistant overlay running on Ubuntu.",
            "You are embedded in the ZeroPoint Operations / Split Reality Concepts stack.",
            "Be concise. Prefer direct answers. You have screen awareness when images are provided.",
            "You operate in AZ_MODE: " + config.AZ_MODE,
        ]

        messages = [
            {"role": "system", "content": " ".join(system_prompt)},
            {"role": "user", "content": transcript},
        ]

        # Stream response
        response_parts = []
        async for chunk in ollama_client.stream_chat(messages):
            response_parts.append(chunk)

        response = "".join(response_parts).strip()
        logger.info(f"ROGUE response: {response[:120]}")

        overlay.active(model=config.OLLAMA_MODEL)
        tts_engine.speak_async(response)

    async def run(self) -> None:
        self.running = True
        self._setup_signals()

        logger.info(f"ROGUE v{ROGUE_VERSION} starting...")
        logger.info(f"Model: {config.OLLAMA_MODEL} | AZ_MODE: {config.AZ_MODE}")

        overlay.init()
        overlay.thinking(model=config.OLLAMA_MODEL, message="Checking Ollama connection...")

        # Verify Ollama is running
        if not await ollama_client.health_check():
            logger.error("Ollama not reachable. Start Ollama and retry.")
            overlay.error("Ollama not reachable")
            tts_engine.speak("ROGUE startup failed. Ollama is not running.")
            return

        overlay.active(model=config.OLLAMA_MODEL, message="ROGUE online")
        tts_engine.speak("ROGUE online.")
        logger.info("ROGUE ready.")

        # Start audio server if enabled
        if config.AUDIO_SERVER_ENABLED:
            self._audio_server_task = asyncio.create_task(self._run_audio_server())
            logger.info(f"Audio server started on port {config.AUDIO_PORT}")

        # Main loop — in production this would listen to the WebSocket transcript feed
        try:
            while self.running:
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            pass

        logger.info("ROGUE shutting down...")
        overlay.offline()
        tts_engine.speak("ROGUE offline.")


def main():
    orchestrator = RogueOrchestrator()
    try:
        asyncio.run(orchestrator.run())
    except KeyboardInterrupt:
        pass
    sys.exit(0)


if __name__ == "__main__":
    main()
