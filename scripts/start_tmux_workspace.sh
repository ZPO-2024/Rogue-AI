#!/usr/bin/env bash
# start_tmux_workspace.sh - ROGUE tmux development workspace
# Creates a named tmux session with panes for each ROGUE subsystem.
# Usage: bash scripts/start_tmux_workspace.sh

set -e

SESSION="rogue"
ROGUE_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# Kill existing session if present
tmux kill-session -t "$SESSION" 2>/dev/null || true

# Create new session, detached
tmux new-session -d -s "$SESSION" -n "main" -x 220 -y 50

# Window 0: main - ROGUE orchestrator
tmux send-keys -t "$SESSION:main" "cd $ROGUE_DIR && source .venv/bin/activate && python -m src.rogue_main" Enter

# Window 1: audio - WebSocket audio server
tmux new-window -t "$SESSION" -n "audio"
tmux send-keys -t "$SESSION:audio" "cd $ROGUE_DIR && source .venv/bin/activate && python -m src.audio_server" Enter

# Window 2: ollama - Ollama model server
tmux new-window -t "$SESSION" -n "ollama"
tmux send-keys -t "$SESSION:ollama" "ollama serve" Enter

# Window 3: logs - tail log output
tmux new-window -t "$SESSION" -n "logs"
tmux send-keys -t "$SESSION:logs" "tail -f /tmp/rogue.log 2>/dev/null || echo Waiting for logs..." Enter

# Window 4: shell - free shell in project dir
tmux new-window -t "$SESSION" -n "shell"
tmux send-keys -t "$SESSION:shell" "cd $ROGUE_DIR && source .venv/bin/activate" Enter

# Return to main window
tmux select-window -t "$SESSION:main"

# Attach to session
echo "ROGUE tmux workspace started. Session: $SESSION"
tmux attach-session -t "$SESSION"
