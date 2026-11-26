# Praktikum 8 — GPSR on Map B (Veins + INET + SUMO)

Status: **implemented and verified** (GPSR V2V Ping and V2V UDP run end-to-end on
Map B; AODV on Map A still runs unchanged).

---

## 1. Environment audit

| Component | Version found | Notes |
|---|---|---|
| OMNeT++ | 6.1 | `~/omnetpp-6.1`, `opp_run` on PATH |
| INET | 4.5.4 | compiled at `~/inet4.5` (`src/libINET.so`) |
| Veins | 5.3.1 | compiled at `~/veins-5.3.1` |
| veins_inet | 5.3.1 | `~/veins-5.3.1/subprojects/veins_inet` |
| SUMO | 1.28.0 | `~/sumo-venv/bin` (apt SUMO is 1.18.0 and **cannot** parse the maps) |

Three defects blocked the workspace before this task:

1. **The run scripts linked libraries that do not exist.**
   `run_cmd.sh` used `-l ${ROOT_DIR}/veins_inet/src/veins_inet`, i.e. the *source*
   tree of the repository copy, which was never compiled. Every run aborted with
   `Cannot load library .../libveins_inet.so`.
   → fixed by `common_env.sh`, which locates an already compiled INET / Veins /
   veins_inet (repository copy first, standalone installation second).

2. **The wrong SUMO was picked up.** `/usr/bin/sumo` is 1.18.0 and rejects the
   committed networks: `Error: Unknown vehicle class 'aircraft' / 'container'`.
   The maps were produced with SUMO 1.28 tools.
   → `common_env.sh` prepends `~/sumo-venv/bin` when it exists.

3. **Veins 5.3.1 rejects SUMO 1.28's TraCI API version.**
   SUMO 1.28 reports TraCI API **22**; `TraCICommandInterface::versionConfigs` only
   knew up to 21, so the run died with *"TraCI server reports unsupported TraCI API
   version"*. Fixed with one extra table entry (see §6).

---

## 2. Files created / modified

### Created

| File | Purpose |
|---|---|
| `common_env.sh` | Shared resolver for OMNeT++, SUMO and the INET/Veins/veins_inet libraries |
| `maps/map_b/map2.net.xml` | Map B road network (copied from the original `map2.net.xml`) |
| `maps/map_b/map2.sumocfg` | Veins-ready SUMO config: `step-length 0.1`, no missing GUI tile file |
| `maps/map_b/map2.trips.xml` | Trip definitions (300 trips) — input for `duarouter` |
| `maps/map_b/map2.pool.xml` | Route pool (300 routes) produced by `duarouter` from `map2.trips.xml` |
| `maps/map_b/map2.poly.xml` | Original polygon/POI definition for Map B (kept for provenance) |
| `maps/map_b/map2.rou.xml` | Generated Map B fleet (80 vehicles) |
| `maps/map_b/build_fleet.py` | Builds `map2.rou.xml` with a deterministic source/destination |
| `vanet_gpsr/map2.launchd.xml` | `veins_launchd` launch config for Map B |
| `vanet_aodv/map2.launchd.xml` | Same, so AODV can also be run on Map B (Praktikum 9) |
| `qos_report.py` | Extracts Ping/UDP QoS metrics from a `.sca` file |
| `docs/PRAKTIKUM8_GPSR_MAP_B.md` | This document |

