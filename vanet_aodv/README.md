# 🚗 VANET-AODV Simulation Workspace (OMNeT++)

This workspace contains the complete network topology source files (*NED*), simulation configurations (*omnetpp.ini*), SUMO vehicular mobility files, and execution automation scripts for evaluating the **AODV (RFC 3561)** routing protocol in a **VANET** environment.

> 📖 **Comprehensive Documentation**: Complete system architecture, IEEE 802.11p physical layer derivations, and data analysis guides are available in the [Root README](../README.md) and the [Project Wiki](../wiki/Home.md).

---

## 1. Network Topology & NED Modules

The network topology is modularly defined using the following components:

- **`Scenario.ned`**: Top-level network simulation scenario. Integrates the `radioMedium` (IEEE 802.11p DSRC 5.9 GHz), `manager` (`VeinsInetManager`), `visualizer` (`IntegratedVisualizer`), `roadsCanvasVisualizer`, mobile vehicle fleet `node[*]`, and static infrastructure `rsu[*]`.
- **`VeinsAodvCar.ned`**: Mobile vehicular node module extending `inet.node.aodv.AodvRouter`. Equipped with an IEEE 802.11p wireless network interface card (NIC) and a `VeinsInetMobility` TraCI adapter.
- **`VeinsAodvRSU.ned`**: Static Road-Side Unit infrastructure node based on `AodvRouter` positioned at an urban road intersection for V2I scenarios.

---

## 2. Benchmark Simulation Scenarios (`omnetpp.ini`)

All scenarios inherit from the global `[General]` configuration block (including multi-layer visualizer rules, DSRC 5.9 GHz center frequency, and 10.0.0.0/8 subnetting):

| Scenario | Communication Paradigm | Application Stack | Traffic Pattern & Evaluation Focus |
|---|:---:|:---:|---|
| **`AODV_V2V_Ping`** | V2V (1-to-1) | ICMP (`PingApp`) | Vehicle 0 sends periodic pings (56 B) to Vehicle 1 while both move along the streets. Evaluates Round-Trip Time (RTT), symmetric route setup, and discovery latency. |
| **`AODV_V2V_UDP`** | V2V (1-to-1) | UDP (`UdpBasicApp`) | Continuous CBR data stream (512 B) from Vehicle 0 to Vehicle 1 (`UdpSink`). Evaluates throughput and Packet Delivery Ratio (PDR) under topology changes. |
| **`AODV_V2I_RSU`** | V2I ($N$-to-1) | UDP Telemetry | Entire vehicle fleet sends periodic telemetry reports (256 B) to a static central RSU. Evaluates multi-hop aggregation and network scalability. |
| **`AODV_HelloMessages`** | V2V (1-to-1) | UDP + RFC 3561 HELLO | Evaluates AODV with periodic broadcast HELLO messages ($1\text{s}$) enabled to compare routing overhead against MAC layer feedback. |

---

## 3. Map Import (`import_map.sh`) & Fleet Density Scaling

### A. Importing a New Map Directly from an `.osm` File
To replace the road network with any new OpenStreetMap file:

```bash
# Executable from root or vanet_aodv:
./import_map.sh <OSM_FILE> [ACTIVE_VEHICLES]

# Example:
./import_map.sh new_city.osm 25
```
This script converts `.osm` to SUMO format via `netconvert --proj.utm`, computes boundaries and city center coordinates, automatically repositions the RSU in `omnetpp.ini` and `Scenario.ned`, and generates valid shortest-path routes with simultaneous departures at $t=0.00\text{s}$.

---

### B. Modifying Vehicle Count on the Current Map (`set_nodes.py`)
The **`set_nodes.py`** utility adjusts the number of active vehicles running on the current map without rebuilding the network:

```bash
./set_nodes.py <VEHICLE_COUNT>
```

#### Usage Examples:
```bash
# Set sparse traffic (10 vehicles):
./set_nodes.py 10

# Set moderate traffic (25 vehicles):
./set_nodes.py 25

# Set dense traffic (50 vehicles):
./set_nodes.py 50
```

#### Technical Characteristics:
- Extracts routes from the master pool (`maps.rou.all.xml`) and updates `maps.rou.xml`.
- Enforces simultaneous fleet deployment at $t = 0.00\text{ s}$ (`depart="0.00"`).
- Sets instant maximum acceleration (`departSpeed="max"`) and optimal lane choice (`departLane="best"`).

---

## 4. Simulation Execution Guide

### Mode A: Headless Command Line (`run_cmd.sh`)
Designed for automated testing and batch benchmarking without a display:

```bash
# Syntax: ./run_cmd.sh <SCENARIO_NAME> [DURATION]

./run_cmd.sh AODV_V2V_Ping 30s
./run_cmd.sh AODV_V2V_UDP 60s
./run_cmd.sh AODV_V2I_RSU 60s
./run_cmd.sh AODV_HelloMessages 60s
```

*The script automatically verifies and spawns the background `veins_launchd` daemon, runs the simulation, and terminates the daemon safely upon completion.*

---

### Mode B: Interactive Graphical GUI (`run_gui.sh`)
Launches the interactive Qtenv graphical user interface displaying physical radio coverage circles, 1-hop MAC data links, and multi-hop AODV routes:

```bash
# Launch default scenario (AODV_V2V_Ping):
./run_gui.sh

# Launch a specific scenario:
./run_gui.sh AODV_V2V_UDP
./run_gui.sh AODV_V2I_RSU
./run_gui.sh AODV_HelloMessages
```

---

### Mode C: Running via OMNeT++ IDE
1. Start the TraCI daemon in terminal:
   ```bash
   ./run_veins_launchd.sh start
   ```
2. Open OMNeT++ IDE, right-click `omnetpp.ini` > **Run As** > **OMNeT++ Simulation**.
3. Select your target scenario (e.g., `AODV_V2V_Ping`) and click **OK**.
4. Stop the daemon when finished:
   ```bash
   ./run_veins_launchd.sh stop
   ```

---

## 5. Workspace Directory Layout

```text
vanet_aodv/
├── .project                # OMNeT++ IDE project metadata
├── .nedfolders             # NED package root configuration
├── package.ned             # Package declaration (vanet_aodv)
├── Scenario.ned            # Top-level network scenario topology
├── VeinsAodvCar.ned        # Mobile vehicle node module
├── VeinsAodvRSU.ned        # Static Road-Side Unit module
├── omnetpp.ini             # Core simulation configuration & benchmarks
├── empty.xml               # Empty physical environment definition
├── maps.net.xml            # SUMO road network (UTM projection)
├── maps.rou.xml            # Active vehicle routes used in simulation
├── maps.rou.all.xml        # Master pool of vehicle routes
├── maps.sumocfg            # Main SUMO simulation configuration
├── maps.launchd.xml        # TraCI launch configuration for SUMO
├── set_nodes.py            # CLI vehicle density scaler
├── run_cmd.sh              # Headless execution runner (Cmdenv)
├── run_gui.sh              # Interactive GUI execution runner (Qtenv)
├── run_veins_launchd.sh    # Control script for veins_launchd daemon
├── results/                # Recorded telemetry and scalar output (*.sca, *.vec)
└── README.md               # Workspace documentation (this file)
```
