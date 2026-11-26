#!/usr/bin/env bash
# ==============================================================================
# run_vanet.sh - single entry point for the VANET practicum simulations
#
#   ./run_vanet.sh <algorithm> <map> <test> <duration>
#
#     algorithm : aodv | gpsr
#     map       : a | b
#     test      : ping | udp | both
#     duration  : simulation time limit, e.g. 40s (a bare number means seconds)
#
# Examples:
#   ./run_vanet.sh aodv a ping 40s
#   ./run_vanet.sh gpsr b both 60s
#
# The script only orchestrates the existing vanet_<algorithm>/run_cmd.sh.  It
# never re-implements the simulation.  Every invocation writes into its own
# directory
#
#   runs/map_<map>/<algorithm>/<run_id>/
#
# and passes --result-dir to opp_run, so the historical Praktikum 8/9/10
# results in vanet_*/results are never overwritten.
# ==============================================================================

set -u -o pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
RUNS_ROOT="${SCRIPT_DIR}/runs"

usage() {
    cat <<'EOF'
Usage: ./run_vanet.sh <algorithm> <map> <test> <duration>

  algorithm   aodv | gpsr
  map         a | b
  test        ping | udp | both   ("both" runs Ping first, then UDP)
  duration    simulation limit, e.g. 40s or 60s (bare number = seconds)

Examples:
  ./run_vanet.sh aodv a ping 40s
  ./run_vanet.sh gpsr b both 60s

Output:
  runs/map_<map>/<algorithm>/<run_id>/   .sca/.vec/.vci + metadata.json

Notes:
  - The simulation itself is executed by vanet_<algorithm>/run_cmd.sh.
  - Existing results under vanet_*/results are never modified.
  - Runs are serialised with flock because veins_launchd uses port 9999.
EOF
}

die() {
    printf 'ERROR: %s\n' "$*" >&2
    exit 2
}

if [ "$#" -eq 1 ] && { [ "$1" = "-h" ] || [ "$1" = "--help" ]; }; then
    usage
    exit 0
fi

if [ "$#" -ne 4 ]; then
    printf 'ERROR: expected 4 arguments, got %d.\n\n' "$#" >&2
    usage >&2
    exit 2
fi

ALGO_RAW="$1"
MAP_RAW="$2"
TEST_RAW="$3"
DURATION_RAW="$4"

ALGO="$(printf '%s' "${ALGO_RAW}" | tr '[:upper:]' '[:lower:]')"
MAP_ARG="$(printf '%s' "${MAP_RAW}" | tr '[:upper:]' '[:lower:]')"
TEST="$(printf '%s' "${TEST_RAW}" | tr '[:upper:]' '[:lower:]')"

case "${ALGO}" in
    aodv) ALGO_LABEL="AODV"; WORKSPACE="${SCRIPT_DIR}/vanet_aodv" ;;
    gpsr) ALGO_LABEL="GPSR"; WORKSPACE="${SCRIPT_DIR}/vanet_gpsr" ;;
    *) die "unknown algorithm '${ALGO_RAW}' (use: aodv, gpsr)" ;;
esac

case "${MAP_ARG}" in
    a|map_a|maps) MAP_KEY="a"; MAP_LABEL="Map A"; LAUNCH_CONFIG="maps.launchd.xml" ;;
    b|map_b|map2) MAP_KEY="b"; MAP_LABEL="Map B"; LAUNCH_CONFIG="map2.launchd.xml" ;;
    *) die "unknown map '${MAP_RAW}' (use: a, b)" ;;
esac

case "${TEST}" in
    ping|udp|both) ;;
    *) die "unknown test '${TEST_RAW}' (use: ping, udp, both)" ;;
esac

DURATION="$(printf '%s' "${DURATION_RAW}" | tr '[:upper:]' '[:lower:]')"
if ! [[ "${DURATION}" =~ ^[0-9]+([.][0-9]+)?(ms|s)?$ ]]; then
    die "invalid duration '${DURATION_RAW}' (examples: 40s, 60s, 30)"
fi
case "${DURATION}" in
    *s) ;;
    *)  DURATION="${DURATION}s" ;;
esac
if [[ "${DURATION}" =~ ^0+([.]0+)?(ms|s)$ ]]; then
    die "duration must be greater than zero"
fi

[ -x "${WORKSPACE}/run_cmd.sh" ] || die "missing executable ${WORKSPACE}/run_cmd.sh"
[ -f "${WORKSPACE}/${LAUNCH_CONFIG}" ] || die "missing map config ${WORKSPACE}/${LAUNCH_CONFIG}"
command -v python3 >/dev/null 2>&1 || die "python3 is required to write metadata.json"
command -v flock >/dev/null 2>&1 || die "flock is required to serialise simulation runs"

mkdir -p "${RUNS_ROOT}" || die "cannot create ${RUNS_ROOT}"

RUN_ID="$(date +%Y%m%d-%H%M%S)-$$"
RUN_DIR="${RUNS_ROOT}/map_${MAP_KEY}/${ALGO}/${RUN_ID}"
mkdir -p "${RUN_DIR}" || die "cannot create ${RUN_DIR}"

