#!/usr/bin/env bash
# ==============================================================================
# Script Menjalankan veins/sumo-launchd.py dengan mode GUI (sumo-gui)
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

echo "[*] Memeriksa keberadaan sumo-gui..."
if ! command -v sumo-gui >/dev/null 2>&1; then
    echo "[!] ERROR: 'sumo-gui' tidak ditemukan di PATH sistem!"
    echo "    Pastikan instalasi SUMO GUI sudah terpasang dan environment aktif."
    exit 1
fi

SUMO_GUI_PATH=$(which sumo-gui)
echo "[✓] sumo-gui ditemukan di: ${SUMO_GUI_PATH}"

echo "[*] Menjalankan veins/sumo-launchd.py -vv -c sumo-gui..."
exec python3 "${SCRIPT_DIR}/veins/sumo-launchd.py" -vv -c sumo-gui "$@"
