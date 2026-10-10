<p align="center">
  <img src="https://raw.githubusercontent.com/sommer/veins/master/doc/veins.png" alt="VANET Logo" width="100" onerror="this.style.display='none'"/>
</p>

<h1 align="center">🚗 VANET-AODV: Vehicular Ad-Hoc Network Simulation Testbed</h1>

<p align="center">
  <strong>Comprehensive Simulation Environment for Ad hoc On-Demand Distance Vector (RFC 3561) Routing over IEEE 802.11p WAVE/DSRC in Realistic Urban Mobility</strong>
</p>

<p align="center">
  <a href="https://omnetpp.org/"><img src="https://img.shields.io/badge/OMNeT%2B%2B-6.4.0-007acc.svg?style=flat-square&logo=c%2B%2B" alt="OMNeT++ 6.4.0"/></a>
  <a href="https://inet.omnetpp.org/"><img src="https://img.shields.io/badge/INET%20Framework-4.5.4-2b9348.svg?style=flat-square" alt="INET 4.5.4"/></a>
  <a href="https://veins.car2x.org/"><img src="https://img.shields.io/badge/Veins-5.3.1-orange.svg?style=flat-square" alt="Veins 5.3.1"/></a>
  <a href="https://eclipse.dev/sumo/"><img src="https://img.shields.io/badge/Eclipse%20SUMO-v1.x-555555.svg?style=flat-square" alt="Eclipse SUMO"/></a>
  <a href="https://datatracker.ietf.org/doc/html/rfc3561"><img src="https://img.shields.io/badge/Routing-AODV%20(RFC%203561)-blueviolet.svg?style=flat-square" alt="RFC 3561 AODV"/></a>
  <a href="https://standards.ieee.org/ieee/802.11p/3929/"><img src="https://img.shields.io/badge/PHY%2FMAC-IEEE%20802.11p%20(5.9%20GHz)-e63946.svg?style=flat-square" alt="IEEE 802.11p"/></a>
  <img src="https://img.shields.io/badge/Documentation-Wiki%20Available-success.svg?style=flat-square" alt="Wiki"/>
  <img src="https://img.shields.io/badge/License-Academic%20%2F%20MIT-informational.svg?style=flat-square" alt="License"/>
</p>

---

## 📑 Table of Contents

