# Waveshare AI Smart Speaker — ROGUE Firmware

ESP32-S3 firmware for the Waveshare AI Smart Speaker board.
Streams wake-word-gated PCM audio to ROGUE audio server via WebSocket.

## Board Details

- **MCU**: ESP32-S3 (dual-core 240MHz, 8MB PSRAM)
- **Audio in**: Built-in I2S mic array (2x MEMS mics)
- **Audio out**: I2S DAC + 1W speaker amplifier
- **Connectivity**: Wi-Fi 802.11 b/g/n, BLE 5.0
- **USB**: USB-C (JTAG + UART)

## Firmware Features

- Wake word detection: "Hey ROGUE" (ESP-SR / offline)
- Continuous 16kHz 16-bit mono PCM streaming over WebSocket
- Reconnect logic with exponential backoff
- LED status indicator (idle / listening / streaming)
- Flush command on silence detection

## Build & Flash

```bash
# Install arduino-cli
curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh

# Install ESP32 core
arduino-cli core install esp32:esp32

# Install dependencies
arduino-cli lib install "WebSockets"

# Edit config before build
cp waveshare-audio-board/config.h.example waveshare-audio-board/config.h
# Edit SSID, PASSWORD, ROGUE_HOST in config.h

# Build and flash
arduino-cli compile --fqbn esp32:esp32:esp32s3 waveshare-audio-board/
arduino-cli upload -p /dev/ttyUSB0 --fqbn esp32:esp32:esp32s3 waveshare-audio-board/
```

## WebSocket Protocol

| Message | Direction | Format |
|---|---|---|
| Raw PCM audio | ESP32 -> ROGUE | Binary, 16kHz 16-bit mono |
| Flush command | ESP32 -> ROGUE | JSON `{"type":"flush"}` |
| Transcript | ROGUE -> ESP32 | JSON `{"type":"transcript","text":"..."}` |

## File Structure

```
waveshare-audio-board/
  README.md          <- This file
  waveshare-audio-board.ino  <- Main sketch (TODO)
  config.h.example   <- WiFi/host config template (TODO)
```

## Status

Firmware scaffold — protocol defined, sketch implementation in progress.
