#!/usr/bin/env bash
# Start the ADK agents locally.
#
# Usage:
#   ./run_local.sh                       # ADK dev web UI (all agents) on port 8000
#   PORT=8080 ./run_local.sh             # web UI on a different port
#   ./run_local.sh run workflow_agents   # interactive CLI for one agent (in agents/)
#   ./run_local.sh <any adk args>        # passed straight to `adk`
set -euo pipefail

cd "$(dirname "$0")"

VENV=".venv"
PYTHON="${PYTHON:-python3}"

if [[ ! -d "$VENV" ]]; then
  echo "Creating virtual environment in $VENV..."
  "$PYTHON" -m venv "$VENV"
fi

# shellcheck disable=SC1091
source "$VENV/bin/activate"

# Reinstall dependencies only when requirements.txt changes.
STAMP="$VENV/.requirements.sha"
REQ_SHA="$(shasum requirements.txt | awk '{print $1}')"
if [[ ! -f "$STAMP" || "$(cat "$STAMP")" != "$REQ_SHA" ]]; then
  echo "Installing dependencies..."
  pip install --quiet --upgrade pip
  pip install --quiet -r requirements.txt
  echo "$REQ_SHA" > "$STAMP"
fi

if [[ ! -f .env ]]; then
  echo "Error: .env not found. Run: cp .env.example .env  and fill in the values." >&2
  exit 1
fi

if ! grep -Eq '^[[:space:]]*(export[[:space:]]+)?MODEL=' .env; then
  echo "Error: MODEL is not set in .env." >&2
  exit 1
fi

# Catch placeholders copied from .env.example that were never filled in.
PLACEHOLDERS="$(grep -En '^[[:space:]]*[^#].*=your-' .env || true)"
if [[ -n "$PLACEHOLDERS" ]]; then
  echo "Error: .env still has placeholder values:" >&2
  echo "$PLACEHOLDERS" >&2
  exit 1
fi

AGENTS_DIR="agents"

if [[ $# -eq 0 ]]; then
  exec adk web --port "${PORT:-8000}" "$AGENTS_DIR"
elif [[ "$1" == "run" && $# -ge 2 && -d "$AGENTS_DIR/$2" ]]; then
  # Allow the short form: ./run_local.sh run workflow_agents
  agent="$2"
  shift 2
  exec adk run "$@" "$AGENTS_DIR/$agent"
else
  exec adk "$@"
fi
