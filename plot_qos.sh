#!/usr/bin/env bash
# ==============================================================================
# plot_qos.sh - build the Praktikum 10 QoS charts from a provenance manifest
#
#   ./plot_qos.sh --map a
#   ./plot_qos.sh --map b
#   ./plot_qos.sh --all
#
#   ./plot_qos.sh --map a --run runs/map_a/aodv/<id> --run runs/map_a/gpsr/<id>
#
# Default source is the validated historical dataset described by
# qos_modul10/data/manifest.json (Praktikum 8/9).  With --run, the charts are
# built from the metadata.json files written by run_vanet.sh instead.
#
# The script only calls the existing Modul 10 pipeline
# (extract_qos.py + plot_qos_charts.py).  It never parses .sca files itself and
# never selects a file by its name alone.
#
# Charts are written to plots/<timestamp>/ (or --out <dir>).  The historical
# charts in qos_modul10/grafik and the historical CSV in qos_modul10/hasil are
# left untouched.
# ==============================================================================

set -u -o pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
QOS_DIR="${SCRIPT_DIR}/qos_modul10"
MANIFEST="${QOS_DIR}/data/manifest.json"
EXTRACT="${QOS_DIR}/scripts/extract_qos.py"
PLOT="${QOS_DIR}/scripts/plot_qos_charts.py"
PLOTS_ROOT="${SCRIPT_DIR}/plots"

usage() {
    cat <<'EOF'
Usage: ./plot_qos.sh (--map a | --map b | --all) [options]

  --map a|b|all     map to plot (required; --all is a shortcut for "all")
  --run <dir>       plot an explicit run directory written by run_vanet.sh
                    (repeat once per protocol). Default: historical dataset.
  --out <dir>       output directory (default: plots/<timestamp>)
  -h, --help        show this help

Examples:
  ./plot_qos.sh --map a
  ./plot_qos.sh --all
  ./plot_qos.sh --map b --run runs/map_b/aodv/20261120-143012-1234 \
                          --run runs/map_b/gpsr/20261120-144501-5678

Output per map: 4 charts (packet loss, average RTT, PDR, throughput).
EOF
}

die() {
    printf 'ERROR: %s\n' "$*" >&2
    exit 2
}

map_slug() {
    printf '%s' "$1" | tr '[:upper:]' '[:lower:]' | tr ' ' '_'
}

MAP_SELECTION=""
OUT_DIR=""
RUN_DIRS=()

while [ "$#" -gt 0 ]; do
    case "$1" in
        --map)
            [ "$#" -ge 2 ] || die "--map requires a value (a, b, all)"
            MAP_SELECTION="$(printf '%s' "$2" | tr '[:upper:]' '[:lower:]')"
            shift 2
            ;;
        --map=*)
            MAP_SELECTION="$(printf '%s' "${1#--map=}" | tr '[:upper:]' '[:lower:]')"
            shift
            ;;
        --all)
            MAP_SELECTION="all"
            shift
            ;;
        --run)
            [ "$#" -ge 2 ] || die "--run requires a directory"
            RUN_DIRS+=("$2")
            shift 2
            ;;
        --run=*)
            RUN_DIRS+=("${1#--run=}")
            shift
            ;;
        --out)
            [ "$#" -ge 2 ] || die "--out requires a directory"
            OUT_DIR="$2"
            shift 2
            ;;
        --out=*)
            OUT_DIR="${1#--out=}"
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            die "unknown argument '$1' (see --help)"
            ;;
    esac
done

[ -n "${MAP_SELECTION}" ] || { usage >&2; die "choose --map a, --map b, or --all"; }

case "${MAP_SELECTION}" in
    a)   MAPS=("Map A"); SOURCE_LABEL="Praktikum 8/9" ;;
    b)   MAPS=("Map B"); SOURCE_LABEL="Praktikum 8/9" ;;
    all) MAPS=("Map A" "Map B"); SOURCE_LABEL="Praktikum 8/9" ;;
    *)   die "invalid map '${MAP_SELECTION}' (use: a, b, all)" ;;
esac

[ -f "${EXTRACT}" ] || die "missing ${EXTRACT}"
[ -f "${PLOT}" ] || die "missing ${PLOT}"
command -v python3 >/dev/null 2>&1 || die "python3 is required"

if [ "${#RUN_DIRS[@]}" -eq 0 ]; then
    [ -f "${MANIFEST}" ] || die "missing historical manifest ${MANIFEST}"
    SOURCE_MANIFEST="${MANIFEST}"
else
    SOURCE_LABEL="Modul 10 run"
fi

