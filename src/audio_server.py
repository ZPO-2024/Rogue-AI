"""
audio_server.py - ROGUE WebSocket Audio Server
Receives audio from ESP32 hardware, runs Whisper STT transcription.
Part of the ROGUE Local AI Overlay stack.
"""

import asyncio
import json
import logging
import os
import subprocess
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

AUDIO_WS_PORT = int(os.getenv("ROGUE_AUDIO_PORT", "8765"))
WHISPER_PATH = os.getenv("WHISPER_PATH", "/usr/local/bin/whisper-cpp")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", str(Path.home() / ".local/share/whisper/models/ggml-base.en.bin"))
SAMPLE_RATE = 16000

try:
    import websockets
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False
    logger.warning("websockets not available - audio server disabled")


async def transcribe_audio(audio_bytes: bytes) -> str:
    """Run Whisper STT on raw PCM audio bytes."""
    if not audio_bytes:
        return ""
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            _write_wav(tmp, audio_bytes)
            tmp_path = tmp.name

        result = subprocess.run(
            [WHISPER_PATH, "-m", WHISPER_MODEL, "-f", tmp_path, "--output-txt", "--no-timestamps"],
            capture_output=True,
            timeout=30,
        )
        Path(tmp_path).unlink(missing_ok=True)

        if result.returncode != 0:
            logger.error(f"Whisper error: {result.stderr.decode()}")
            return ""

        text = result.stdout.decode().strip()
        logger.info(f"Transcribed: {text[:100]}")
        return text

    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return ""


def _write_wav(f, pcm_bytes: bytes) -> None:
    """Write minimal WAV header + PCM data."""
    import struct
    num_channels = 1
    bits_per_sample = 16
    byte_rate = SAMPLE_RATE * num_channels * bits_per_sample // 8
    block_align = num_channels * bits_per_sample // 8
    data_size = len(pcm_bytes)
    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF", 36 + data_size, b"WAVE",
        b"fmt ", 16, 1, num_channels,
        SAMPLE_RATE, byte_rate, block_align, bits_per_sample,
        b"data", data_size,
    )
    f.write(header)
    f.write(pcm_bytes)


async def handle_client(websocket):
    """Handle incoming WebSocket connection from ESP32."""
    client_addr = websocket.remote_address
    logger.info(f"ESP32 connected: {client_addr}")
    audio_buffer = bytearray()

    try:
        async for message in websocket:
            if isinstance(message, bytes):
                audio_buffer.extend(message)
                # Process when buffer reaches ~2 seconds of audio
                if len(audio_buffer) >= SAMPLE_RATE * 2 * 2:
                    transcript = await transcribe_audio(bytes(audio_buffer))
                    audio_buffer.clear()
                    if transcript:
                        response = json.dumps({"type": "transcript", "text": transcript})
                        await websocket.send(response)
            elif isinstance(message, str):
                try:
                    cmd = json.loads(message)
                    if cmd.get("type") == "flush":
                        if audio_buffer:
                            transcript = await transcribe_audio(bytes(audio_buffer))
                            audio_buffer.clear()
                            if transcript:
                                await websocket.send(json.dumps({"type": "transcript", "text": transcript}))
                except json.JSONDecodeError:
                    pass
    except Exception as e:
        logger.info(f"ESP32 disconnected: {client_addr} ({e})")


async def run_server():
    if not HAS_WEBSOCKETS:
        logger.error("Cannot start audio server: websockets package not installed")
        return
    logger.info(f"ROGUE Audio Server starting on ws://0.0.0.0:{AUDIO_WS_PORT}")
    async with websockets.serve(handle_client, "0.0.0.0", AUDIO_WS_PORT):
        await asyncio.Future()  # Run forever


def start():
    asyncio.run(run_server())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    start()
