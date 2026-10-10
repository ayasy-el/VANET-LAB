#!/usr/bin/env bash
# ==============================================================================
# Script Eksekusi Simulasi Berbasis GUI (Qtenv)
# VANET Routing Protokol AODV di Peta Keputih (Veins + INET + SUMO)
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

if [ -d "${ROOT_DIR}/inet/src" ]; then
    INET_DIR="${ROOT_DIR}/inet"
elif [ -d "${ROOT_DIR}/../inet4.5/src" ]; then
    INET_DIR="${ROOT_DIR}/../inet4.5"
else
    echo "ERROR: Direktori INET tidak ditemukan!"
    exit 1
fi

CONFIG="${1:-AODV_V2V_Ping}"

echo "=========================================================="
echo "  VANET AODV SIMULATION (GUI MODE - Qtenv)"
echo "  Configuration: ${CONFIG}"
echo "=========================================================="

# 1. Cek / Jalankan veins_launchd jika belum aktif di port 9999
STARTED_LAUNCHD=0
if ! nc -z 127.0.0.1 9999 2>/dev/null; then
    echo "[+] Menjalankan veins_launchd daemon di port 9999..."
    python3 "${ROOT_DIR}/veins/bin/veins_launchd" -p 9999 -d -P /tmp/vanet_launchd.pid -L /tmp/vanet_launchd.log
    sleep 1
    STARTED_LAUNCHD=1
else
    echo "[i] veins_launchd sudah berjalan di port 9999."
fi

cleanup() {
    if [ "${STARTED_LAUNCHD}" -eq 1 ] && [ -f /tmp/vanet_launchd.pid ]; then
        PID=$(cat /tmp/vanet_launchd.pid 2>/dev/null || true)
        if [ -n "${PID}" ]; then
            echo "[+] Menghentikan veins_launchd (PID: ${PID})..."
            kill "${PID}" 2>/dev/null || true
            rm -f /tmp/vanet_launchd.pid
        fi
    fi
}
trap cleanup EXIT

# 2. Jalankan GUI Qtenv
echo "[+] Membuka antarmuka grafis Qtenv..."
cd "${SCRIPT_DIR}"

opp_run \
    -l "${ROOT_DIR}/veins_inet/src/veins_inet" \
    -n ".:${ROOT_DIR}/veins_inet/src/veins_inet:${ROOT_DIR}/veins/src/veins:${INET_DIR}/src" \
    -x "${INET_DIR}/.nedexclusions" \
    -u Qtenv \
    -c "${CONFIG}" \
    "$@"
