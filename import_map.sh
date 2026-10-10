#!/usr/bin/env bash
# ==============================================================================
# import_map.sh - Automated OSM Map Import Script for VANET-AODV
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

OSM_FILE="${1:-map.osm}"
CARS="${2:-20}"

echo "[*] Running automated map import from: ${OSM_FILE}..."
exec python3 "${SCRIPT_DIR}/import_map.py" "${OSM_FILE}" --cars "${CARS}" "${@:3}"
