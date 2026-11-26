#!/usr/bin/env python3
"""
validate_qos.py - verify the Praktikum 10 QoS table against the raw .sca files.

The script recomputes every metric directly from the .sca file, compares it
with hasil/qos_summary.csv, checks the recorded PingApp loss scalar, verifies
unit ranges, and checks that AODV and GPSR used the same map, fleet, seed and
radio configuration.  The result is written to hasil/validasi.md.

Usage (from qos_modul10/):
    python3 scripts/validate_qos.py
"""

from __future__ import annotations

import csv
import json
import math
import platform
import sys
from datetime import datetime

from extract_qos import (
    BASE_DIR,
    first_config,
    launch_config_name,
    module_type,
    module_with_scalar,
    node_count,
    parse_sca,
    to_seconds,
)

MANIFEST = BASE_DIR / "data" / "manifest.json"
CSV_PATH = BASE_DIR / "hasil" / "qos_summary.csv"
REPORT = BASE_DIR / "hasil" / "validasi.md"
REPO_ROOT = BASE_DIR.parent

TOL = 5e-4  # CSV keeps 4 decimals


def num(value):
    """Convert a CSV cell to float; empty cells become NaN."""
    if value is None or str(value).strip() == "":
        return float("nan")
    return float(value)


def close(a, b, tol=TOL):
    if math.isnan(a) or math.isnan(b):
        return False
    return abs(a - b) <= tol


def bytes_value(value):
    """Parse '512B' / '1kB' into bytes."""
    if value is None:
        return None
    text = str(value).strip()
    for suffix, factor in (("kB", 1000), ("KB", 1000), ("B", 1)):
        if text.endswith(suffix):
            try:
                return float(text[: -len(suffix)]) * factor
            except ValueError:
                return None
    return None


def config_value(configs, key):
    """First recorded value of a config key (command-line override first)."""
    for name, value in configs:
        if name == key:
            return value.strip('"')
    return None


def show(value):
    """Compact display for report tables."""
    if isinstance(value, float):
        return f"{value:g}"
    return str(value)


def recompute(sca, scenario: str):
    scalars, pars, configs, stats = sca["scalars"], sca["pars"], sca["configs"], sca["stats"]
    result = {
        "run_id": sca["run_id"],
        "seedset": sca["attrs"].get("seedset", ""),
        "launch_config": launch_config_name(pars),
        "module_type": module_type(pars),
        "node_count": node_count(sca),
        "sim_time_limit": to_seconds(first_config(configs, "sim-time-limit")),
    }

    if scenario == "ping":
        src = module_with_scalar(scalars, "Pings sent")
        sent = scalars[(src, "Pings sent")]
        received = scalars.get((src, "pingRxSeq:count"), 0.0)
        rtt = stats.get((src, "rtt:histogram"), {})
        result.update(
            {
                "src": src,
                "sent": sent,
                "received": received,
                "loss": (sent - received) / sent * 100.0 if sent else float("nan"),
                "recorded_loss": scalars.get((src, "ping loss rate (%)"), float("nan")),
                "rtt_min_ms": rtt.get("min", float("nan")) * 1e3,
                "rtt_avg_ms": rtt.get("mean", float("nan")) * 1e3,
                "rtt_max_ms": rtt.get("max", float("nan")) * 1e3,
            }
        )
    elif scenario == "udp":
        src = module_with_scalar(scalars, "packets sent")
        tx = scalars[(src, "packetSent:count")]
        tx_bytes = scalars.get((src, "packetSent:sum(packetBytes)"), 0.0)
        candidates = [
            (module, scalars[(module, name)])
            for (module, name) in scalars
            if name == "packetReceived:count"
            and module != src
            and ".app[" in module
            and scalars[(module, name)] > 0
        ]
        dst, rx = max(candidates, key=lambda item: item[1]) if candidates else (None, 0.0)
        rx_bytes = scalars.get((dst, "packetReceived:sum(packetBytes)"), 0.0) if dst else 0.0
        interval = to_seconds(pars.get((src, "sendInterval")))
        start = to_seconds(pars.get((src, "startTime"))) or 0.0
        duration = (tx - 1) * interval if interval and tx > 1 else float("nan")
        result.update(
            {
                "src": src,
                "dst": dst,
                "tx": tx,
                "rx": rx,
                "tx_bytes": tx_bytes,
                "rx_bytes": rx_bytes,
                "pdr": rx / tx * 100.0 if tx else float("nan"),
                "window": duration,
                "throughput": rx_bytes * 8.0 / (duration * 1000.0) if duration else float("nan"),
                "message_length": bytes_value(pars.get((src, "messageLength"))),
                "interval": interval,
                "start": start,
                "stop": to_seconds(pars.get((src, "stopTime"))),
            }
        )
    return result


