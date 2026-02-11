#!/usr/bin/env bash
set -e

# SimpOs install script for Linux (Ubuntu, etc.)
# Runs from the project root where main.py and requirements.txt live.

# 1) Detect project directory (where this script is located)
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${PROJECT_DIR}"

echo "[SimpOs] Installing in ${PROJECT_DIR}..."

# 2) Create virtual environment
echo "[SimpOs] Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

# 3) Install dependencies
echo "[SimpOs] Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# 4) Setup auto-start on login
PROFILE_FILE="${HOME}/.bash_profile"
if [ ! -f "${PROFILE_FILE}" ]; then
  PROFILE_FILE="${HOME}/.profile"
fi

START_CMD="cd \"${PROJECT_DIR}\" && source .venv/bin/activate && python main.py"

if ! grep -Fq "${START_CMD}" "${PROFILE_FILE}" 2>/dev/null; then
  echo "[SimpOs] Adding auto-start to ${PROFILE_FILE}..."
  {
    echo ""
    echo "# Auto-start SimpOs"
    echo "${START_CMD}"
  } >> "${PROFILE_FILE}"
else
  echo "[SimpOs] Auto-start command already present in ${PROFILE_FILE}."
fi

echo ""
echo "[SimpOs] Installation complete."
echo "Open a new terminal or re-login; SimpOs will start automatisch na inloggen."


#!/usr/bin/env bash
set -e

# Bepaal repo‑map:
# - als script in een git‑repo staat, gebruik die map
# - anders val terug op $HOME/SimpOs
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -d "${SCRIPT_DIR}/.git" ]; then
  REPO_DIR="${SCRIPT_DIR}"
else
  REPO_DIR="${HOME}/SimpOs"
fi

echo "[SimpOs] Installing in ${REPO_DIR}..."

if [ ! -d "${REPO_DIR}" ]; then
  echo "[SimpOs] ERROR: repository directory not found: ${REPO_DIR}"
  echo "[SimpOs] Run this script vanuit de repo‑map, of clone eerst met:"
  echo "  git clone https://github.com/freezingjoeri/SimpOs.git"
  echo "  cd SimpOs"
  echo "  bash install_linux.sh"
  exit 1
fi

cd "${REPO_DIR}"

echo "[SimpOs] Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

echo "[SimpOs] Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

PROFILE_FILE="${HOME}/.bash_profile"
if [ ! -f "${PROFILE_FILE}" ]; then
  PROFILE_FILE="${HOME}/.profile"
fi

START_CMD='cd "'"${REPO_DIR}"'" && source .venv/bin/activate && python main.py'

if ! grep -Fq "${START_CMD}" "${PROFILE_FILE}" 2>/dev/null; then
  echo "[SimpOs] Adding auto-start to ${PROFILE_FILE}..."
  {
    echo ""
    echo "# Auto-start SimpOs"
    echo "${START_CMD}"
  } >> "${PROFILE_FILE}"
else
  echo "[SimpOs] Auto-start command already present in ${PROFILE_FILE}."
fi

echo ""
echo "[SimpOs] Installation complete."
echo "Open a new terminal or re-login; SimpOs will start automatisch na inloggen."