# One simulation at a time: veins_launchd listens on a single port.
exec 9>"${RUNS_ROOT}/.lock"
flock -w 1800 9 || die "another run has held the simulation lock for more than 30 minutes"

if [ "${TEST}" = "both" ]; then
    TESTS=(ping udp)
else
    TESTS=("${TEST}")
fi

RECORDS="${RUN_DIR}/.tests.tsv"
: > "${RECORDS}"
MARKER="${RUN_DIR}/.start_marker"
: > "${MARKER}"

METADATA_WRITTEN=0
OVERALL=0

finalize_metadata() {
    [ "${METADATA_WRITTEN}" -eq 1 ] && return 0
    [ -f "${RECORDS}" ] || return 0

    VANET_RUN_ID="${RUN_ID}" \
    VANET_RUN_DIR="${RUN_DIR}" \
    VANET_ALGO="${ALGO}" \
    VANET_ALGO_LABEL="${ALGO_LABEL}" \
    VANET_MAP_KEY="${MAP_KEY}" \
    VANET_MAP_LABEL="${MAP_LABEL}" \
    VANET_LAUNCH_CONFIG="${LAUNCH_CONFIG}" \
    VANET_TEST="${TEST}" \
    VANET_DURATION="${DURATION}" \
    VANET_WORKSPACE="${WORKSPACE}" \
    VANET_EXPECTED_TESTS="${#TESTS[@]}" \
    VANET_OVERALL="${OVERALL}" \
    python3 - "${RECORDS}" "${RUN_DIR}/metadata.json" <<'PY'
import json
import os
import sys
from datetime import datetime, timezone

records_path, out_path = sys.argv[1], sys.argv[2]
env = os.environ

tests = []
with open(records_path, encoding="utf-8") as fh:
    for raw in fh:
        raw = raw.rstrip("\n")
        if not raw:
            continue
        (name, config, status, exit_code, started, finished,
         sca, digest, seedset, nodes, run_id) = raw.split("\t")
        tests.append(
            {
                "test": name,
                "config": config,
                "status": status,
                "exit_code": int(exit_code),
                "started_at": started,
                "finished_at": finished,
                "sca_file": sca or None,
                "sca_path": os.path.join(env["VANET_RUN_DIR"], sca) if sca else None,
                "sha256": digest or None,
                "seedset": int(seedset) if seedset.isdigit() else None,
                "node_count": int(nodes) if nodes.isdigit() else None,
                "sca_run_id": run_id or None,
            }
        )

expected = int(env["VANET_EXPECTED_TESTS"])
all_ok = len(tests) == expected and all(t["status"] == "ok" for t in tests)
run_ok = all_ok and env.get("VANET_OVERALL") == "0"

first = next((t for t in tests if t["status"] == "ok"), None)
seedset = first["seedset"] if first else None
node_count = first["node_count"] if first else None

combination = {
    "id": f"map_{env['VANET_MAP_KEY']}_{env['VANET_ALGO']}",
    "map": env["VANET_MAP_LABEL"],
    "algorithm": env["VANET_ALGO_LABEL"],
    "status": "available" if all_ok else "missing",
    "workspace": os.path.basename(env["VANET_WORKSPACE"]),
    "launch_config": env["VANET_LAUNCH_CONFIG"],
    "seedset": seedset,
    "sim_time_limit": env["VANET_DURATION"],
    "node_count": node_count,
    "source_directory": env["VANET_RUN_DIR"],
    "data_directory": env["VANET_RUN_DIR"],
    "provenance_note": f"Generated by run_vanet.sh; run_id {env['VANET_RUN_ID']}.",
    "runs": [
        {
            "scenario": t["test"],
            "config": t["config"],
            "file": t["sca_file"],
            "source_path": t["sca_path"],
            "run_id": t["sca_run_id"],
            "sha256": t["sha256"],
        }
        for t in tests
        if t["status"] == "ok" and t["sca_file"]
    ],
}

document = {
    "schema_version": 1,
    "run_id": env["VANET_RUN_ID"],
    "created_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
    "algorithm": env["VANET_ALGO"],
    "algorithm_label": env["VANET_ALGO_LABEL"],
    "map": env["VANET_MAP_KEY"],
    "map_label": env["VANET_MAP_LABEL"],
    "launch_config": env["VANET_LAUNCH_CONFIG"],
    "test": env["VANET_TEST"],
    "duration": env["VANET_DURATION"],
    "seedset": seedset,
    "seed_source": "read from the .sca metadata after the run (opp_run -r 0)",
    "status": "ok" if run_ok else "failed",
    "result_dir": env["VANET_RUN_DIR"],
    "command": [
        "./run_vanet.sh",
        env["VANET_ALGO"],
        env["VANET_MAP_KEY"],
        env["VANET_TEST"],
        env["VANET_DURATION"],
    ],
    "tests": tests,
    "combination": combination,
}

with open(out_path, "w", encoding="utf-8") as fh:
    json.dump(document, fh, indent=2)
    fh.write("\n")
PY

    METADATA_WRITTEN=1
    rm -f "${RECORDS}" "${MARKER}"
}

