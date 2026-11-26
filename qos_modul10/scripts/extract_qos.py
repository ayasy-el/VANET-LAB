#!/usr/bin/env python3
"""
extract_qos.py - build a QoS table for Praktikum 10 from OMNeT++ .sca files.

The script reads data/manifest.json, parses the .sca file of every available
run, and writes hasil/qos_summary.csv.  Only application-level counters are
used (PingApp, UdpBasicApp, UdpSink); AODV/GPSR control traffic is ignored.

Usage (from qos_modul10/):
    python3 scripts/extract_qos.py
    python3 scripts/extract_qos.py --manifest other.json --output /tmp/qos.csv

Output:
    hasil/qos_summary.csv (default)

Formulas:
    Packet Loss (%) = (Ping Sent - Ping Received) / Ping Sent * 100
    PDR (%)         = Rx Packets / Tx Packets * 100
    Throughput      = Total Received Bytes * 8 / (Measurement Duration * 1000)

Measurement duration is read from the application parameters of each run
(sendInterval, startTime), not assumed from the 40 s simulation limit.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MANIFEST = BASE_DIR / "data" / "manifest.json"
OUTPUT = BASE_DIR / "hasil" / "qos_summary.csv"

COLUMNS = [
    "map",
    "algorithm",
    "scenario",
    "status",
    "source_file",
    "run_id",
    "run_datetime",
    "seedset",
    "sim_time_limit_s",
    "node_count",
    "launch_config",
    "module_type",
    "ping_sent",
    "ping_received",
    "packet_loss_pct",
    "packet_loss_recorded_pct",
    "rtt_min_ms",
    "rtt_avg_ms",
    "rtt_max_ms",
    "udp_tx_packets",
    "udp_rx_packets",
    "pdr_pct",
    "udp_tx_bytes",
    "udp_rx_bytes",
    "measurement_window_s",
    "throughput_kbps",
    "notes",
]


KEEP_ATTRS = {"configname", "datetime", "seedset", "runnumber", "replication"}
KEEP_SCALARS = {
    "Pings sent",
    "pingRxSeq:count",
    "ping loss rate (%)",
    "packets sent",
    "packetSent:count",
    "packetSent:sum(packetBytes)",
    "packetReceived:count",
    "packetReceived:sum(packetBytes)",
}
KEEP_MANAGER_PARS = {"launchConfig", "moduleType"}
KEEP_APP_PARS = {"sendInterval", "startTime", "stopTime", "messageLength"}
NODE_PREFIX = "Scenario.node["


def clean_value(text):
    """Strip one layer of quotes and unescape OMNeT++'s escaped quotes."""
    text = text.strip()
    if len(text) >= 2 and text[0] == '"' and text[-1] == '"':
        text = text[1:-1]
    return text.replace('\\"', '"').strip('"')


def split_name_value(rest):
    """Split a scalar/statistic rest field that may start with a quoted name."""
    if rest.startswith('"'):
        end = rest.find('"', 1)
        if end != -1:
            return rest[1:end], rest[end + 1:].strip()
    parts = rest.split(None, 1)
    return (parts[0], parts[1].strip()) if len(parts) == 2 else (rest, "")


def parse_sca(path: Path) -> dict:
    """Parse the small subset of an OMNeT++ 6 .sca file that this module needs.

    Only application counters, a few parameters and the RTT histogram are kept.
    Lines that cannot contribute (bin edges, per-module attributes, unrelated
    parameters) are skipped before any expensive string parsing.  This keeps
    the parser fast on the 5-20 MB .sca files produced by Map B.
    """
    configs = []          # ordered (key, value); first value = command-line override
    pars = {}             # (module, parameter) -> value
    scalars = {}          # (module, scalar name) -> float
    stats = {}            # (module, statistic name) -> {field: float}
    attrs = {}            # run attributes (configname, seedset, ...)
    run_id = ""
    current_stat = None
    max_node = -1

    with path.open(errors="replace") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue

            key = line.split(None, 1)[0]
            if key == "bin" or key == "version":
                continue

            if key == "run":
                run_parts = line.split(None, 1)
                run_id = run_parts[1] if len(run_parts) == 2 else ""
                current_stat = None
            elif key == "attr":
                parts = line.split(None, 2)
                if len(parts) == 3 and parts[1] in KEEP_ATTRS:
                    attrs[parts[1]] = clean_value(parts[2])
                current_stat = None
            elif key == "config":
                parts = line.split(None, 2)
                if len(parts) == 3:
                    configs.append((parts[1], clean_value(parts[2])))
                current_stat = None
            elif key == "par":
                parts = line.split(None, 3)
                if len(parts) == 4:
                    module, param, value = parts[1], parts[2], parts[3]
                    if module.startswith(NODE_PREFIX):
                        start = len(NODE_PREFIX)
                        end = module.find("]", start)
                        if end != -1:
                            try:
                                max_node = max(max_node, int(module[start:end]))
                            except ValueError:
                                pass
                    keep = (
                        (module == "Scenario.manager" and param in KEEP_MANAGER_PARS)
                        or (module.endswith(".app[0]") and param in KEEP_APP_PARS)
                    )
                    if keep:
                        pars[(module, param)] = clean_value(value)
                current_stat = None
            elif key == "scalar":
                parts = line.split(None, 2)
                if len(parts) == 3:
                    module, rest = parts[1], parts[2]
                    if module.startswith(NODE_PREFIX):
                        start = len(NODE_PREFIX)
                        end = module.find("]", start)
                        if end != -1:
                            try:
                                max_node = max(max_node, int(module[start:end]))
                            except ValueError:
                                pass
                    name, value = split_name_value(rest)
                    if name in KEEP_SCALARS:
                        try:
                            scalars[(module, name)] = float(value)
                        except ValueError:
                            pass
                current_stat = None
            elif key == "statistic":
                parts = line.split(None, 2)
                if len(parts) == 3:
                    module, name = parts[1], clean_value(parts[2])
                    if module.startswith(NODE_PREFIX):
                        start = len(NODE_PREFIX)
                        end = module.find("]", start)
                        if end != -1:
                            try:
                                max_node = max(max_node, int(module[start:end]))
                            except ValueError:
                                pass
                    current_stat = (module, name) if name == "rtt:histogram" else None
                    if current_stat:
                        stats[current_stat] = {}
            elif key == "field":
                if current_stat:
                    parts = line.split(None, 2)
                    if len(parts) == 3:
                        try:
                            stats[current_stat][parts[1]] = float(parts[2])
                        except ValueError:
                            pass

    return {
        "configs": configs,
        "pars": pars,
        "scalars": scalars,
        "stats": stats,
        "attrs": attrs,
        "run_id": run_id,
        "max_node": max_node,
    }


