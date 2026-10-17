# 📚 VANET-AODV Simulation Wiki

Welcome to the official documentation portal (**Wiki**) for the **VANET-AODV** simulation testbed. This wiki provides comprehensive technical references covering system architecture, routing protocols, physical radio propagation, vehicular traffic mobility, and simulation data analysis.

---

## 🧭 Wiki Navigation

| Document | Topic & Scope |
|---|---|
| [**1. Architecture & Design**](Architecture-and-Design.md) | Quad-simulator integration (OMNeT++, INET, Veins, SUMO), NED module hierarchy (`Scenario`, `VeinsAodvCar`, `VeinsAodvRSU`), and TraCI synchronization loop. |
| [**2. AODV Routing Protocol**](Routing-Protocol-AODV.md) | RFC 3561 mechanisms in vehicular networks (RREQ broadcast, RREP unicast, RERR route errors, Expanding Ring Search, and HELLO messages). |
| [**3. GPSR Routing Protocol**](Routing-Protocol-GPSR.md) | Geographic position-based routing (Greedy forwarding, perimeter void traversal via GG/RNG, periodic beaconing, and stateless relaying). |
| [**4. Physical & MAC Layers (IEEE 802.11p)**](Physical-and-MAC-Layers.md) | DSRC 5.9 GHz spectrum, OFDM modulation, Free-Space Path Loss derivation, transmission radius calculation, and antenna offsets. |
| [**5. Traffic Mobility & Road Map**](Traffic-Mobility-and-Map.md) | OpenStreetMap processing, UTM cartesian coordinates, route definitions (`maps.rou.xml`), `set_nodes.py`, and the `import_map.sh` pipeline. |
| [**6. Simulation Scenarios Guide**](Simulation-Scenarios.md) | In-depth parameters and behaviors of benchmark scenarios across AODV and GPSR workspaces. |
| [**7. GUI & Visualization Guide (Qtenv)**](GUI-and-Visualization-Guide.md) | Visual semantics: physical radio ranges (blue), 1-hop MAC links (gold), network routes (green/cyan), and propagation ray filtering. |
| [**8. Data Analysis & Performance Metrics**](Data-Analysis-and-Metrics.md) | Network performance formulas (PDR, RTT latency, throughput, routing overhead), scalar (`.sca`) and vector (`.vec`) data extraction. |
| [**9. Getting Started & Troubleshooting**](Getting-Started-and-Troubleshooting.md) | System requirements, execution instructions for CLI/GUI modes, and solutions to common errors. |

---

## 🔍 System Ecosystem Overview

This project unites industry-standard discrete-event and microscopic traffic simulation frameworks:

```
+-------------------------------------------------------------------------+
|                              Eclipse SUMO                               |
|        (Microscopic Traffic Simulation: Routes, Speeds, Lanes)          |
+-----------------------------------+-------------------------------------+
                                    | TraCI TCP Socket (:9999)
                                    v
+-------------------------------------------------------------------------+
|                                 Veins                                   |
|   (Dynamic Vehicle Synchronization + IEEE 802.11p WAVE Foundation)      |
+-----------------------------------+-------------------------------------+
                                    | VeinsInetMobility
                                    v
+-------------------------------------------------------------------------+
|                           INET Framework 4.5                            |
|  - Application Layer : PingApp, UdpBasicApp, UdpSink                    |
|  - Routing Layer     : AODV (RFC 3561) & GPSR (Position-Based)          |
|  - Network Layer     : IPv4 Stack (10.0.0.0/8), Global ARP              |
|  - Link/MAC Layer    : IEEE 802.11p NIC                                 |
|  - Physical Layer    : Ieee80211DimensionalRadio (5.9 GHz DSRC)         |
+-----------------------------------+-------------------------------------+
                                    | Discrete Event Kernel
                                    v
+-------------------------------------------------------------------------+
|                               OMNeT++ 6.4                               |
|                  (Simulation Engine & Qtenv Visualizer)                 |
+-------------------------------------------------------------------------+
```

---

## 💡 Recommended Reading Path

1. Review [Architecture & Design](Architecture-and-Design.md) to understand how OMNeT++ and SUMO synchronize in time.
2. Study [AODV Routing Protocol](Routing-Protocol-AODV.md) to understand route discovery and maintenance dynamics under high mobility.
3. Review [Physical & MAC Layers](Physical-and-MAC-Layers.md) for the mathematical calculations of transmission range.
4. Select a scenario from the [Simulation Scenarios Guide](Simulation-Scenarios.md) and execute it following [Getting Started & Troubleshooting](Getting-Started-and-Troubleshooting.md).
5. Extract and analyze simulation metrics using the [Data Analysis & Performance Metrics](Data-Analysis-and-Metrics.md) guide.
