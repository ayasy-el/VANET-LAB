#!/usr/bin/env python3
"""
plot_qos_charts.py - create the Praktikum 10 QoS bar charts.

Reads hasil/qos_summary.csv and writes four charts per map:

    map_a_packet_loss.png
    map_a_avg_rtt.png
    map_a_pdr.png
    map_a_throughput.png

The same names are used for Map B.  A chart is only written when both AODV
and GPSR have valid data for that map; otherwise the combination is skipped
and reported.  No illustrative or synthetic values are ever plotted.

Usage (from qos_modul10/):
    python3 scripts/plot_qos_charts.py
    python3 scripts/plot_qos_charts.py --map a
    python3 scripts/plot_qos_charts.py --csv /tmp/qos.csv --chart-dir /tmp/charts --map b

Without arguments the script keeps its original behaviour: it reads
hasil/qos_summary.csv and writes all eight charts into grafik/.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # headless, no display needed
import matplotlib.pyplot as plt
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "hasil" / "qos_summary.csv"
CHART_DIR = BASE_DIR / "grafik"

ALGORITHMS = ["AODV", "GPSR"]
COLORS = {"AODV": "#1f4e79", "GPSR": "#c55a11"}
MAPS = ["Map A", "Map B"]
MAP_CHOICES = {"a": "Map A", "b": "Map B"}

METRICS = [
    {
        "key": "packet_loss",
        "scenario": "ping",
        "column": "packet_loss_pct",
        "title": "Packet Loss (V2V Ping)",
        "ylabel": "Packet loss (%)",
        "decimals": 2,
        "suffix": " %",
    },
    {
        "key": "avg_rtt",
        "scenario": "ping",
        "column": "rtt_avg_ms",
        "title": "Average RTT (V2V Ping)",
        "ylabel": "Average RTT (ms)",
        "decimals": 2,
        "suffix": " ms",
    },
    {
        "key": "pdr",
        "scenario": "udp",
        "column": "pdr_pct",
        "title": "Packet Delivery Ratio (V2V UDP)",
        "ylabel": "PDR (%)",
        "decimals": 2,
        "suffix": " %",
    },
    {
        "key": "throughput",
        "scenario": "udp",
        "column": "throughput_kbps",
        "title": "Throughput (V2V UDP)",
        "ylabel": "Throughput (kbps)",
        "decimals": 3,
        "suffix": " kbps",
    },
]


def value_for(df, map_name, algorithm, metric):
    """Return the metric value for one algorithm, or None when unavailable."""
    rows = df[
        (df["map"] == map_name)
        & (df["algorithm"] == algorithm)
        & (df["scenario"] == metric["scenario"])
        & (df["status"] == "available")
    ]
    if rows.empty:
        return None
    value = rows.iloc[0][metric["column"]]
    if pd.isna(value):
        return None
    return float(value)


def footer_text(df, map_name, source_label="Praktikum 8/9"):
    rows = df[(df["map"] == map_name) & (df["status"] == "available")]
    seeds = sorted({f"{float(value):g}" for value in rows["seedset"].dropna().unique()})
    limits = sorted({f"{float(value):g}" for value in rows["sim_time_limit_s"].dropna().unique()})
    seed_text = ", ".join(seeds) if seeds else "?"
    limit_text = ", ".join(limits) if limits else "?"
    return (
        f"Source: OMNeT++ 6.1 .sca results ({source_label}) | "
        f"seedset {seed_text} | {limit_text} s simulation | one run per protocol"
    )


def plot_metric(df, map_name, metric, output_dir, source_label="Praktikum 8/9"):
    values = {algorithm: value_for(df, map_name, algorithm, metric) for algorithm in ALGORITHMS}
    missing = [algorithm for algorithm, value in values.items() if value is None]
    if missing:
        print(
            f"[skip] {map_name} / {metric['key']}: missing data for "
            f"{', '.join(missing)}"
        )
        return False

    heights = [values[algorithm] for algorithm in ALGORITHMS]
    max_value = max(heights)
    y_top = max_value * 1.18 if max_value > 0 else 1.0

    fig, ax = plt.subplots(figsize=(6.4, 4.6))
    bars = ax.bar(
        ALGORITHMS,
        heights,
        width=0.45,
        color=[COLORS[algorithm] for algorithm in ALGORITHMS],
        edgecolor="black",
        linewidth=0.6,
        zorder=3,
    )

    for bar, value in zip(bars, heights):
        label = f"{value:.{metric['decimals']}f}{metric['suffix']}"
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            bar.get_height() + y_top * 0.02,
            label,
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )

    ax.set_title(f"{metric['title']} - {map_name}", pad=12, fontweight="bold")
    ax.set_xlabel("Routing protocol")
    ax.set_ylabel(metric["ylabel"])
    ax.set_ylim(0, y_top)
    ax.yaxis.grid(True, linestyle="--", linewidth=0.6, alpha=0.45, zorder=0)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)

    fig.text(
        0.01,
        0.01,
        footer_text(df, map_name, source_label),
        fontsize=7.5,
        color="#444444",
        ha="left",
    )
    fig.tight_layout(rect=(0, 0.04, 1, 1))

    output_path = output_dir / f"{map_name.lower().replace(' ', '_')}_{metric['key']}.png"
    fig.savefig(output_path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    if not output_path.exists() or output_path.stat().st_size == 0:
        print(f"[fail] empty output: {output_path}")
        return False

    try:
        shown = output_path.relative_to(BASE_DIR)
    except ValueError:
        shown = output_path
    print(f"[ok]   {shown}")
    return True


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Create the Praktikum 10 QoS bar charts.")
    parser.add_argument(
        "--map",
        choices=["a", "b", "all"],
        default="all",
        help="plot one map or both (default: all)",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=CSV_PATH,
        help=f"QoS table to read (default: {CSV_PATH})",
    )
    parser.add_argument(
        "--chart-dir",
        type=Path,
        default=CHART_DIR,
        help=f"output root directory (default: {CHART_DIR})",
    )
    parser.add_argument(
        "--source-label",
        default="Praktikum 8/9",
        help="dataset label printed in the chart footer (default: Praktikum 8/9)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="fail without plotting when a requested map lacks AODV or GPSR data",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    csv_path = args.csv
    chart_dir = args.chart_dir
    maps = MAPS if args.map == "all" else [MAP_CHOICES[args.map]]

    if not csv_path.exists():
        print(f"ERROR: {csv_path} not found. Run scripts/extract_qos.py first.", file=sys.stderr)
        return 1

    try:
        df = pd.read_csv(csv_path)
    except pd.errors.EmptyDataError:
        print(f"ERROR: {csv_path} is empty. Run scripts/extract_qos.py again.", file=sys.stderr)
        return 1
    except pd.errors.ParserError as exc:
        print(f"ERROR: cannot parse {csv_path}: {exc}", file=sys.stderr)
        return 1

    if df.empty:
        print(f"ERROR: {csv_path} has no data rows. Run scripts/extract_qos.py again.", file=sys.stderr)
        return 1

    required = {"map", "algorithm", "scenario", "status", *[m["column"] for m in METRICS]}
    missing_columns = required.difference(df.columns)
    if missing_columns:
        print(f"ERROR: CSV is missing columns: {sorted(missing_columns)}", file=sys.stderr)
        return 1

    # Every chart needs one Ping run (loss, RTT) and one UDP run (PDR,
    # throughput), so completeness means both scenarios for both protocols.
    incomplete = []
    for map_name in maps:
        for algorithm in ALGORITHMS:
            available = df[
                (df["map"] == map_name)
                & (df["algorithm"] == algorithm)
                & (df["status"] == "available")
            ]
            have = set(available["scenario"])
            missing_scenarios = [s for s in ("ping", "udp") if s not in have]
            if missing_scenarios:
                incomplete.append(
                    f"{map_name} / {algorithm} (missing {', '.join(missing_scenarios)})"
                )
    if incomplete and args.strict:
        print("ERROR: dataset is incomplete for the requested map(s):", file=sys.stderr)
        for item in incomplete:
            print(f"  - missing {item}", file=sys.stderr)
        print("No chart was written.", file=sys.stderr)
        return 1

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.labelsize": 10.5,
            "xtick.labelsize": 10.5,
            "ytick.labelsize": 9.5,
        }
    )

    created = 0
    skipped = 0
    for map_name in maps:
        output_dir = chart_dir / map_name.lower().replace(" ", "_")
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n[{map_name}]")
        for metric in METRICS:
            if plot_metric(df, map_name, metric, output_dir, args.source_label):
                created += 1
            else:
                skipped += 1

    print(f"\nCreated {created} chart(s); skipped {skipped}.")
    if skipped:
        print(
            "Charts were skipped for combinations without valid data. "
            "Check the QoS table and its validation report."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