if [ -z "${OUT_DIR}" ]; then
    OUT_DIR="${PLOTS_ROOT}/$(date +%Y%m%d-%H%M%S)"
    [ -e "${OUT_DIR}" ] && OUT_DIR="${OUT_DIR}-$$"
fi

# Never overwrite the historical deliverable charts.
OUT_REAL="$(realpath -m -- "${OUT_DIR}")"
GRAFIK_REAL="$(realpath -m -- "${QOS_DIR}/grafik")"
case "${OUT_REAL}" in
    "${GRAFIK_REAL}"|"${GRAFIK_REAL}"/*)
        die "refusing to write into ${QOS_DIR}/grafik (historical charts); use --out <dir>"
        ;;
esac

TMP="$(mktemp -d)"
trap 'rm -rf "${TMP}"' EXIT

if [ "${#RUN_DIRS[@]}" -gt 0 ]; then
    python3 - "${TMP}/manifest.json" "${MAP_SELECTION}" "${RUN_DIRS[@]}" <<'PY'
import json
import os
import sys
from datetime import date

out_path, selection, *run_dirs = sys.argv[1:]
wanted = {"a": "Map A", "b": "Map B"}.get(selection)

combinations = []
for run_dir in run_dirs:
    meta_path = os.path.join(run_dir, "metadata.json")
    if not os.path.isfile(meta_path):
        sys.exit(f"ERROR: no metadata.json in {run_dir}")
    with open(meta_path, encoding="utf-8") as fh:
        meta = json.load(fh)

    if meta.get("status") != "ok":
        sys.exit(f"ERROR: run {meta.get('run_id', run_dir)} did not finish successfully")
    if wanted and meta.get("map_label") != wanted:
        sys.exit(
            f"ERROR: {run_dir} belongs to {meta.get('map_label')}, "
            f"but --map {selection} was requested"
        )

    combo = meta.get("combination")
    if not combo or combo.get("status") != "available":
        sys.exit(f"ERROR: {run_dir}/metadata.json has no usable combination block")

    key = (combo["map"], combo["algorithm"])
    if any((c["map"], c["algorithm"]) == key for c in combinations):
        sys.exit(f"ERROR: duplicate {key[1]} run for {key[0]}")
    combinations.append(combo)

document = {
    "schema_version": 1,
    "description": "Manifest built by plot_qos.sh from run_vanet.sh metadata.",
    "verified_on": date.today().isoformat(),
    "combinations": combinations,
}
with open(out_path, "w", encoding="utf-8") as fh:
    json.dump(document, fh, indent=2)
    fh.write("\n")

for combo in combinations:
    print(f"[run]  {combo['map']:<6} {combo['algorithm']:<5} {combo['data_directory']}")
PY
    [ "$?" -eq 0 ] || exit 1
    SOURCE_MANIFEST="${TMP}/manifest.json"
fi

echo "Source : ${SOURCE_MANIFEST}"
echo "Charts : ${OUT_DIR}"
echo ""

python3 "${EXTRACT}" --manifest "${SOURCE_MANIFEST}" --output "${TMP}/qos_summary.csv" || {
    printf 'ERROR: QoS extraction failed; no chart was written.\n' >&2
    exit 1
}

echo ""
python3 "${PLOT}" \
    --csv "${TMP}/qos_summary.csv" \
    --chart-dir "${OUT_DIR}" \
    --map "${MAP_SELECTION}" \
    --source-label "${SOURCE_LABEL}" \
    --strict || {
    printf 'ERROR: chart generation failed or the dataset is incomplete.\n' >&2
    exit 1
}

# Verify that every expected file exists instead of trusting the exit code.
MISSING=()
for map_label in "${MAPS[@]}"; do
    slug="$(map_slug "${map_label}")"
    map_dir="${OUT_DIR}/${slug}"
    for metric in packet_loss avg_rtt pdr throughput; do
        file="${map_dir}/${slug}_${metric}.png"
        [ -s "${file}" ] || MISSING+=("${file}")
    done
done

if [ "${#MISSING[@]}" -gt 0 ]; then
    printf 'ERROR: expected chart(s) missing:\n' >&2
    printf '  %s\n' "${MISSING[@]}" >&2
    exit 1
fi

cp "${TMP}/qos_summary.csv" "${OUT_DIR}/qos_summary.csv"
cp "${SOURCE_MANIFEST}" "${OUT_DIR}/manifest.json"
COUNT=$((${#MAPS[@]} * 4))

echo ""
echo "=========================================================="
echo "  Created ${COUNT} chart(s) for: ${MAPS[*]}"
echo "  Directory: ${OUT_DIR}"
echo "  Table    : ${OUT_DIR}/qos_summary.csv"
echo "=========================================================="