on_exit() {
    finalize_metadata || true
}
trap on_exit EXIT

for current_test in "${TESTS[@]}"; do
    case "${current_test}" in
        ping) CONFIG="${ALGO_LABEL}_V2V_Ping" ;;
        udp)  CONFIG="${ALGO_LABEL}_V2V_UDP" ;;
    esac

    echo "=========================================================="
    echo "  ${ALGO_LABEL} | ${MAP_LABEL} | ${current_test}"
    echo "  Config    : ${CONFIG}"
    echo "  Duration  : ${DURATION}"
    echo "  Result dir: ${RUN_DIR}"
    echo "=========================================================="

    STARTED="$(date -Iseconds)"
    "${WORKSPACE}/run_cmd.sh" "${CONFIG}" "${DURATION}" \
        --map "${MAP_KEY}" --result-dir="${RUN_DIR}" 2>&1 | tee -a "${RUN_DIR}/run.log"
    RC=${PIPESTATUS[0]}
    FINISHED="$(date -Iseconds)"

    STATUS="ok"
    if [ "${RC}" -ne 0 ]; then
        STATUS="failed"
        OVERALL=1
        printf 'ERROR: %s exited with code %d\n' "${CONFIG}" "${RC}" >&2
    fi

    SCA_NAME=""
    SCA_SHA=""
    SCA_SEED=""
    SCA_NODES=""
    SCA_RUN_ID=""

    shopt -s nullglob
    CANDIDATES=("${RUN_DIR}/${CONFIG}"-*.sca)
    shopt -u nullglob

    if [ "${#CANDIDATES[@]}" -eq 0 ]; then
        if [ "${STATUS}" = "ok" ]; then
            STATUS="failed"
            OVERALL=1
            printf 'ERROR: no %s-*.sca was produced in %s\n' "${CONFIG}" "${RUN_DIR}" >&2
        fi
    elif [ "${#CANDIDATES[@]}" -gt 1 ]; then
        STATUS="failed"
        OVERALL=1
        printf 'ERROR: more than one .sca matched %s-*.sca in %s\n' "${CONFIG}" "${RUN_DIR}" >&2
    else
        SCA="${CANDIDATES[0]}"
        SCA_NAME="$(basename -- "${SCA}")"
        SCA_SHA="$(sha256sum -- "${SCA}" | cut -d' ' -f1)"
        SCA_SEED="$(awk '$1 == "attr" && $2 == "seedset" { print $3; exit }' "${SCA}")"
        SCA_NODES="$(awk -F'[][]' '
            BEGIN { max = -1 }
            /^par Scenario\.node\[/ {
                idx = $2 + 0
                if (idx > max) max = idx
            }
            END { print (max < 0 ? 0 : max + 1) }
        ' "${SCA}")"
        SCA_RUN_ID="$(awk '$1 == "run" { print $2; exit }' "${SCA}")"
    fi

    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
        "${current_test}" "${CONFIG}" "${STATUS}" "${RC}" \
        "${STARTED}" "${FINISHED}" "${SCA_NAME}" "${SCA_SHA}" \
        "${SCA_SEED}" "${SCA_NODES}" "${SCA_RUN_ID}" >> "${RECORDS}"

    if [ "${STATUS}" = "ok" ]; then
        echo "[ok]   ${SCA_NAME} | seedset ${SCA_SEED:-?} | nodes ${SCA_NODES:-?}"
    else
        echo "[fail] ${CONFIG}"
    fi
    echo ""
done

# Guard: a new run must not touch the historical result directories.
if [ -d "${WORKSPACE}/results" ]; then
    TOUCHED="$(find "${WORKSPACE}/results" -type f -newer "${MARKER}" -print -quit)"
    if [ -n "${TOUCHED}" ]; then
        OVERALL=1
        printf 'ERROR: historical results were modified: %s\n' "${TOUCHED}" >&2
    fi
fi

finalize_metadata
if [ ! -f "${RUN_DIR}/metadata.json" ]; then
    OVERALL=1
    printf 'ERROR: metadata.json could not be written.\n' >&2
fi

echo "=========================================================="
if [ "${OVERALL}" -eq 0 ]; then
    echo "  Run finished successfully"
else
    echo "  Run finished with errors"
fi
echo "  Result dir : ${RUN_DIR}"
echo "  Metadata   : ${RUN_DIR}/metadata.json"
echo "  Log        : ${RUN_DIR}/run.log"
echo "=========================================================="

if [ "${OVERALL}" -eq 0 ] && [ "${TEST}" = "both" ]; then
    echo ""
    echo "Plot these results together with the other protocol:"
    echo "  ./plot_qos.sh --map ${MAP_KEY} --run ${RUN_DIR} --run <other-protocol-run-dir>"
fi

exit "${OVERALL}"
