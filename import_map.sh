#!/usr/bin/env bash
# ==============================================================================
# import_map.sh - Script Otomasi Import Peta .osm ke Simulasi VANET-AODV
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

OSM_FILE="${1:-map.osm}"
CARS="${2:-20}"

echo "[*] Menjalankan konversi peta dari: ${OSM_FILE}..."
exec python3 "${SCRIPT_DIR}/import_map.py" "${OSM_FILE}" --cars "${CARS}" "${@:3}"
