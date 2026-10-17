# 🧪 Simulation Scenarios Guide

This document provides a detailed breakdown of the four operational VANET benchmark scenarios defined in `vanet_aodv/omnetpp.ini`.

---

## 1. Scenario Hierarchy

All scenarios build upon the `vanet_aodv.Scenario` network topology and inherit parameters from the global `[General]` section:

```
                           ┌───────────────────────────┐
                           │      [Config General]     │
                           │   5.9GHz Radio, Visual,   │
                           │     AODV Base, TraCI      │
                           └─────────────┬─────────────┘
                                         │
         ┌───────────────────────────────┼───────────────────────────────┐
         ▼                               ▼                               ▼
┌──────────────────┐            ┌──────────────────┐            ┌──────────────────┐
│  AODV_V2V_Ping   │            │   AODV_V2V_UDP   │            │   AODV_V2I_RSU   │
│  V2V Ping (ICMP) │            │  V2V Stream UDP  │            │  V2I Telemetry   │
└──────────────────┘            └────────┬─────────┘            └──────────────────┘
                                         │ extends
                                         ▼
                                ┌──────────────────┐
                                │AODV_HelloMessages│
                                │  UDP + HELLO Msg │
                                └──────────────────┘
```

---

## 2. Technical Breakdown of Benchmark Scenarios

---

### Scenario 1: `[Config AODV_V2V_Ping]`
*Bidirectional Route Discovery Evaluation Using ICMP Echo*

```ini
[Config AODV_V2V_Ping]
description = "V2V AODV routing simulation using ICMP Ping between moving vehicles"

*.node[0].numApps = 1
*.node[0].app[0].typename = "PingApp"
*.node[0].app[0].destAddr = "node[1](ipv4)"
*.node[0].app[0].sendInterval = 1s
*.node[0].app[0].startTime = 3s
*.node[0].app[0].stopTime = 80s
*.node[0].app[0].printPing = true

*.node[*].numApps = 0
```

#### Behavior & Dynamics:
1. **Source (`node[0]`)**: Sends $56\text{-byte}$ ICMP Echo Requests once per second to Vehicle 1.
2. **Destination (`node[1]`)**: Responds with ICMP Echo Replies.
3. **Relay Vehicles (`node[2..N]`)**: Operate purely as AODV packet forwarders.
4. **Primary Evaluation Metrics**:
   - Validates symmetric two-way route establishment (forward and reverse paths).
   - Measures initial route discovery latency (RREQ propagation and RREP return).
   - Tracks Round-Trip Time (RTT) variations as cars move dynamically through the road network.

---

### Scenario 2: `[Config AODV_V2V_UDP]`
*Continuous Unidirectional Data Streaming Across Dynamic Topologies*

```ini
[Config AODV_V2V_UDP]
description = "V2V AODV routing simulation with continuous UDP data transmission"

*.node[1].numApps = 1
*.node[1].app[0].typename = "UdpSink"
*.node[1].app[0].localPort = 5000

*.node[0].numApps = 1
*.node[0].app[0].typename = "UdpBasicApp"
*.node[0].app[0].destAddresses = "node[1](ipv4)"
*.node[0].app[0].destPort = 5000
*.node[0].app[0].messageLength = 512B
*.node[0].app[0].sendInterval = 1s
*.node[0].app[0].startTime = 3s
*.node[0].app[0].stopTime = 80s

*.node[*].numApps = 0
```

#### Behavior & Dynamics:
1. **Continuous Data Stream**: Vehicle 0 transmits constant bitrate (CBR) $512\text{-byte}$ UDP packets to Vehicle 1 at port 5000.
2. **Mobility Stress Test**: Unlike Ping, which pauses between requests, UDP streams packets continuously. When an intermediate relay turns at an intersection, buffered packets are held while AODV performs route rediscovery.
3. **Primary Evaluation Metrics**:
   - **Packet Delivery Ratio (PDR)**: Percentage of transmitted UDP packets received by `UdpSink`.
   - **Average Throughput** ($kbps$).
   - Packet drop frequency during topology breakages.

---

### Scenario 3: `[Config AODV_V2I_RSU]`
*Vehicle-to-Infrastructure Telemetry Reporting*

```ini
[Config AODV_V2I_RSU]
description = "V2I AODV routing simulation to a static Road-Side Unit (RSU)"

*.numRsu = 1

*.rsu[0].mobility.typename = "StationaryMobility"
*.rsu[0].mobility.initialX = 1040m
*.rsu[0].mobility.initialY = 868m
*.rsu[0].mobility.initialZ = 5m
*.rsu[0].mobility.initFromDisplayString = false

*.rsu[0].wlan[0].radio.transmitter.power = 100mW

*.rsu[0].numApps = 1
*.rsu[0].app[0].typename = "UdpSink"
*.rsu[0].app[0].localPort = 5000

*.node[*].numApps = 1
*.node[*].app[0].typename = "UdpBasicApp"
*.node[*].app[0].destAddresses = "rsu[0](ipv4)"
*.node[*].app[0].destPort = 5000
*.node[*].app[0].messageLength = 256B
*.node[*].app[0].sendInterval = uniform(2s, 4s)
*.node[*].app[0].startTime = uniform(2s, 5s)
```

