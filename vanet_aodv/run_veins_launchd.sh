#!/usr/bin/env bash
# ==============================================================================
# Script Kontrol Daemon veins_launchd (TraCI Server Bridge untuk SUMO)
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
            echo "[i] veins_launchd sudah aktif di port ${PORT}."
        else
            echo "[+] Memulai veins_launchd di port ${PORT}..."
            python3 "${ROOT_DIR}/veins/bin/veins_launchd" -p "${PORT}" -d -P "${PID_FILE}" -L "${LOG_FILE}"
            sleep 1
            echo "[✓] veins_launchd berhasil dijalankan. (PID: $(cat ${PID_FILE}))"
        fi
        ;;
    stop)
        if [ -f "${PID_FILE}" ]; then
            PID=$(cat "${PID_FILE}")
            echo "[+] Menghentikan veins_launchd (PID: ${PID})..."
            kill "${PID}" 2>/dev/null || true
            sleep 0.5
            echo "[✓] Berhenti."
        else
            echo "[i] File PID tidak ditemukan. Mencoba menghentikan via pkill..."
            pkill -f veins_launchd || true
            echo "[✓] Selesai."
        fi
        ;;
    status)
        if nc -z 127.0.0.1 "${PORT}" 2>/dev/null; then
            echo "[✓] veins_launchd AKTIF dan mendengarkan koneksi di port ${PORT}."
            if [ -f "${PID_FILE}" ]; then
                echo "    PID : $(cat ${PID_FILE})"
            fi
            echo "    Log : ${LOG_FILE}"
        else
            echo "[x] veins_launchd TIDAK aktif di port ${PORT}."
        fi
        ;;
    log)
        if [ -f "${LOG_FILE}" ]; then
            tail -f -n 50 "${LOG_FILE}"
        else
            echo "File log ${LOG_FILE} belum ada."
        fi
        ;;
    *)
        echo "Penggunaan: $0 {start|stop|status|log}"
        exit 1
        ;;
esac
