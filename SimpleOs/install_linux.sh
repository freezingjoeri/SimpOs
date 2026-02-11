#!/usr/bin/env bash
set -e

REPO_DIR="${HOME}/SimpleOs"

echo "[SimpOs] Installing to ${REPO_DIR}..."

if [ ! -d "${REPO_DIR}" ]; then
  echo "[SimpOs] Cloning repository (assumes you already ran: git clone ... SimpleOs)"
  echo "[SimpOs] ERROR: ${REPO_DIR} not found."
  echo "Clone your GitHub repo first, e.g.:"
  echo "  git clone https://github.com/<USERNAME>/<REPO>.git \"${REPO_DIR}\""
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

START_CMD='cd "$HOME/SimpleOs" && source .venv/bin/activate && python main.py'

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