def add_check(checks, name, passed, detail=""):
    checks.append((name, bool(passed), detail))


def main():
    if not CSV_PATH.exists():
        print(f"ERROR: {CSV_PATH} not found. Run scripts/extract_qos.py first.", file=sys.stderr)
        return 1

    try:
        manifest = json.loads(MANIFEST.read_text())
    except json.JSONDecodeError as exc:
        print(f"ERROR: manifest.json tidak valid: {exc}", file=sys.stderr)
        return 1

    with CSV_PATH.open(newline="") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        print(f"ERROR: {CSV_PATH} is empty. Run scripts/extract_qos.py again.", file=sys.stderr)
        return 1

    by_key = {(row["map"], row["algorithm"], row["scenario"]): row for row in rows}
    combos = {(combo["map"], combo["algorithm"]): combo for combo in manifest["combinations"]}

    checks = []
    value_rows = []
    provenance_rows = []
    missing = []
    parsed = {}

    for combo in manifest["combinations"]:
        key = (combo["map"], combo["algorithm"])
        if combo["status"] != "available":
            missing.append(combo)
            continue

        for run in combo["runs"]:
            path = BASE_DIR / combo["data_directory"] / run["file"]
            try:
                sca = parse_sca(path)
                parsed[path] = sca
                actual = recompute(sca, run["scenario"])
            except (FileNotFoundError, KeyError, ValueError) as exc:
                add_check(checks, f"read {combo['id']}/{run['scenario']}", False, str(exc))
                continue
            row = by_key.get((combo["map"], combo["algorithm"], run["scenario"]))
            if row is None:
                add_check(checks, f"CSV row {combo['id']}/{run['scenario']}", False, "row missing")
                continue

            provenance_rows.append(
                [
                    combo["map"],
                    combo["algorithm"],
                    run["scenario"],
                    run["file"],
                    actual["run_id"],
                    actual["launch_config"],
                    str(actual["node_count"]),
                    str(actual["seedset"]),
                    f"{actual['sim_time_limit']:g}" if actual["sim_time_limit"] else "",
                ]
            )

            # Provenance must agree with the manifest and with the CSV.
            add_check(
                checks,
                f"run id {combo['id']}/{run['scenario']}",
                actual["run_id"] == run["run_id"] == row["run_id"],
                f"{actual['run_id']}",
            )
            add_check(
                checks,
                f"launch config {combo['id']}/{run['scenario']}",
                actual["launch_config"] == combo["launch_config"] == row["launch_config"],
                f"{actual['launch_config']}",
            )
            add_check(
                checks,
                f"vehicle count {combo['id']}/{run['scenario']}",
                actual["node_count"] == combo["node_count"] == int(num(row["node_count"])),
                f"{actual['node_count']}",
            )
            add_check(
                checks,
                f"seedset {combo['id']}/{run['scenario']}",
                str(actual["seedset"]) == str(combo["seedset"]) == row["seedset"],
                f"{actual['seedset']}",
            )

            if run["scenario"] == "ping":
                pairs = [
                    ("Pings sent", num(row["ping_sent"]), actual["sent"]),
                    ("Pings received", num(row["ping_received"]), actual["received"]),
                    ("Packet loss (%)", num(row["packet_loss_pct"]), actual["loss"]),
                    ("Recorded loss (%)", num(row["packet_loss_recorded_pct"]), actual["recorded_loss"]),
                    ("RTT min (ms)", num(row["rtt_min_ms"]), actual["rtt_min_ms"]),
                    ("RTT avg (ms)", num(row["rtt_avg_ms"]), actual["rtt_avg_ms"]),
                    ("RTT max (ms)", num(row["rtt_max_ms"]), actual["rtt_max_ms"]),
                ]
                for name, csv_value, sca_value in pairs:
                    value_rows.append([combo["id"], run["scenario"], name, f"{csv_value:.4f}", f"{sca_value:.4f}", f"{abs(csv_value - sca_value):.6f}"])
                    add_check(checks, f"{name} {combo['id']}", close(csv_value, sca_value), f"delta={abs(csv_value - sca_value):.6f}")

                add_check(
                    checks,
                    f"computed loss = recorded scalar {combo['id']}",
                    close(actual["loss"], actual["recorded_loss"], 1e-6),
                    f"{actual['loss']:.6f} vs {actual['recorded_loss']:.6f}",
                )
                add_check(
                    checks,
                    f"loss in 0..100 {combo['id']}",
                    0.0 <= actual["loss"] <= 100.0,
                    f"{actual['loss']:.4f}",
                )
            else:
                pairs = [
                    ("Tx packets", num(row["udp_tx_packets"]), actual["tx"]),
                    ("Rx packets", num(row["udp_rx_packets"]), actual["rx"]),
                    ("PDR (%)", num(row["pdr_pct"]), actual["pdr"]),
                    ("Tx bytes", num(row["udp_tx_bytes"]), actual["tx_bytes"]),
                    ("Rx bytes", num(row["udp_rx_bytes"]), actual["rx_bytes"]),
                    ("Window (s)", num(row["measurement_window_s"]), actual["window"]),
                    ("Throughput (kbps)", num(row["throughput_kbps"]), actual["throughput"]),
                ]
                for name, csv_value, sca_value in pairs:
                    value_rows.append([combo["id"], run["scenario"], name, f"{csv_value:.4f}", f"{sca_value:.4f}", f"{abs(csv_value - sca_value):.6f}"])
                    add_check(checks, f"{name} {combo['id']}", close(csv_value, sca_value), f"delta={abs(csv_value - sca_value):.6f}")

                add_check(
                    checks,
                    f"PDR = Rx/Tx*100 {combo['id']}",
                    close(actual["pdr"], actual["rx"] / actual["tx"] * 100.0, 1e-9),
                    f"{actual['pdr']:.6f}",
                )
                add_check(
                    checks,
                    f"PDR in 0..100 {combo['id']}",
                    0.0 <= actual["pdr"] <= 100.0,
                    f"{actual['pdr']:.4f}",
                )
                add_check(
                    checks,
                    f"Rx bytes = Rx * messageLength {combo['id']}",
                    actual["message_length"] is not None
                    and close(actual["rx_bytes"], actual["rx"] * actual["message_length"], 1e-6),
                    f"{actual['rx_bytes']:.0f} bytes",
                )
                add_check(
                    checks,
                    f"Tx bytes = Tx * messageLength {combo['id']}",
                    actual["message_length"] is not None
                    and close(actual["tx_bytes"], actual["tx"] * actual["message_length"], 1e-6),
                    f"{actual['tx_bytes']:.0f} bytes",
                )
                add_check(
                    checks,
                    f"throughput formula {combo['id']}",
                    close(actual["throughput"], actual["rx_bytes"] * 8.0 / (actual["window"] * 1000.0), 1e-9),
                    f"window={actual['window']:g} s",
                )

    # Same-map consistency: AODV and GPSR must share map, fleet, seed and radio.
    consistency_rows = []
    for map_name in ["Map A", "Map B"]:
        ping_rows = {
            row["algorithm"]: row
            for row in rows
            if row["map"] == map_name and row["scenario"] == "ping" and row["status"] == "available"
        }
        if set(ping_rows) != {"AODV", "GPSR"}:
            continue
        aodv_path = BASE_DIR / combos[(map_name, "AODV")]["data_directory"] / "AODV_V2V_Ping-#0.sca"
        gpsr_path = BASE_DIR / combos[(map_name, "GPSR")]["data_directory"] / "GPSR_V2V_Ping-#0.sca"
        aodv = parsed.get(aodv_path) or parse_sca(aodv_path)
        gpsr = parsed.get(gpsr_path) or parse_sca(gpsr_path)

        for label, key in [
            ("launch config", None),
            ("vehicle count", None),
            ("seedset", None),
            ("sim-time-limit", None),
        ]:
            if label == "launch config":
                left, right = launch_config_name(aodv["pars"]), launch_config_name(gpsr["pars"])
            elif label == "vehicle count":
                left, right = node_count(aodv), node_count(gpsr)
            elif label == "seedset":
                left, right = aodv["attrs"].get("seedset"), gpsr["attrs"].get("seedset")
            else:
                left = to_seconds(first_config(aodv["configs"], "sim-time-limit"))
                right = to_seconds(first_config(gpsr["configs"], "sim-time-limit"))
            consistency_rows.append([map_name, label, show(left), show(right), "OK" if left == right else "BEDA"])
            add_check(checks, f"same {label} on {map_name}", left == right, f"{left} vs {right}")

        for label, key in [
            ("radio opMode", "*.node[*].wlan[0].opMode"),
            ("radio type", "*.node[*].wlan[0].radio.typename"),
            ("radio band", "*.node[*].wlan[0].radio.bandName"),
            ("radio channel", "*.node[*].wlan[0].radio.channelNumber"),
            ("radio bandwidth", "*.node[*].wlan[0].radio.bandwidth"),
            ("tx power", "*.node[*].wlan[0].radio.transmitter.power"),
        ]:
            left, right = config_value(aodv["configs"], key), config_value(gpsr["configs"], key)
            consistency_rows.append([map_name, label, show(left), show(right), "OK" if left == right else "BEDA"])
            add_check(checks, f"same {label} on {map_name}", left == right, f"{left} vs {right}")

        for label, param in [("sendInterval", "sendInterval"), ("startTime", "startTime"), ("stopTime", "stopTime")]:
            src_a = module_with_scalar(aodv["scalars"], "Pings sent")
            src_g = module_with_scalar(gpsr["scalars"], "Pings sent")
            left = aodv["pars"].get((src_a, param))
            right = gpsr["pars"].get((src_g, param))
            consistency_rows.append([map_name, label, show(left), show(right), "OK" if left == right else "BEDA"])
            add_check(checks, f"same {label} on {map_name}", left == right, f"{left} vs {right}")

        # The route/network inputs of both workspaces must be identical.
        # Map A uses maps.*, Map B uses map2.*.
        prefix = "maps" if map_name == "Map A" else "map2"
        for asset in [f"{prefix}.launchd.xml", f"{prefix}.rou.xml", f"{prefix}.net.xml", f"{prefix}.sumocfg"]:
            aodv_asset = REPO_ROOT / "vanet_aodv" / asset
            gpsr_asset = REPO_ROOT / "vanet_gpsr" / asset
            same = aodv_asset.exists() and gpsr_asset.exists() and aodv_asset.read_bytes() == gpsr_asset.read_bytes()
            consistency_rows.append(
                [
                    map_name,
                    asset,
                    "file AODV" if aodv_asset.exists() else "tidak ada",
                    "file GPSR" if gpsr_asset.exists() else "tidak ada",
                    "OK (byte-identical)" if same else "BEDA",
                ]
            )
            add_check(checks, f"same {asset} on {map_name}", same, "byte-identical" if same else "different")

    passed = sum(1 for _, ok, _ in checks if ok)
    failed = len(checks) - passed

    lines = []
    lines.append("# Laporan Validasi QoS — Modul Praktikum 10")
    lines.append("")
    lines.append(f"Dibuat: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append(f"Python: {platform.python_version()} | CSV: `hasil/qos_summary.csv`")
    lines.append("")
    lines.append("## 1. Ringkasan")
    lines.append("")
    lines.append(f"- Pemeriksaan dijalankan: **{len(checks)}**")
    lines.append(f"- Lulus: **{passed}**")
    lines.append(f"- Gagal: **{failed}**")
    lines.append(f"- Kombinasi tidak tersedia: **{len(missing)}**")
    lines.append("")
    if failed:
        lines.append("> **PERHATIAN:** ada pemeriksaan yang gagal. Jangan memakai grafik sebelum diperbaiki.")
    elif missing:
        lines.append("> Semua pemeriksaan untuk data yang tersedia lulus. Grafik untuk kombinasi yang datanya belum ada tidak dibuat.")
    else:
        lines.append("> Semua pemeriksaan lulus. Delapan grafik (4 Map A + 4 Map B) dibuat dari data yang tervalidasi.")
    lines.append("")

    lines.append("## 2. Provenance data")
    lines.append("")
    lines.append("| Peta | Algoritma | Skenario | File | Run ID | Launch config | Node | Seed | Durasi (s) |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for row in provenance_rows:
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")

    lines.append("## 3. Nilai CSV vs statistik .sca")
    lines.append("")
    lines.append("| Kombinasi | Skenario | Metrik | CSV | Hitung ulang dari .sca | Selisih |")
    lines.append("|---|---|---|---|---|---|")
    for row in value_rows:
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")

    lines.append("## 4. Konsistensi konfigurasi AODV vs GPSR")
    lines.append("")
    lines.append("| Peta | Parameter | AODV | GPSR | Status |")
    lines.append("|---|---|---|---|---|")
    for row in consistency_rows:
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")

    lines.append("## 5. Asal data per grafik")
    lines.append("")
    lines.append("| Grafik | Metrik | Run AODV | Run GPSR | Status |")
    lines.append("|---|---|---|---|---|")
    graph_metrics = [
        ("packet_loss", "ping", "Packet Loss"),
        ("avg_rtt", "ping", "Average RTT"),
        ("pdr", "udp", "PDR"),
        ("throughput", "udp", "Throughput"),
    ]
    for map_name in ["Map A", "Map B"]:
        slug = map_name.lower().replace(" ", "_")
        for key, scenario, label in graph_metrics:
            aodv_row = by_key.get((map_name, "AODV", scenario))
            gpsr_row = by_key.get((map_name, "GPSR", scenario))
            ready = (
                aodv_row is not None
                and gpsr_row is not None
                and aodv_row["status"] == "available"
                and gpsr_row["status"] == "available"
            )
            if ready:
                lines.append(
                    f"| {slug}_{key}.png | {label} | {aodv_row['run_id']} | "
                    f"{gpsr_row['run_id']} | dibuat |"
                )
            else:
                lines.append(f"| {slug}_{key}.png | {label} | - | - | tidak dibuat |")
    lines.append("")

    lines.append("## 6. Kombinasi yang belum tersedia")
    lines.append("")
    if missing:
        for combo in missing:
            lines.append(f"### {combo['map']} + {combo['algorithm']}")
            lines.append("")
            lines.append(combo.get("missing_reason", ""))
            lines.append("")
            if combo.get("rerun"):
                lines.append("Perintah menjalankan ulang (output diisolasi, tidak menimpa hasil lama):")
                lines.append("")
                lines.append("```bash")
                for command in combo["rerun"]:
                    lines.append(command)
                lines.append("```")
                lines.append("")
        lines.append("Grafik untuk kombinasi yang belum tersedia **tidak dibuat**. Tidak ada angka pengganti atau data sintetis yang digunakan.")
    else:
        lines.append("Tidak ada. Keempat kombinasi (Map A/B × AODV/GPSR) tersedia dan tervalidasi.")
        lines.append("")
        lines.append("Delapan grafik dibuat dari data mentah yang tersedia; tidak ada angka pengganti atau data sintetis yang digunakan.")
    lines.append("")

    lines.append("## 7. Catatan interpretasi")
    lines.append("")
    lines.append("- Setiap kombinasi hanya memiliki **satu run** dengan seedset 0. Hasil ini belum cukup untuk menyimpulkan keunggulan algoritma secara umum.")
    lines.append("- Packet Loss berasal dari run PingApp; PDR dan throughput berasal dari run UDP (UdpBasicApp/UdpSink), bukan dari paket kontrol AODV/GPSR.")
    lines.append("- Pada data Map A ini Packet Loss dan PDR tampak saling melengkapi karena kedua run memakai 38 paket dan jumlah penerimaan yang sama; keduanya tetap berasal dari dua run yang berbeda.")
    lines.append("- Throughput memakai jendela pengukuran aktual: dari paket pertama sampai paket terakhir, yaitu (38 − 1) × 1 s = 37 s, bukan 40 s durasi simulasi.")
    lines.append("- Menurut dokumentasi Praktikum 8, pasangan kendaraan Map A berjarak sekitar 280 m sedangkan jangkauan radio sekitar 228 m; nilai delivery yang rendah adalah sifat skenario Map A, bukan bukti bahwa satu protokol selalu lebih baik.")
    lines.append("")

    REPORT.write_text("\n".join(lines) + "\n")

    print(f"Checks: {len(checks)} | passed: {passed} | failed: {failed}")
    print(f"Report: {REPORT.relative_to(BASE_DIR)}")
    if missing:
        print("Missing combinations: " + ", ".join(f"{c['map']} + {c['algorithm']}" for c in missing))

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