def to_seconds(value):
    """Convert an OMNeT++ time string ('40s', '500ms') to seconds."""
    if value is None:
        return None
    value = str(value).strip()
    for suffix, factor in (("ms", 1e-3), ("us", 1e-6), ("ns", 1e-9), ("s", 1.0)):
        if value.endswith(suffix):
            try:
                return float(value[: -len(suffix)]) * factor
            except ValueError:
                return None
    try:
        return float(value)
    except ValueError:
        return None


def first_config(configs, key):
    """Return the first value of a config key (the command-line override)."""
    for name, value in configs:
        if name == key:
            return value
    return None


def module_with_scalar(scalars, scalar_name):
    """Return the module that recorded a given scalar, or None."""
    for (module, name) in scalars:
        if name == scalar_name:
            return module
    return None


def launch_config_name(pars):
    """Extract the launchd XML basename from the resolved manager parameter."""
    raw = pars.get(("Scenario.manager", "launchConfig"), "")
    match = re.search(r"([^/\s]+\.xml):\d+", raw)
    return match.group(1) if match else raw


def module_type(pars):
    raw = pars.get(("Scenario.manager", "moduleType"), "")
    raw = raw.strip().strip('"')
    return raw.split(".")[-1] if raw else ""


def node_count(sca):
    """Highest Scenario.node[N] index plus one."""
    return sca["max_node"] + 1 if sca["max_node"] >= 0 else 0


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ping_metrics(scalars, stats):
    src = module_with_scalar(scalars, "Pings sent")
    if src is None:
        raise ValueError("no 'Pings sent' scalar found")

    sent = scalars.get((src, "Pings sent"), 0.0)
    received = scalars.get((src, "pingRxSeq:count"), 0.0)
    loss = (sent - received) / sent * 100.0 if sent else float("nan")
    recorded_loss = scalars.get((src, "ping loss rate (%)"), float("nan"))

    rtt = stats.get((src, "rtt:histogram"), {})
    return {
        "ping_sent": sent,
        "ping_received": received,
        "packet_loss_pct": loss,
        "packet_loss_recorded_pct": recorded_loss,
        "rtt_min_ms": rtt.get("min", float("nan")) * 1e3,
        "rtt_avg_ms": rtt.get("mean", float("nan")) * 1e3,
        "rtt_max_ms": rtt.get("max", float("nan")) * 1e3,
    }


def udp_metrics(configs, pars, scalars):
    src = module_with_scalar(scalars, "packets sent")
    if src is None:
        raise ValueError("no 'packets sent' scalar found")

    tx = scalars.get((src, "packetSent:count"), 0.0)
    tx_bytes = scalars.get((src, "packetSent:sum(packetBytes)"), 0.0)

    # The sink is the application module that actually received packets.
    candidates = []
    for (module, name) in scalars:
        if name != "packetReceived:count" or module == src or ".app[" not in module:
            continue
        count = scalars[(module, name)]
        if count > 0:
            candidates.append((module, count))
    dst, rx = max(candidates, key=lambda item: item[1]) if candidates else (None, 0.0)
    rx_bytes = scalars.get((dst, "packetReceived:sum(packetBytes)"), 0.0) if dst else 0.0
    pdr = rx / tx * 100.0 if tx else float("nan")

    start = to_seconds(pars.get((src, "startTime")))
    interval = to_seconds(pars.get((src, "sendInterval")))
    start = 0.0 if start is None else start

    # Measurement window = first to last transmitted packet.  This is read
    # from the app parameters of this run, not assumed to be 40 s.
    if interval and tx > 1:
        duration = (tx - 1) * interval
    else:
        stop = to_seconds(pars.get((src, "stopTime")))
        limit = to_seconds(first_config(configs, "sim-time-limit"))
        end = min(value for value in (stop, limit) if value is not None)
        duration = end - start

    throughput = rx_bytes * 8.0 / (duration * 1000.0) if duration else float("nan")
    return {
        "udp_tx_packets": tx,
        "udp_rx_packets": rx,
        "pdr_pct": pdr,
        "udp_tx_bytes": tx_bytes,
        "udp_rx_bytes": rx_bytes,
        "measurement_window_s": duration,
        "throughput_kbps": throughput,
    }


