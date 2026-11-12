#!/usr/bin/env bash
# ==============================================================================
# Script to run veins/sumo-launchd.py with SUMO-GUI
#
# The launch daemon is only a *server*: which map is simulated is decided by the
# OMNeT++ launch configuration (maps.launchd.xml / map2.launchd.xml), which the
# run scripts select with the --map flag.  This script therefore only makes sure
# that a SUMO-GUI new enough for the committed .net.xml files is used.
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VANET_ROOT="${SCRIPT_DIR}"
export VANET_ROOT

# shellcheck source=common_env.sh
. "${SCRIPT_DIR}/common_env.sh"

cd "${SCRIPT_DIR}"

echo "[*] Checking for sumo-gui binary..."
if ! command -v sumo-gui >/dev/null 2>&1; then
    echo "[!] ERROR: 'sumo-gui' not found in system PATH!"
    echo "    Please ensure SUMO is installed and your environment is sourced."
    exit 1
fi

SUMO_GUI_PATH=$(command -v sumo-gui)
echo "[✓] Found sumo-gui at: ${SUMO_GUI_PATH}"
echo "[✓] SUMO version: $(sumo-gui --version 2>/dev/null | head -1)"

echo "[*] Launching veins/sumo-launchd.py -vv -c sumo-gui..."
echo "    Tip: pick the map from the OMNeT++ side, e.g."
echo "         ./run_cmd.sh GPSR_V2V_Ping 40s --map map2"
exec python3 "${SCRIPT_DIR}/veins/sumo-launchd.py" -vv -c sumo-gui "$@"