- [📌 Overview](#-overview)
- [✨ Key Features](#-key-features)
- [🏗️ System Architecture](#️-system-architecture)
- [📡 Radio & Network Specifications](#-radio--network-specifications)
- [🧪 Simulation Scenarios & Benchmark Matrix](#-simulation-scenarios--benchmark-matrix)
- [🖥️ Multi-Layer Network Visualizer (Qtenv)](#️-multi-layer-network-visualizer-qtenv)
- [🗺️ Map Import & Traffic Scaling](#️-map-import--traffic-scaling)
- [🚀 Quick Start Guide](#-quick-start-guide)
- [📊 Evaluation Metrics & Output Files](#-evaluation-metrics--output-files)
- [📚 Project Wiki & Documentation](#-project-wiki--documentation)
- [📂 Directory Layout](#-directory-layout)
- [📄 References & License](#-references--license)

---

## 📌 Overview

**VANET-AODV** is an integrated vehicular network simulation testbed designed to evaluate the performance of the reactive **Ad hoc On-Demand Distance Vector (AODV, RFC 3561)** routing protocol across realistic urban traffic environments.

The platform couples microscopic road traffic mobility from **Eclipse SUMO** with physical radio propagation modeling and the complete communication protocol stack from **INET Framework** via the **Veins TraCI** bridge. Because the simulated urban road topology extends over $2.08\text{ km} \times 1.74\text{ km}$ while vehicular radio range is constrained to $\approx 227\text{ meters}$, the AODV routing engine adaptively discovers and maintains multi-hop packet relay paths as vehicles maneuver dynamically.

```
┌─────────────────┐             ┌─────────────────┐             ┌─────────────────┐
│ Vehicle 0 (Src) │             │ Vehicle Relay   │             │ Vehicle 1 (Dst) │
└────────┬────────┘             └────────┬────────┘             └────────┬────────┘
         │                               │                               │
         ├────── RREQ (Broadcast) ──────►│                               │
         │                               ├────── RREQ (Broadcast) ──────►│
         │                               │◄───── RREP (Unicast) ─────────┤
         │◄───── RREP (Unicast) ─────────┤                               │
         │                                                               │
         │══════ MULTI-HOP DATA STREAM (ICMP / UDP) ════════════════════►│
```

---

## ✨ Key Features

- **Quad-Simulator Coupling**: Bi-directional real-time synchronization between OMNeT++ 6.4, INET 4.5.4, Veins 5.3.1, and SUMO via TraCI.
- **Full RFC 3561 Compliance**: Comprehensive AODV lifecycle implementation (RREQ broadcast, RREP unicast, RERR route error, expanding ring search, and periodic HELLO neighbor sensing).
- **Realistic DSRC/WAVE Physical Layer**: IEEE 802.11p transceiver at $5.9\text{ GHz}$ (Channel 3, 10 MHz channel bandwidth), thermal noise floor of $-110\text{ dBm}$, and Free-Space Path Loss attenuation.
- **Real-World Urban Geospatial Model**: Real road network extracted from OpenStreetMap covering an area of $\approx 3.61\text{ km}^2$.
- **Simultaneous Zero-Second Fleet Deployment**: All vehicles deploy and accelerate simultaneously at $t = 0.00\text{ s}$ (`departSpeed="max"` and `departLane="best"`) for immediate ad-hoc interactions.
- **Comprehensive V2V & V2I Evaluation Suite**: Standardized benchmarks for Vehicle-to-Vehicle (ICMP ping, continuous UDP CBR) and Vehicle-to-Infrastructure (RSU telemetry reporting).
- **Clean Multi-Layer Visualization**: Calibrated Qtenv visualizer distinctly separating physical radio range, 1-hop MAC links, and multi-hop AODV forwarding paths.
- **One-Command OSM Map Importer**: End-to-end automated pipeline (`import_map.sh`) to import any OpenStreetMap `.osm` file and immediately run it without manual configuration.

---

## 🏗️ System Architecture

The simulation environment is structured with clean modular separation between traffic flow and telecommunications domains:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                   ECLIPSE SUMO                                         │
│       Microscopic Traffic Simulator: Car-Following, Collision Avoidance, Speeds        │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │ TraCI TCP Socket (Port 9999)
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              VEINS (veins_launchd Bridge)                              │
│       Coordinate System Translation & Dynamic OMNeT++ Vehicle Instantiation            │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │ VeinsInetMobility
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                  INET FRAMEWORK 4.5                                    │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│  │ APPLICATION LAYER   : PingApp (ICMP) / UdpBasicApp / UdpSink                     │  │
│  ├──────────────────────────────────────────────────────────────────────────────────┤  │
│  │ ROUTING LAYER       : AODV Routing Engine (RFC 3561 Dynamic Discovery & Repair)  │  │
│  ├──────────────────────────────────────────────────────────────────────────────────┤  │
│  │ NETWORK LAYER       : IPv4 Auto-Configuration (10.0.0.0/8) & Global ARP          │  │
│  ├──────────────────────────────────────────────────────────────────────────────────┤  │
│  │ MAC / LINK LAYER    : IEEE 802.11p Network Interface Controller (NIC)            │  │
│  ├──────────────────────────────────────────────────────────────────────────────────┤  │
│  │ PHYSICAL LAYER      : Ieee80211DimensionalRadioMedium (5.9 GHz DSRC Channel 3)   │  │
│  └──────────────────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📡 Radio & Network Specifications

Physical layer and transceiver properties are configured according to vehicular communications standards:

| Parameter | Vehicle Node (*Car*) | Infrastructure (*RSU*) | Unit / Value |
|---|:---:|:---:|:---:|
| **Center Frequency** | $5.9\text{ GHz}$ | $5.9\text{ GHz}$ | DSRC Band |
| **Channel Number** | Channel 3 | Channel 3 | 802.11p standard |
| **Channel Bandwidth** | $10\text{ MHz}$ | $10\text{ MHz}$ | Half-clocked OFDM |
| **Transmitter Power ($P_{tx}$)** | $10\text{ mW}$ ($+10\text{ dBm}$) | $100\text{ mW}$ ($+20\text{ dBm}$) | DSRC regulations |
| **Reception Sensitivity ($P_{rx\_min}$)** | $-85\text{ dBm}$ | $-85\text{ dBm}$ | Modulation threshold |
| **Theoretical Communication Range ($d_{max}$)** | $\approx \mathbf{227\text{ m}}$ | $\approx \mathbf{718\text{ m}}$ | Free-Space Path Loss |
| **Thermal Noise Floor** | $-110\text{ dBm}$ | $-110\text{ dBm}$ | Environmental noise |
| **Antenna Height ($Z$)** | $1.5\text{ m}$ (vehicle roof) | $5.0\text{ m}$ (tower mast) | Cartesian coordinate |
| **IPv4 Subnet** | `10.0.0.0/8` | `10.0.0.0/8` | Private Class A |

> 📖 **Mathematical Derivation**: Full Friis free-space propagation derivation and parameter calibration formulas are documented in [Physical & MAC Layers Wiki](wiki/Physical-and-MAC-Layers.md).

---

## 🧪 Simulation Scenarios & Benchmark Matrix

Scenarios are declaratively configured in `vanet_aodv/omnetpp.ini`:

| Scenario | Paradigm | Application Stack | Traffic Load | Primary Evaluation Focus |
|---|:---:|:---:|:---:|---|
| **`AODV_V2V_Ping`** | V2V (1:1) | ICMP (`PingApp`) | 56 B / $1\text{s}$ | Round-trip latency (RTT), RREQ/RREP discovery overhead, packet loss rate |
| **`AODV_V2V_UDP`** | V2V (1:1) | UDP (`UdpBasicApp`) | 512 B / $1\text{s}$ | Continuous throughput ($kbps$), Packet Delivery Ratio (PDR) |
| **`AODV_V2I_RSU`** | V2I ($N$:1) | UDP Telemetry | 256 B / $2\sim4\text{s}$ | Many-to-one uplink aggregation, RSU coverage resilience |
| **`AODV_HelloMessages`** | V2V (1:1) | UDP + RFC 3561 HELLO | 512 B / $1\text{s}$ + Hello $1\text{s}$ | Control routing overhead comparison (beaconing vs MAC link-layer feedback) |

---

## 🖥️ Multi-Layer Network Visualizer (Qtenv)

Visualizer rules are configured centrally under the `[General]` section in `omnetpp.ini` to guarantee uniform, uncluttered presentation across all scenarios:

| Visual Element | Graphical Appearance | Component | Physical & Protocol Semantics |
|---|:---:|---|---|
| **Physical Radio Range** | 🔵 **DeepSkyBlue Circle** | `mediumVisualizer` | Real radio propagation boundary ($P_{rx} \ge -85\text{ dBm}$). |
| **1-Hop MAC Data Link** | 🟡 **Gold Solid Line** (2.5px) | `dataLinkVisualizer` | Successful unicast frame transmission with MAC ACK acknowledgement. |
| **AODV Multi-Hop Route** | 🟢 **Lime Green Line** (3.5px) | `networkRouteVisualizer` | Active end-to-end multi-hop forwarding route stored in routing tables. |
| **Road Network Geometry** | 🟤 **Firebrick Line** | `roadsCanvasVisualizer` | 2D canvas projection of SUMO street centerlines and junctions. |

> [!NOTE]
> Imaginary radio wave propagation rays (`mediumVisualizer.displaySignals`) are globally disabled to remove screen clutter and ensure focus on verifiable network communication links.

---

## 🗺️ Map Import & Traffic Scaling

### A. Automated OSM Map Importer (`import_map.sh`)
To import any new urban region from OpenStreetMap (`.osm`) in a single step:

```bash
# Syntax: ./import_map.sh <OSM_FILE> [ACTIVE_VEHICLES]

# Example: Import a new map with 30 active vehicles
./import_map.sh new_city.osm 30

# Or regenerate with the default map (map.osm):
./import_map.sh map.osm 20
```

**Automated Pipeline Workflow:**
1. **`netconvert`**: Converts `.osm` into `maps.net.xml` with real UTM cartesian coordinates (`--proj.utm`).
2. **Auto Center RSU**: Extracts `convBoundary`, calculates urban centroid, and automatically positions RSU in `omnetpp.ini` and `Scenario.ned`.
3. **Auto Resize Canvas**: Adjusts canvas dimensions `@display("bgb=...")` in `Scenario.ned` to match the new map size.
4. **`randomTrips.py` & `duarouter`**: Generates valid shortest-path routes across connected road segments.
5. **Fleet Synchronization**: Formats all vehicles to depart simultaneously at $t = 0.00\text{ s}$ (`departSpeed="max"`).
6. **Workspace Sync**: Deploys updated files directly to `vanet_aodv/`, making the simulation instantly ready to run.

---

### B. Dynamic Fleet Density Scaling (`set_nodes.py`)
For an already imported map, adjust the vehicle count at any time without rebuilding the road network:

```bash
cd vanet_aodv

# Scale fleet density:
./set_nodes.py 10    # 10 vehicles (sparse traffic)
./set_nodes.py 25    # 25 vehicles (moderate traffic)
./set_nodes.py 50    # 50 vehicles (dense traffic)
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites & Environment Setup

Ensure OMNeT++ 6.4, INET 4.5, Veins 5.3, and SUMO are installed and exported to your shell environment:

```bash
cd /path/to/VANET-LAB
source ../setenv
```

### 2. Interactive Graphical Mode (Qtenv)

Launch the TraCI daemon with SUMO-GUI in your first terminal:
```bash
./run_sumo_launchd.sh
```

In a second terminal, start the interactive OMNeT++ visualizer:
```bash
cd vanet_aodv

# Launch default scenario (AODV_V2V_Ping):
./run_gui.sh

# Or select a specific scenario:
./run_gui.sh AODV_V2V_UDP
./run_gui.sh AODV_V2I_RSU
./run_gui.sh AODV_HelloMessages
```

### 3. Headless Batch Mode (Cmdenv)

For automated benchmarking or executions on remote servers without a display:
```bash
cd vanet_aodv

# Syntax: ./run_cmd.sh <SCENARIO_NAME> [DURATION]
./run_cmd.sh AODV_V2V_Ping 30s
./run_cmd.sh AODV_V2V_UDP 60s
./run_cmd.sh AODV_V2I_RSU 100s
```

---

## 📊 Evaluation Metrics & Output Files

Simulations automatically store structured telemetry in `vanet_aodv/results/`:
- **`*.sca` (Scalar)**: Aggregate simulation statistics (packets sent/received, mean latency, loss counts).
- **`*.vec` (Vector)**: Dynamic time-series metrics (per-packet RTT, throughput over time).

### Key Performance Formulas:

1. **Packet Delivery Ratio (PDR)**:
   $$\text{PDR} = \left(\frac{\sum \text{Packets Received}}{\sum \text{Packets Sent}}\right) \times 100\%$$
2. **Average End-to-End Latency / RTT**:
   $$\text{RTT}_{\text{avg}} = \frac{1}{N} \sum_{i=1}^N \text{RTT}_i$$
3. **Network Throughput**:
   $$\text{Throughput (kbps)} = \frac{\sum \text{Bits Received}}{\Delta t \times 1000}$$

---

## 📚 Project Wiki & Documentation

Comprehensive technical documentation is maintained under the **`wiki/`** directory:

| Wiki Document | Description |
|---|---|
| [**Home**](wiki/Home.md) | Central documentation portal and index. |
| [**Architecture & Design**](wiki/Architecture-and-Design.md) | Quad-simulator integration, NED hierarchy, and TraCI loop. |
| [**AODV Routing Protocol**](wiki/Routing-Protocol-AODV.md) | RFC 3561 deep dive, expanding ring search, and routing tables. |
| [**Physical & MAC Layers**](wiki/Physical-and-MAC-Layers.md) | Mathematical Friis derivation, 5.9 GHz DSRC, and antenna setup. |
| [**Traffic & Mobility Model**](wiki/Traffic-Mobility-and-Map.md) | OSM geospatial mapping, UTM bounds, and simultaneous departures. |
| [**Simulation Scenarios Guide**](wiki/Simulation-Scenarios.md) | Detailed parameter reference for all 4 benchmark scenarios. |
| [**GUI Visualization Guide**](wiki/GUI-and-Visualization-Guide.md) | Runtime inspection guide, visual semantics, and filter explanations. |
| [**Data Analysis & Metrics**](wiki/Data-Analysis-and-Metrics.md) | `opp_scavetool` extraction procedures and automated Python parsers. |
| [**Execution & Troubleshooting**](wiki/Getting-Started-and-Troubleshooting.md) | Step-by-step setup and solutions to common simulation errors. |

---

## 📂 Directory Layout

```text
VANET-LAB/
├── inet/                  # INET Framework 4.5 (Core Network & Physical layers)
├── veins/                 # Veins 5.3 (Vehicular framework & TraCI client)
├── veins_inet/            # Veins-INET subproject (Mobility adapter)
├── map.osm                # Raw OpenStreetMap geospatial source
├── maps.net.xml           # Converted SUMO road network (UTM projection)
├── maps.rou.xml           # Active vehicle routes used in simulation
├── maps.sumocfg           # Primary microscopic SUMO simulation configuration
├── import_map.py          # Python automation pipeline for .osm map import
├── import_map.sh          # Bash runner for automated map import
├── run_sumo_launchd.sh    # Daemon launcher for veins_launchd + SUMO-GUI
├── wiki/                  # Comprehensive project technical documentation
│   ├── Home.md
│   ├── Architecture-and-Design.md
│   ├── Routing-Protocol-AODV.md
│   ├── Physical-and-MAC-Layers.md
│   ├── Traffic-Mobility-and-Map.md
│   ├── Simulation-Scenarios.md
│   ├── GUI-and-Visualization-Guide.md
│   ├── Data-Analysis-and-Metrics.md
│   └── Getting-Started-and-Troubleshooting.md
├── vanet_aodv/            # OMNeT++ SIMULATION WORKSPACE
│   ├── Scenario.ned       # Top-level network scenario topology
│   ├── VeinsAodvCar.ned   # Mobile vehicular node extending AodvRouter
│   ├── VeinsAodvRSU.ned   # Static Road-Side Unit infrastructure node
│   ├── omnetpp.ini        # Core simulation parameters & benchmark scenarios
│   ├── maps.rou.all.xml   # Master pool of vehicle routes
│   ├── set_nodes.py       # Instant vehicle fleet density scaler CLI
│   ├── run_cmd.sh         # Automated headless command-line runner
│   ├── run_gui.sh         # Automated interactive graphical runner
│   └── results/           # Output directory for simulation records (*.sca, *.vec)
└── README.md              # Project documentation gateway
```

---

## 📄 References & License

- **License**: This project is licensed for research and academic evaluation (*Academic Public License*).
- **Standards & Publications**:
  - RFC 3561: *Ad hoc On-Demand Distance Vector (AODV) Routing*, IETF.
  - IEEE Std 802.11p-2010: *Wireless Access in Vehicular Environments (WAVE)*.
  - Sommer, C., German, R., & Dressler, F. (2011). *Bidirectionally Coupled Network and Road Traffic Simulation for Improved IVC Analysis*. IEEE Transactions on Mobile Computing.