def fmt(value, digits=4):
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def row_for_run(combination, run):
    path = BASE_DIR / combination["data_directory"] / run["file"]
    if not path.exists():
        raise FileNotFoundError(f"missing data file: {path}")

    actual_hash = sha256(path)
    if actual_hash != run["sha256"]:
        raise ValueError(
            f"sha256 mismatch for {path}\n"
            f"  manifest: {run['sha256']}\n"
            f"  actual  : {actual_hash}"
        )

    sca = parse_sca(path)
    metrics = {
        "ping_sent": "",
        "ping_received": "",
        "packet_loss_pct": "",
        "packet_loss_recorded_pct": "",
        "rtt_min_ms": "",
        "rtt_avg_ms": "",
        "rtt_max_ms": "",
        "udp_tx_packets": "",
        "udp_rx_packets": "",
        "pdr_pct": "",
        "udp_tx_bytes": "",
        "udp_rx_bytes": "",
        "measurement_window_s": "",
        "throughput_kbps": "",
    }

    if run["scenario"] == "ping":
        metrics.update(ping_metrics(sca["scalars"], sca["stats"]))
    elif run["scenario"] == "udp":
        metrics.update(udp_metrics(sca["configs"], sca["pars"], sca["scalars"]))
    else:
        raise ValueError(f"unknown scenario: {run['scenario']}")

    limit = to_seconds(first_config(sca["configs"], "sim-time-limit"))
    row = {
        "map": combination["map"],
        "algorithm": combination["algorithm"],
        "scenario": run["scenario"],
        "status": "available",
        "source_file": str(Path(combination["data_directory"]) / run["file"]),
        "run_id": sca["run_id"],
        "run_datetime": sca["attrs"].get("datetime", ""),
        "seedset": sca["attrs"].get("seedset", ""),
        "sim_time_limit_s": fmt(limit, 0) if limit is not None else "",
        "node_count": node_count(sca),
        "launch_config": launch_config_name(sca["pars"]),
        "module_type": module_type(sca["pars"]),
        "notes": combination.get("provenance_note", ""),
    }

    for key, value in metrics.items():
        if key in ("ping_sent", "ping_received", "udp_tx_packets", "udp_rx_packets"):
            row[key] = fmt(value, 0)
        elif key in ("udp_tx_bytes", "udp_rx_bytes"):
            row[key] = fmt(value, 0)
        elif key == "measurement_window_s":
            row[key] = fmt(value, 2)
        else:
            row[key] = fmt(value, 4)
    return row


def row_for_missing(combination):
    row = {column: "" for column in COLUMNS}
    row.update(
        {
            "map": combination["map"],
            "algorithm": combination["algorithm"],
            "scenario": "ping+udp",
            "status": "missing",
            "notes": combination.get("missing_reason", ""),
        }
    )
    return row


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Extract application-level QoS metrics from OMNeT++ .sca files."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=MANIFEST,
        help=f"provenance manifest to read (default: {MANIFEST})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT,
        help=f"CSV file to write (default: {OUTPUT})",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    manifest_path = args.manifest
    output_path = args.output

    if not manifest_path.exists():
        print(f"ERROR: manifest not found: {manifest_path}", file=sys.stderr)
        return 1

    try:
        manifest = json.loads(manifest_path.read_text())
    except json.JSONDecodeError as exc:
        print(f"ERROR: {manifest_path} tidak valid: {exc}", file=sys.stderr)
        return 1

    rows = []
    try:
        for combination in manifest["combinations"]:
            if combination["status"] != "available":
                rows.append(row_for_missing(combination))
                print(f"[skip] {combination['id']}: {combination['status']}")
                continue
            for run in combination["runs"]:
                row = row_for_run(combination, run)
                rows.append(row)
                print(
                    f"[ok]   {combination['id']:<12} {run['scenario']:<4} "
                    f"run={row['run_id']} map={row['launch_config']} nodes={row['node_count']}"
                )
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        print(
            "CSV lama tidak ditimpa. Perbaiki manifest atau salin ulang "
            "file .sca, lalu jalankan lagi.",
            file=sys.stderr,
        )
        return 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    try:
        shown = output_path.relative_to(BASE_DIR)
    except ValueError:
        shown = output_path
    print(f"\nWrote {len(rows)} rows to {shown}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
