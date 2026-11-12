#!/usr/bin/env bash
# ==============================================================================
# GUI Interactive Execution Script (Qtenv)
# VANET Routing Protocol GPSR (Veins + INET + SUMO)
#
# Usage: ./run_gui.sh [CONFIG] [extra opp_run options...]
#   ./run_gui.sh GPSR_V2V_Ping
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
VANET_ROOT="${ROOT_DIR}"
export VANET_ROOT

# shellcheck source=../common_env.sh
. "${ROOT_DIR}/common_env.sh"

CONFIG="${1:-GPSR_V2V_Ping}"
if [ $# -ge 1 ]; then shift 1; fi

# Optional map selection: --map <a|b> picks the matching launchd config
# (a -> maps.launchd.xml, b -> map2.launchd.xml).
EXTRA_ARGS=()
while [ $# -gt 0 ]; do
    case "$1" in
        --map|-m)
            MAP_NAME="$2"
            shift 2
            ;;
        --map=*)
            MAP_NAME="${1#--map=}"
            shift
            ;;
        *)
            EXTRA_ARGS+=("$1")
            shift
            ;;
    esac
done

# Practicum naming: the matrix uses "a" and "b", while the launch configuration
# files keep their original names (maps.launchd.xml / map2.launchd.xml).
case "${MAP_NAME:-}" in
    a|A|map_a) MAP_NAME="maps"; MAP_LABEL="Map A" ;;
    b|B|map_b) MAP_NAME="map2"; MAP_LABEL="Map B" ;;
    maps)      MAP_LABEL="Map A" ;;
    map2)      MAP_LABEL="Map B" ;;
    "")        ;;
    *)         MAP_LABEL="${MAP_NAME}" ;;
esac

if [ -n "${MAP_NAME:-}" ]; then
    if [ ! -f "${SCRIPT_DIR}/${MAP_NAME}.launchd.xml" ]; then
        echo "ERROR: map '${MAP_NAME}' not found (no ${MAP_NAME}.launchd.xml)." >&2
        exit 1
    fi
    echo "  Map           : ${MAP_LABEL} (${MAP_NAME})"
    EXTRA_ARGS+=("--*.manager.launchConfig=xmldoc(\"${MAP_NAME}.launchd.xml\")")
fi

echo "=========================================================="
echo "  VANET GPSR SIMULATION (GUI MODE - Qtenv)"
echo "  Configuration: ${CONFIG}"
echo "  SUMO         : $(command -v sumo-gui)"
echo "=========================================================="

cd "${SCRIPT_DIR}"

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

echo "[+] Opening Qtenv user interface..."

opp_run \
    "${OPP_LIBS[@]}" \
    -n "${OPP_NED_PATH}" \
    -x "${OPP_NED_EXCLUSIONS}" \
    -u Qtenv \
    -c "${CONFIG}" \
    "${EXTRA_ARGS[@]}"
