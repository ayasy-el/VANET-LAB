#!/usr/bin/env python3
"""
qos_report.py - extract VANET QoS metrics from an OMNeT++ scalar result file.

Works with the .sca files produced by the Ping and UDP scenarios of the
vanet_aodv / vanet_gpsr projects.  Only application-level counters are used,
never routing-protocol (AODV/GPSR) control traffic.

Usage:
    ./qos_report.py <result.sca> [<result.sca> ...]

Metrics
-------
V2V Ping
    Pings sent / received, packet loss (%), min / avg / max RTT (ms)

V2V UDP
    Tx packets, Rx packets, PDR (%), total data received (bytes),
    average throughput (kbit/s)

Throughput uses the real traffic window (stopTime - startTime, clipped to the
simulation time limit), not the whole simulation.
"""

import shlex
import sys


def parse_sca(path):
    configs, pars, scalars, stats, attrs = {}, {}, {}, {}, {}
    current = None
    with open(path, errors="replace") as f:
        for raw in f:
            try:
                parts = shlex.split(raw.strip())
            except ValueError:
                continue
            if not parts:
                continue
            key = parts[0]
            if key in ("version", "run", "config", "par", "scalar", "statistic"):
                current = None
            if key == "attr" and len(parts) >= 3:
                attrs[parts[1]] = parts[2]
            elif key == "config" and len(parts) >= 3:
                configs[parts[1]] = parts[2]
            elif key == "par" and len(parts) >= 4:
                pars[(parts[1], parts[2])] = parts[3]
            elif key == "scalar" and len(parts) >= 4:
                try:
                    scalars[(parts[1], parts[2])] = float(parts[3])
                except ValueError:
                    pass
            elif key == "statistic" and len(parts) >= 3:
                current = (parts[1], parts[2])
                stats[current] = {}
            elif key == "field" and current and len(parts) >= 3:
                try:
                    stats[current][parts[1]] = float(parts[2])
                except ValueError:
                    pass
    return configs, pars, scalars, stats, attrs


def to_seconds(value):
    """Parse an OMNeT++ time string such as '40s', '3s', '500ms'."""
    if value is None:
        return None
    value = value.strip()
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


def find_module(scalars, suffix):
    """Return the first module name that ends with the given suffix."""
    for (mod, _name) in scalars:
        if mod.endswith(suffix):
            return mod
    return None


def report_ping(path, scalars, stats, pars):
    src = None
    for (mod, name) in scalars:
        if name == "Pings sent":
            src = mod
            break
    if src is None:
        return False

    sent = scalars.get((src, "Pings sent"), scalars.get((src, "pingTxSeq:count"), 0.0))
    received = scalars.get((src, "pingRxSeq:count"), 0.0)
    loss = (sent - received) / sent * 100.0 if sent else float("nan")

    rtt = stats.get((src, "rtt:histogram"), {})
    rtt_min = rtt.get("min", float("nan")) * 1e3
    rtt_avg = rtt.get("mean", float("nan")) * 1e3
    rtt_max = rtt.get("max", float("nan")) * 1e3

    print(f"  Source node          : {src}")
    print(f"  Pings sent           : {int(sent)}")
    print(f"  Pings received       : {int(received)}")
    print(f"  Packet loss          : {loss:.2f} %")
    print(f"  RTT min / avg / max  : {rtt_min:.3f} / {rtt_avg:.3f} / {rtt_max:.3f} ms")
    return True


def report_udp(path, configs, pars, scalars):
    src = None
    for (mod, name) in scalars:
        if name == "packets sent":
            src = mod
            break
    if src is None:
        return False

    tx = scalars.get((src, "packetSent:count"), 0.0)
    tx_bytes = scalars.get((src, "packetSent:sum(packetBytes)"), 0.0)

    # the sink is the node whose application received packets
    dst = None
    for (mod, name) in scalars:
        if name != "packetReceived:count" or mod == src or ".app[" not in mod:
            continue
        if scalars[(mod, name)] > 0:
            dst = mod
            break
    rx = scalars.get((dst, "packetReceived:count"), 0.0) if dst else 0.0
    rx_bytes = scalars.get((dst, "packetReceived:sum(packetBytes)"), 0.0) if dst else 0.0

    pdr = rx / tx * 100.0 if tx else float("nan")

    # Measurement window = time between the first and the last transmitted
    # packet.  This is independent of the configured stopTime (which is longer
    # than the simulation time limit in the 40 s laboratory runs).
    start = to_seconds(pars.get((src, "startTime")))
    interval = to_seconds(pars.get((src, "sendInterval")))
    if start is None:
        start = 0.0
    if interval and tx > 1:
        duration = (tx - 1) * interval
    else:
        stop = to_seconds(pars.get((src, "stopTime")))
        sim_limit = to_seconds(configs.get("sim-time-limit"))
        end = min(x for x in (stop, sim_limit) if x is not None)
        duration = end - start
    end = start + duration
    throughput = (rx_bytes * 8.0) / (duration * 1000.0) if duration else float("nan")

    print(f"  Source node          : {src}")
    print(f"  Sink node            : {dst}")
    print(f"  Tx packets           : {int(tx)}")
    print(f"  Rx packets           : {int(rx)}")
    print(f"  PDR                  : {pdr:.2f} %")
    print(f"  Total data received  : {int(rx_bytes)} bytes")
    print(f"  Measurement window   : {start:g} s .. {end:g} s ({duration:g} s)")
    print(f"  Average throughput   : {throughput:.2f} kbit/s")
    return True


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    for path in sys.argv[1:]:
        configs, pars, scalars, stats, attrs = parse_sca(path)
        print("=" * 62)
        print(f"  {path}")
        print(f"  config: {attrs.get('configname', '?')}")
        print("=" * 62)
        if not (report_ping(path, scalars, stats, pars) or report_udp(path, configs, pars, scalars)):
            print("  [!] no PingApp / UdpBasicApp statistics found in this file")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
