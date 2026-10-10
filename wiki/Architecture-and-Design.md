# 🏗️ Architecture & System Design

This document details the software architecture, multi-simulator coupling mechanisms, and NED (*Network Description*) module hierarchy of the VANET-AODV simulation platform.

---

## 1. Multi-Simulator Coupling (Bi-directional Synchronization)

Vehicular network simulations require accurate modeling across two fundamentally different domains:
1. **Physical Vehicular Mobility**: Acceleration, braking, lane-changing dynamics, traffic light compliance, and collision avoidance. This is simulated by **Eclipse SUMO**.
2. **Wireless Network Communications**: Radio wave propagation, signal attenuation, interference, MAC contention, routing protocols, and user applications. This is simulated by **OMNeT++** alongside the **INET Framework**.

Real-time synchronization between both simulators is bridged by **Veins** (*Vehicular Network Open, Integrated with OMNeT++*) over the TCP-based **TraCI (Traffic Control Interface)** protocol.

```
       OMNeT++ (Client)                             SUMO (Server)
    ┌──────────────────────┐                     ┌─────────────────┐
    │ VeinsInetManager     │─── TraCI Connect ──►│ Port 9999       │
    │                      │◄── Handshake OK ────│ (sumo / -gui)   │
    │                      │                     │                 │
    │ Time Loop (dt=0.1s): │                     │                 │
    │                      │─── Timestep (t) ───►│ Physical Motion │
    │                      │◄── Vehicle States ──│ Positions (XYZ) │
    │                      │    (Speed, Heading) │ Speeds, Lanes   │
    │ Update INET Node     │                     │                 │
    │ (VeinsInetMobility)  │                     │                 │
    └──────────────────────┘                     └─────────────────┘
```

### Timestep Synchronization Loop:
1. OMNeT++ sends a `timestep` command to the SUMO daemon over the TCP socket at port 9999.
2. SUMO advances its microscopic vehicle physics by the configured update interval (`*.manager.updateInterval = 0.1s`).
3. SUMO responds with active vehicle states, including cartesian coordinates $(x, y, z)$, velocities, and headings.
4. `VeinsInetManager` in OMNeT++ dynamically:
   - Instantiates new `node[i]` submodules when vehicles depart onto the SUMO street network.
   - Updates the physical coordinates of the `VeinsInetMobility` submodules.
   - Deconstructs `node[i]` submodules when vehicles reach their destination and exit the SUMO map.

---

## 2. Network Module Hierarchy (NED Architecture)

Network topologies and submodules are declaratively defined using OMNeT++'s NED language.

### A. Top-Level Network: `Scenario.ned`

```ned
package vanet_aodv;

import inet.physicallayer.wireless.ieee80211.packetlevel.Ieee80211DimensionalRadioMedium;
import org.car2x.veins.subprojects.veins_inet.VeinsInetManager;
import inet.visualizer.common.IntegratedVisualizer;
import inet.environment.common.PhysicalEnvironment;
import org.car2x.veins.visualizer.roads.RoadsCanvasVisualizer;

network Scenario
{
    parameters:
        int numRsu = default(0);
        @display("bgb=2500,2000");
    submodules:
        radioMedium: Ieee80211DimensionalRadioMedium {
            @display("p=150,100");
        }
        manager: VeinsInetManager {
            @display("p=150,200");
        }
        visualizer: IntegratedVisualizer {
            @display("p=150,300");
        }
        physicalEnvironment: PhysicalEnvironment {
            @display("p=150,400");
        }
        roadsCanvasVisualizer: RoadsCanvasVisualizer {
            @display("p=150,500");
        }
        rsu[numRsu]: VeinsAodvRSU {
            @display("p=1040,868");
        }
        node[0]: VeinsAodvCar;
}
```

#### Key Components:
- **`radioMedium` (`Ieee80211DimensionalRadioMedium`)**: Wireless transmission space. Calculates signal reception power, path loss, environmental noise, and packet collisions.
- **`manager` (`VeinsInetManager`)**: TraCI bridge controller managing vehicular lifecycles and coordinate mappings.
- **`roadsCanvasVisualizer` (`RoadsCanvasVisualizer`)**: Renders SUMO street geometries onto the OMNeT++ 2D canvas.
- **`visualizer` (`IntegratedVisualizer`)**: Central engine rendering radio communication ranges, 1-hop MAC links, and multi-hop network routes.
- **`rsu[numRsu]` (`VeinsAodvRSU`)**: Optional static infrastructure gateway node.
- **`node[0]` (`VeinsAodvCar`)**: Dynamic node array placeholder expanded at runtime into `node[0..N-1]`.

---

### B. Vehicular Node: `VeinsAodvCar.ned`

```ned
package vanet_aodv;

import inet.node.aodv.AodvRouter;

module VeinsAodvCar extends AodvRouter
{
    parameters:
        @display("i=veins/node/car;is=vs");
}
```

`VeinsAodvCar` inherits from INET's **`AodvRouter`**, equipping the vehicle with a complete IPv4 network stack:
- **Application Layer (`app[*]`)**: Supports `PingApp`, `UdpBasicApp`, and `UdpSink`.
- **Routing Protocol (`aodv`)**: RFC 3561 AODV routing engine with packet queues and route tables.
- **Network Layer (`ipv4`)**: IP routing, fragmentation, and `GlobalArp`.
- **Wireless Interface (`wlan[*]`)**: IEEE 802.11p NIC coupled with dimensional physical radio.
- **Mobility Submodule (`mobility`)**: Bound to `VeinsInetMobility` to receive real-time coordinates from SUMO.

---

### C. Road-Side Unit: `VeinsAodvRSU.ned`

```ned
package vanet_aodv;

import inet.node.aodv.AodvRouter;

module VeinsAodvRSU extends AodvRouter
{
    parameters:
        @display("i=device/antennatower;is=m");
}
```

The Road-Side Unit also extends `AodvRouter`, but is configured with static infrastructure properties:
- Uses `StationaryMobility` positioned at a central urban intersection $(X=1040\text{m}, Y=868\text{m}, Z=5\text{m})$.
- Employs a higher transmission power ($100\text{ mW}$) to provide broad intersection coverage.

---

## 3. Network Addressing Scheme (IPv4 & ARP)

IP address assignment is automatically handled via INET's **`HostAutoConfigurator`**:

```ini
*.node[*].ipv4.configurator.typename = "HostAutoConfigurator"
*.node[*].ipv4.configurator.interfaces = "wlan0"
*.node[*].ipv4.configurator.addressBase = "10.0.0.0"
*.node[*].ipv4.configurator.netmask = "255.0.0.0"
*.node[*].ipv4.configurator.mcastGroups = "224.0.0.1"
*.node[*].ipv4.arp.typename = "GlobalArp"
```

- **Subnet Structure**: Vehicles and RSUs reside within a single Class A private subnet (`10.0.0.0/8`):
  - Vehicle 0: `10.0.0.1`
  - Vehicle 1: `10.0.0.2`
  - Vehicle $k$: `10.0.0.(k+1)`
  - RSU 0: `10.0.0.X`
- **Global ARP Optimization**: INET's `GlobalArp` resolves MAC-to-IP mappings globally without injecting broadcast ARP requests into the wireless spectrum. This keeps the 5.9 GHz channel clean for accurate measurement of AODV control overhead and application traffic.
