#!/usr/bin/env bash
# ==============================================================================
# Script to run veins/sumo-launchd.py with SUMO-GUI
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

echo "[*] Checking for sumo-gui binary..."
if ! command -v sumo-gui >/dev/null 2>&1; then
    echo "[!] ERROR: 'sumo-gui' not found in system PATH!"
    echo "    Please ensure SUMO is installed and your environment is sourced."
    exit 1
fi

SUMO_GUI_PATH=$(which sumo-gui)
echo "[✓] Found sumo-gui at: ${SUMO_GUI_PATH}"

echo "[*] Launching veins/sumo-launchd.py -vv -c sumo-gui..."
exec python3 "${SCRIPT_DIR}/veins/sumo-launchd.py" -vv -c sumo-gui "$@"
