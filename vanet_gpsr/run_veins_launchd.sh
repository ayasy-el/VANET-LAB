#!/usr/bin/env bash
# ==============================================================================
# Control Script for veins_launchd Daemon (SUMO TraCI Server Bridge)
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
PID_FILE="/tmp/vanet_launchd.pid"
LOG_FILE="/tmp/vanet_launchd.log"
PORT=9999

action="${1:-status}"

case "$action" in
    start)
        if nc -z 127.0.0.1 "${PORT}" 2>/dev/null; then
            echo "[i] veins_launchd is already listening on port ${PORT}."
        else
            echo "[+] Starting veins_launchd on port ${PORT}..."
            python3 "${ROOT_DIR}/veins/bin/veins_launchd" -p "${PORT}" -d -P "${PID_FILE}" -L "${LOG_FILE}"
            sleep 1
            echo "[✓] veins_launchd successfully started. (PID: $(cat ${PID_FILE}))"
        fi
        ;;
    stop)
        if [ -f "${PID_FILE}" ]; then
            PID=$(cat "${PID_FILE}")
            echo "[+] Stopping veins_launchd (PID: ${PID})..."
            kill "${PID}" 2>/dev/null || true
            sleep 0.5
            echo "[✓] Stopped."
        else
            echo "[i] PID file not found. Attempting termination via pkill..."
            pkill -f veins_launchd || true
            echo "[✓] Done."
        fi
        ;;
    status)
        if nc -z 127.0.0.1 "${PORT}" 2>/dev/null; then
            echo "[✓] veins_launchd is ACTIVE and listening on port ${PORT}."
            if [ -f "${PID_FILE}" ]; then
                echo "    PID : $(cat ${PID_FILE})"
            fi
            echo "    Log : ${LOG_FILE}"
        else
            echo "[x] veins_launchd is NOT active on port ${PORT}."
        fi
        ;;
    log)
        if [ -f "${LOG_FILE}" ]; then
            tail -f -n 50 "${LOG_FILE}"
        else
            echo "Log file ${LOG_FILE} does not exist yet."
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|status|log}"
        exit 1
        ;;
esac
