#!/usr/bin/env bash
# ==============================================================================
# GUI Interactive Execution Script (Qtenv)
# VANET Routing Protocol GPSR (Veins + INET + SUMO)
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Auto-source OMNeT++ environment if opp_run is not in PATH
if ! command -v opp_run &> /dev/null; then
    if [ -f "${ROOT_DIR}/../omnetpp-6.4.0/setenv" ]; then
        source "${ROOT_DIR}/../omnetpp-6.4.0/setenv"
    fi
fi

if [ -d "${ROOT_DIR}/inet/src" ]; then
    INET_DIR="${ROOT_DIR}/inet"
elif [ -d "${ROOT_DIR}/../inet4.5/src" ]; then
    INET_DIR="${ROOT_DIR}/../inet4.5"
else
    echo "ERROR: INET directory not found!"
    exit 1
fi

CONFIG="${1:-GPSR_V2V_Ping}"

echo "=========================================================="
echo "  VANET GPSR SIMULATION (GUI MODE - Qtenv)"
echo "  Configuration: ${CONFIG}"
echo "=========================================================="

# 1. Check / start veins_launchd if not running on port 9999
STARTED_LAUNCHD=0
if ! nc -z 127.0.0.1 9999 2>/dev/null; then
    echo "[+] Starting veins_launchd daemon on port 9999..."
    python3 "${ROOT_DIR}/veins/bin/veins_launchd" -p 9999 -d -P /tmp/vanet_launchd.pid -L /tmp/vanet_launchd.log
    sleep 1
    STARTED_LAUNCHD=1
else
    echo "[i] veins_launchd is already listening on port 9999."
fi

cleanup() {
    if [ "${STARTED_LAUNCHD}" -eq 1 ] && [ -f /tmp/vanet_launchd.pid ]; then
        PID=$(cat /tmp/vanet_launchd.pid 2>/dev/null || true)
        if [ -n "${PID}" ]; then
            echo "[+] Stopping veins_launchd (PID: ${PID})..."
            kill "${PID}" 2>/dev/null || true
            rm -f /tmp/vanet_launchd.pid
        fi
    fi
}
trap cleanup EXIT

# 2. Launch Qtenv GUI
echo "[+] Opening Qtenv user interface..."
cd "${SCRIPT_DIR}"

opp_run \
    -l "${ROOT_DIR}/veins_inet/src/veins_inet" \
    -n ".:${ROOT_DIR}/veins_inet/src/veins_inet:${ROOT_DIR}/veins/src/veins:${INET_DIR}/src" \
    -x "${INET_DIR}/.nedexclusions" \
    -u Qtenv \
    -c "${CONFIG}" \
    "$@"
