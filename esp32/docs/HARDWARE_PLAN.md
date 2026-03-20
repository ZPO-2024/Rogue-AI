# ROGUE ESP32 Hardware Plan

Voice hardware integration for the ROGUE Local AI Overlay.
Two board tracks: Waveshare AI Smart Speaker (production) and Lonely Binary S3 (dev/prototype).

---

## Hardware Tracks

### Track A: Waveshare AI Smart Speaker (Production)

- **Board**: Waveshare ESP32-S3-BOX-3 / Waveshare AI Smart Speaker
- **Chip**: ESP32-S3 dual-core 240MHz
- **Audio**: Built-in I2S mic array + speaker output
- **Connectivity**: Wi-Fi + BLE
- **Role**: Always-on wake word detection -> PCM audio stream -> ROGUE audio_server (WebSocket)
- **Wake word**: "Hey ROGUE" via ESP-SR or Porcupine offline model
- **Audio format**: 16kHz mono 16-bit PCM, chunked over WebSocket
- **Target firmware**: `esp32/waveshare-audio-board/`

### Track B: Lonely Binary S3 (Dev/Prototype)

- **Board**: Lonely Binary ESP32-S3 dev board
- **Chip**: ESP32-S3
- **Audio**: External I2S MEMS mic (INMP441 or SPH0645)
- **Role**: Same as Track A — dev target for firmware iteration before flashing Waveshare
- **Target firmware**: `esp32/lonelybinary-s3/`

---

## System Architecture

```
[ESP32 mic] --PCM--> [WebSocket ws://rogue-host:8765] --transcript--> [ROGUE audio_server.py]
                                                                              |
                                                                   [Whisper STT transcription]
                                                                              |
                                                              [rogue_main.py orchestrator]
                                                                              |
                                                              [Ollama LLM inference]
                                                                              |
                                                              [Piper TTS response]
                                                                              |
                                                       [WebSocket text reply to ESP32 speaker]
```

---

## Firmware Requirements

- Arduino-CLI or ESP-IDF build toolchain
- Board package: `esp32:esp32` (Espressif Arduino core)
- Libraries: `WiFi.h`, `WebSocketsClient.h` (Links2004/arduinoWebSockets)
- Whisper model on host: `ggml-base.en.bin` (~140MB)
- ROGUE host accessible on local network (static IP or mDNS)

## Connection Config

```cpp
// Set in firmware before flash
const char* SSID = "YOUR_WIFI_SSID";
const char* PASSWORD = "YOUR_WIFI_PASS";
const char* ROGUE_HOST = "192.168.1.X"; // ROGUE Ubuntu host IP
const int ROGUE_PORT = 8765;
```

---

## Build Status

| Component | Status |
|---|---|
| Waveshare firmware | In progress |
| Lonely Binary firmware | In progress |
| Serial probe sketch | Ready |
| WebSocket audio protocol | Defined |
| Wake word integration | Planned (ESP-SR) |