#### Behavior & Dynamics:
1. **Central RSU**: Positioned at a central urban intersection with high transmission power ($100\text{ mW}$, $\approx 718\text{ m}$ radius).
2. **Many-to-One Uplink**: Every moving vehicle in the city periodically ($2 \sim 4\text{ seconds}$) sends telemetry packets ($256\text{ bytes}$) toward the RSU.
3. **Primary Evaluation Metrics**:
   - Multi-source convergence and channel contention near the RSU.
   - Aggregate network throughput and packet collision degradation.
   - Multi-hop mesh aggregation radius.

---

### Scenario 4: `[Config AODV_HelloMessages]`
*Evaluating Periodic HELLO Beacons on Routing Overhead*

```ini
[Config AODV_HelloMessages]
extends = AODV_V2V_UDP
description = "AODV with periodic HELLO messages (RFC 3561) for neighbor sensing"

**.aodv.useHelloMessages = true
**.aodv.helloInterval = 1s
**.aodv.allowedHelloLoss = 2
**.aodv.activeRouteTimeout = 3s
```

#### Behavior & Dynamics:
1. Inherits all parameters from `AODV_V2V_UDP`, but enables RFC 3561 periodic HELLO broadcasts.
2. Nodes broadcast HELLO messages every $1\text{ second}$. If 2 consecutive HELLOs are missed ($2\text{ seconds}$), neighbor links are marked broken without waiting for MAC-layer transmission failures.
3. **Primary Evaluation Metrics**:
   - **Normalized Routing Overhead (NRO)**: Compares bandwidth consumed by HELLO control traffic versus reactive MAC ACK feedback.
   - Route repair latency under active neighbor sensing.

---

## 3. Comparative Benchmark Matrix

| Parameter | `AODV_V2V_Ping` | `AODV_V2V_UDP` | `AODV_V2I_RSU` | `AODV_HelloMessages` |
|---|:---:|:---:|:---:|:---:|
| **Communication Paradigm** | V2V (1-to-1) | V2V (1-to-1) | V2I ($N$-to-1) | V2V (1-to-1) |
| **Transport Layer Protocol** | ICMP | UDP | UDP | UDP |
| **Application Payload Size** | $56\text{ Bytes}$ | $512\text{ Bytes}$ | $256\text{ Bytes}$ | $512\text{ Bytes}$ |
| **Transmission Interval** | $1.0\text{s}$ constant | $1.0\text{s}$ constant | `uniform(2s, 4s)` | $1.0\text{s}$ constant |
| **Active RSUs** | $0$ | $0$ | $1$ | $0$ |
| **AODV HELLO Beacons** | Disabled | Disabled | Disabled | **Enabled ($1\text{s}$)** |
| **Core Research Focus** | RTT & Discovery Latency | PDR & Throughput | Scalability & Contention | Control Channel Overhead |

---

## 4. GPSR Simulation Scenarios (`vanet_gpsr/omnetpp.ini`)

GPSR scenarios evaluate geographic forwarding performance under vehicular mobility:

```
                           ┌───────────────────────────┐
                           │      [Config General]     │
                           │   5.9GHz Radio, Visual,   │
                           │     GPSR Base, TraCI      │
                           └─────────────┬─────────────┘
                                         │
         ┌───────────────────────────────┼───────────────────────────────┐
         ▼                               ▼                               ▼
┌──────────────────┐            ┌──────────────────┐            ┌──────────────────┐
│  GPSR_V2V_Ping   │            │   GPSR_V2V_UDP   │            │   GPSR_V2I_RSU   │
│  V2V Ping (ICMP) │            │  V2V Stream UDP  │            │  V2I Telemetry   │
└──────────────────┘            └────────┬─────────┘            └──────────────────┘
                                         │ extends
                         ┌───────────────┴───────────────┐
                         ▼                               ▼
              ┌─────────────────────┐         ┌─────────────────────┐
              │GPSR_Planarization_RNG│        │ GPSR_Beacon_Tuning  │
              │  RNG Planarization  │         │ Fast Beaconing 0.5s │
              └─────────────────────┘         └─────────────────────┘
```

### GPSR Benchmark Matrix:

| Parameter | `GPSR_V2V_Ping` | `GPSR_V2V_UDP` | `GPSR_V2I_RSU` | `GPSR_Planarization_RNG` | `GPSR_Beacon_Tuning` |
|---|:---:|:---:|:---:|:---:|:---:|
| **Paradigm** | V2V (1-to-1) | V2V (1-to-1) | V2I ($N$-to-1) | V2V (1-to-1) | V2V (1-to-1) |
| **Transport** | ICMP | UDP | UDP | UDP | UDP |
| **Payload** | $56\text{ B}$ | $512\text{ B}$ | $256\text{ B}$ | $512\text{ B}$ | $512\text{ B}$ |
| **Interval** | $1.0\text{s}$ | $1.0\text{s}$ | `uniform(2s, 4s)` | $1.0\text{s}$ | $1.0\text{s}$ |
| **Planarization** | GG (Gabriel Graph) | GG | GG | **RNG (Relative Neighbor)** | GG |
| **Beacon Interval** | $1.0\text{s}$ | $1.0\text{s}$ | $1.0\text{s}$ | $1.0\text{s}$ | **$0.5\text{s}$** |
| **Focus** | Zero-discovery RTT | Geographic PDR | Spatial Convergence | Void recovery modes | High-speed beaconing |
