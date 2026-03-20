# 🤖 ROGUE — Local AI Overlay

> **Offline-first Ubuntu AI assistant** with voice, screen awareness, and hardware integration.  
> Part of the **ZeroPoint Operations / Split Reality Concepts** stack.

---

## What is ROGUE?

ROGUE is a fully offline AI assistant overlay for Ubuntu — described in the original design brief as *"Clippy done right"* — with zero cloud exposure for sensitive sessions.

It provides:
- **Always-on-top overlay UI** with keyboard-first activation
- **Voice input** via ESP32 hardware mic array → Whisper.cpp STT
- **Local LLM reasoning** via Ollama (phi3:mini, mistral, llava)
- **Voice output** via Piper TTS → ESP32 speaker
- **Screen context** via automated screenshot capture (mss/scrot)
- **PC control** via pyautogui

---

## Architecture

```
ESP32 Mic (Waveshare AI Smart Speaker)
    ↓  WiFi / WebSocket
Ubuntu AI Node
    ├── Whisper.cpp (STT)
    ├── Ollama (LLM: phi3:mini / mistral / llava)
    ├── Piper TTS
    ├── Screen Capture (mss)
    ├── PC Control (pyautogui)
    └── Overlay UI (Tkinter/PyQt6)
    ↓  Audio stream
ESP32 Speaker (Waveshare AI Smart Speaker)
```

### Cowork Pattern

```
ROGUE (local reasoning)
  → Claude Code (strategy + execution)
    → OpenHands (autonomous file-level build)
      → ECHO-API / Normandy Cockpit (orchestration, audit, control)
```

---

## Hardware

| Board | Role |
|---|---|
| **Waveshare ESP32-S3 AI Smart Speaker** | Primary voice endpoint — ES7210 dual mic array, ES8311 codec, RGB ring, display/camera headers, 16MB flash, 8MB PSRAM |
| **Lonely Binary ESP32-S3** | Sidecar / dev node — fallback control, wake-word experiments, sensor relay |

---

## Repo Structure

```
Rogue-AI/
├── src/                    # Python source — core ROGUE modules
│   ├── config.py           # Central config (env-driven)
│   ├── ollama_client.py    # Local Ollama LLM interface
│   ├── screen_capture.py   # Screenshot capture (mss)
│   ├── pc_control.py       # pyautogui keyboard/mouse control
│   ├── rogue_overlay.py    # Tkinter overlay UI
│   ├── tts.py              # Piper TTS wrapper
│   ├── audio_server.py     # WebSocket audio receiver (ESP32 stream)
│   └── rogue_main.py       # Main keyboard-first loop
├── scripts/                # Setup & run shell scripts
│   ├── setup_python.sh     # Python venv + pip install
│   ├── install_ollama.sh   # Ollama install + model pulls
│   ├── install_whisper.sh  # Whisper.cpp build from source
│   ├── install_piper.sh    # Piper TTS binary + voice download
│   ├── run_rogue.sh        # Launch ROGUE (with --healthcheck flag)
│   ├── run_audio_server.sh # Launch audio WebSocket server
│   └── start_tmux_workspace.sh  # Full tmux layout
├── esp32/                  # ESP32 hardware track
│   ├── waveshare-audio-board/   # Waveshare AI Smart Speaker firmware
│   ├── lonelybinary-s3/         # Lonely Binary ESP32-S3 firmware
│   ├── shared/                  # Shared utilities (serial probe etc.)
│   └── docs/                    # Hardware plans, flashing notes
├── lib/                    # AZ integration modules (Node.js / JS)
│   └── apocalypse-zero/    # AZ config, OSS queue, integration briefs
├── data/                   # Runtime data (queue state, briefs)
│   └── apocalypse-zero/
│       ├── repo-queue.json
│       └── briefs/
├── docs/                   # Architecture docs
│   ├── APOCALYPSE_ZERO_INTEGRATION.md
│   ├── OSS_INTEGRATION_WORKFLOW.md
│   └── HARDWARE_PLAN.md
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
└── README.md
```

---

## Quick Start

### 1. Clone & Setup Python

```bash
git clone https://github.com/ZPO-2024/Rogue-AI.git
cd Rogue-AI
bash scripts/setup_python.sh
cp .env.example .env
# Edit .env with your settings
```

### 2. Install Local AI Stack

```bash
bash scripts/install_ollama.sh      # Installs Ollama + pulls phi3:mini
bash scripts/install_whisper.sh     # Builds Whisper.cpp from source
bash scripts/install_piper.sh       # Installs Piper TTS
```

### 3. Run ROGUE

```bash
# Health check
bash scripts/run_rogue.sh --healthcheck

# Full keyboard-first mode
bash scripts/run_rogue.sh

# Full tmux workspace (recommended)
bash scripts/start_tmux_workspace.sh
```

---

## Build Status

| Component | Status |
|---|---|
| Ollama + phi3:mini | ✅ Verified working (11434) |
| Whisper.cpp base.en | ✅ Built from source |
| Python module structure | ✅ Complete |
| Piper TTS | 🔲 Binary + voice files needed |
| llava / mistral pulls | 🔲 Pending (large downloads) |
| ESP32 Waveshare firmware | 🔲 In progress |
| ESP32 Lonely Binary probe | 🔲 In progress |
| Overlay UI (Tkinter) | 🔲 Coded, off by default |
| provider-factory.js bridge | 🔲 Next phase (ECHO-API) |

---

## AZ System Context

ROGUE lives inside the **Apocalypse Zero (AZ)** secure mesh:

| Layer | Component | Role |
|---|---|---|
| Secure shell | AZ System (Tails + Tailscale + Vault) | Zero-cloud sensitive sessions |
| Local intelligence | **ROGUE** | Offline voice-first AI brain |
| Physical endpoint | ESP32 hardware | Voice I/O |
| Orchestration | ECHO-API / Normandy Cockpit | Routing, audit, approvals, telemetry |
| OSS integration | AZ OSS Workflow Queue | Queued repo research + brief generation |

---

## Related Repos

- [ZPO-2024/echo-api](https://github.com/ZPO-2024/echo-api) — ECHO-API / Normandy Cockpit (private)

---

*ZeroPoint Operations — Split Reality Concepts*