Symlinks (flat names are mandatory for `veins_launchd`'s `<copy file="...">`):
`vanet_gpsr/{map2.net.xml,map2.rou.xml,map2.sumocfg}` and the same three in
`vanet_aodv/`, all pointing to `../maps/map_b/`.

### Modified

| File | Change |
|---|---|
| `vanet_gpsr/run_cmd.sh`, `run_gui.sh` | Source `common_env.sh`; new `--map <name>` flag; `cd` into the project before starting `veins_launchd` (it resolves `<copy>` entries relative to its working directory) |
| `vanet_aodv/run_cmd.sh`, `run_gui.sh` | Same (the old scripts could not run at all) |
| `vanet_gpsr/omnetpp.ini` | `launchConfig = xmldoc("map2.launchd.xml")` (Map B); `GPSR_V2I_RSU` explicitly stays on Map A |
| `vanet_aodv/omnetpp.ini` | `launchConfig = xmldoc("maps.launchd.xml")` — behaviour identical to before |
| `run_sumo_launchd.sh` | Uses the resolved SUMO-GUI (1.28) instead of hard-coded `PATH` lookup |
| `veins/src/.../TraCICommandInterface.cc` and `~/veins-5.3.1/...` | TraCI API 22 entry (see §6) |

**AODV configuration was not touched**: same network, same NED modules, same radio
parameters, same scenario definitions. Only the launch-config indirection and the
environment resolution changed.

---

## 3. Map B scenario design

The original `map2.rou.xml` spreads 300 trips over 600 s, so during the first 40 s
only a handful of vehicles exist and they are ~1 km apart — V2V communication is
impossible. Map B therefore uses a generated fleet:

* **80 vehicles**, all present from `t = 1 s`, same convention as Map A's
  `set_nodes.py` (all vehicles on the road, `departSpeed="max"`).
* **Source = SUMO vehicle 29 → `node[0]`**, **destination = SUMO vehicle 66 →
  `node[1]`**. They stay **340–450 m** apart for the whole run, which is a stable
  2–3 hop path.
* The mapping is made deterministic by staggered departures: vehicle 29 departs at
  `0.00 s`, vehicle 66 at `0.20 s`, the rest at `1.00 s`. `VeinsInetManager`
  creates one module per vehicle in insertion order, so `node[0]`/`node[1]` are
  fixed. Without this, SUMO chooses the insertion order and `node[0]`/`node[1]`
  landed on vehicles **1182 m apart** (that variant delivered 1/38 pings).

Regenerate / change density:

```bash
cd maps/map_b
# rebuild the route pool (only needed once)
duarouter -n map2.net.xml --route-files map2.trips.xml \
          -o map2.pool.xml --ignore-errors true
# rebuild the fleet
python3 build_fleet.py --pool map2.pool.xml --out map2.rou.xml \
        --count 80 --src 29 --dst 66
```

### Radio range — why the node pair matters

With the unchanged AODV radio parameters (10 mW, 5.9 GHz, 10 MHz, receiver
sensitivity −85 dBm, free-space path loss) the usable range is **≈ 228 m**.
Consequences:

* Map A's legacy pair (`node[0]`–`node[1]`) is ~280 m apart with 20 vehicles —
  the link is at the edge of the range, hence the very low AODV delivery.
* On Map B the pair is deliberately chosen to have 2–3 hops inside that range.

---

## 4. Running the simulation

### 4.1 SUMO only (sanity check of Map B)

```bash
export PATH=$HOME/sumo-venv/bin:$PATH
cd maps/map_b
sumo -c map2.sumocfg            # headless
sumo-gui -c map2.sumocfg        # with GUI
```

### 4.2 GPSR V2V Ping (CLI)

```bash
cd vanet_gpsr
./run_cmd.sh GPSR_V2V_Ping 40s
```

### 4.3 GPSR V2V UDP (CLI)

```bash
cd vanet_gpsr
./run_cmd.sh GPSR_V2V_UDP 40s
```

### 4.4 GUI (Qtenv)

```bash
cd vanet_gpsr
./run_gui.sh GPSR_V2V_Ping      # Map B
./run_gui.sh GPSR_V2V_UDP       # Map B
./run_gui.sh GPSR_V2V_Ping --map maps   # Map A
```

The GUI shows the road canvas, the radio coverage circles, the 1-hop MAC links
(gold) and the multi-hop GPSR routes (cyan). `veins_launchd` starts SUMO headless;
to watch the traffic in SUMO as well, start the SUMO-GUI daemon first in a second
terminal:

```bash
./run_sumo_launchd.sh
```

### 4.5 Extract QoS

```bash
./qos_report.py vanet_gpsr/results/GPSR_V2V_Ping-#0.sca
./qos_report.py vanet_gpsr/results/GPSR_V2V_UDP-#0.sca
```

Equivalent manual query with `opp_scavetool`:

```bash
source common_env.sh
opp_scavetool query -f 'name =~ "Pings sent" OR name =~ "pingRxSeq:count"' \
    vanet_gpsr/results/GPSR_V2V_Ping-#0.sca
```

Formulas used by `qos_report.py`:

```text
Packet Loss (%)      = (Pings sent - Pings received) / Pings sent * 100
PDR (%)              = Rx packets / Tx packets * 100
Throughput (kbit/s)  = Total received bytes * 8 / (measurement window * 1000)
```

The measurement window is the interval between the **first and the last transmitted
packet** (38 packets at 1 s → 37 s), not the 40 s simulation limit and not the
`stopTime = 80 s` of the ini file.

Only application counters are used (`PingApp` / `UdpBasicApp` / `UdpSink`),
never GPSR or AODV control traffic.

---

## 5. Measured results (40 s, run on this machine)

### GPSR V2V Ping — Map B

| Metric | Value |
|---|---|
| Pings sent | 38 |
| Pings received | 27 |
| Packet loss | 28.95 % |
| RTT min / avg / max | 1.088 / 1.400 / 2.256 ms |

### GPSR V2V UDP — Map B

| Metric | Value |
|---|---|
| Tx packets | 38 |
| Rx packets | 26 |
| PDR | 68.42 % |
| Total data received | 13 312 bytes |
| Measurement window | 3 s – 40 s (37 s) |
| Average throughput | 2.88 kbit/s |

### AODV regression — Map A (unchanged configuration)

| Metric | AODV_V2V_Ping | AODV_V2V_UDP |
|---|---|---|
| Pings / Tx packets | 38 | 38 |
| Received / Rx packets | 4 | 4 |
| Loss / PDR | 89.47 % | 10.53 % |
| RTT min/avg/max | 45.673 / 482.451 / 1045.328 ms | — |
| Throughput | — | 0.44 kbit/s |

The AODV numbers are low because of the 228 m radio range versus the 280 m distance
of Map A's legacy vehicle pair — this is a property of the pre-existing Map A
scenario, not a regression introduced here. The run itself is unchanged.

The GPSR values are deterministic (fixed `seedset`), so re-running reproduces them
exactly.

---

## 6. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `Cannot load library .../libveins_inet.so` | Repository framework copies are not compiled | Let `common_env.sh` find `~/inet4.5` / `~/veins-5.3.1`, or build the copies |
| `Unknown vehicle class 'aircraft'` | SUMO 1.18 from apt | Put `~/sumo-venv/bin` first in `PATH` (done by `common_env.sh`) |
| `TraCI server reports unsupported TraCI API version: 22` | Veins 5.3.1 version table | Add `{22, {22, TYPE_DOUBLE, TYPE_POLYGON, VAR_TIME}},` to `versionConfigs` and `make -C veins/src` |
| `GlobalArp does not support dynamic address resolution` | A vehicle left the simulation and a neighbour still addressed it | Keep the fleet alive for the measurement window (see `build_fleet.py`); the generated Map B fleet does this for `node[0]`/`node[1]` |
| Ping loss ≈ 95–100 % | `node[0]`/`node[1]` too far apart (beyond ~228 m per hop) | Re-pick the pair with `build_fleet.py --src/--dst` and verify distances in the SUMO FCD output |
| `Could not connect to TraCI server` | `veins_launchd` not running / port 9999 busy | `./run_veins_launchd.sh status` / `start` |

---

## 7. Praktikum 9 (protocol swap)

Both workspaces contain the assets of both maps, so swapping needs no file edits:

```bash
cd vanet_aodv && ./run_cmd.sh AODV_V2V_Ping 40s --map map2   # AODV on Map B
cd vanet_gpsr && ./run_cmd.sh GPSR_V2V_Ping 40s --map maps   # GPSR on Map A
```

Both combinations were smoke-tested and start correctly. Note that a *meaningful*
result needs a source/destination pair designed for that map: the Map B fleet
(vehicles 29/66) is tuned for Map B, while Map A still uses its legacy pair.
