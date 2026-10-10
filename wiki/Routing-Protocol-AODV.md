# 🧭 AODV Routing Protocol (RFC 3561)

This document details the mechanics of the **Ad hoc On-Demand Distance Vector (AODV)** routing protocol according to **RFC 3561**, its behavior in highly dynamic vehicular environments (*VANETs*), and its parameter configurations in INET Framework.

---

## 1. Fundamentals of AODV in VANET

AODV is a **reactive (on-demand)** routing protocol. Unlike proactive protocols (such as OLSR or DSDV) that continuously maintain fresh paths to every destination in the network via periodic topology broadcasts, AODV **initiates route discovery only when an application needs to transmit data**.

This reactive paradigm is particularly suited for VANETs because:
1. **High Topology Dynamics**: High vehicle velocities cause links to break and expire quickly. Proactively maintaining complete network paths wastes significant 5.9 GHz bandwidth.
2. **Bandwidth Conservation**: Control message overhead remains minimal when data transmission occurs only between specific pairs or clusters of vehicles.
3. **Loop-Free Operation**: Destination Sequence Numbers (**DestSeqNum**) strictly prevent routing loops and guarantee fresh route selection.

---

## 2. AODV Route Lifecycle

```
               [Phase 1: ROUTE DISCOVERY]
  Source (Src) ─── RREQ Broadcast (Multi-Hop) ───► Destination (Dst)
  Source (Src) ◄─── RREP Unicast (Reverse Path) ── Destination (Dst)

               [Phase 2: DATA TRANSMISSION]
  Source (Src) ════════════ Data Packets ════════► Destination (Dst)

               [Phase 3: ROUTE MAINTENANCE]
  (Link breaks due to vehicle motion)
  Forwarder ────── RERR (Route Error) ───────────► Source (Src)
```

---

### A. Route Discovery Mechanism

When a source node (e.g., `node[0]`) needs to send packets to a destination (`node[1]`) but does not possess a valid routing entry:

1. **RREQ Generation**:
   - The source creates a `RREQ` (Route Request) packet containing:
     - `Source IP` & `Source Sequence Number`
     - `Broadcast ID` (incremented for each new RREQ)
     - `Destination IP` & `Last Known Destination Sequence Number`
     - `Hop Count = 0`
   - The RREQ packet is broadcasted to all 1-hop physical neighbors within range.

2. **Reverse Path Setup**:
   - Each intermediate neighbor receiving the RREQ checks the tuple `(Source IP, Broadcast ID)`. Duplicate packets are immediately discarded.
   - The node establishes a **Reverse Path** entry in its routing table, recording the previous hop neighbor as the path back to the source.
   - The Hop Count is incremented by 1. If the node is not the destination and does not have a fresh route to the destination, it rebroadcasts the RREQ.

3. **RREP Generation & Forward Path Setup**:
   - When the RREQ arrives at the destination (`node[1]`), the destination increments its own sequence number.
   - The destination generates a `RREP` (Route Reply) packet and transmits it **unicast** along the Reverse Path.
   - Intermediate forwarders process the RREP and establish a **Forward Path** toward the destination.
   - Upon receiving the RREP at the source, packet buffering ends and data transmission begins immediately.

---

### B. Expanding Ring Search Algorithm

To prevent broadcast flooding across the entire city when the destination is physically close to the source, AODV employs **Expanding Ring Search**:

1. AODV broadcasts the initial RREQ with a small Time-To-Live (TTL):
   $$\text{TTL}_{start} = 2$$
2. If no RREP is received within the discovery timeout window, TTL is incrementally increased:
   $$\text{TTL}_{next} = \text{TTL}_{prev} + \text{TTL}_{increment} \quad (\text{TTL}_{increment} = 2)$$
3. This process repeats until the threshold is reached:
   $$\text{TTL}_{threshold} = 7$$
4. If no route is found at $\text{TTL}_{threshold}$, a full network broadcast is executed:
   $$\text{TTL} = \text{NetDiameter} = 30$$

---

### C. Route Maintenance & Error Handling

Vehicular mobility continuously breaks communication links when cars move apart or turn at intersections.

1. **Link Breakage Detection**:
   - Detected when IEEE 802.11p MAC frame transmissions fail to receive an ACK after maximum retry attempts.
   - Alternatively (if enabled), detected when expected periodic *AODV HELLO* messages are missed from a neighboring node.
2. **RERR Dissemination**:
   - The node that detects the link failure marks the affected routing entries as invalid.
   - It issues a `RERR` (Route Error) message listing unreachable destinations to all upstream *precursor* nodes that utilize this link.
3. **Route Recovery**:
   - Upstream nodes forward the RERR back to the source.
   - The source can initiate a new *Route Discovery* sequence to find an alternative active path.

---

## 3. RFC 3561 HELLO Messages vs MAC Layer Feedback

The scenario `[Config AODV_HelloMessages]` evaluates the trade-offs of enabling periodic HELLO beacons:

```ini
[Config AODV_HelloMessages]
extends = AODV_V2V_UDP
**.aodv.useHelloMessages = true
**.aodv.helloInterval = 1s
**.aodv.allowedHelloLoss = 2
**.aodv.activeRouteTimeout = 3s
```

| Parameter Comparison | Without Hello Messages (Default `omnetpp.ini`) | With Hello Messages (`AODV_HelloMessages`) |
|---|---|---|
| **Neighbor Sensing Mechanism** | Uses MAC layer feedback (802.11p ACK failure). | Periodic broadcast of HELLO packets every $1\text{ second}$. |
| **Channel Overhead** | Very low. Wireless spectrum is utilized only when active user data is transmitted. | Scales linearly with the number of active vehicles in the area. |
| **Failure Detection Speed** | Instantaneous during active data flow. | Governed by timeout: $2 \times \text{helloInterval} = 2\text{ seconds}$. |
| **Recommendation in Dense VANET** | Strongly recommended to prevent spectrum saturation. | Useful for research benchmarking of proactive neighbor monitoring. |

---

## 4. AODV INET Configuration Parameters

Below are the primary AODV parameters configured in `vanet_aodv/omnetpp.ini`:

```ini
##########################################################
#             AODV Routing Protocol Parameters           #
##########################################################
**.aodv.interface = "wlan0"
**.aodv.activeRouteTimeout = 3s
**.aodv.useHelloMessages = false
**.aodv.askGratuitousRREP = false
**.aodv.destinationOnlyFlag = false
**.aodv.rreqRetries = 3
**.aodv.rreqRatelimit = 20
**.aodv.rerrRatelimit = 20
**.aodv.ttlStart = 2
**.aodv.ttlIncrement = 2
**.aodv.ttlThreshold = 7
**.aodv.netDiameter = 30
**.aodv.nodeTraversalTime = 0.05s
```

### Parameter Reference:
- **`activeRouteTimeout = 3s`**: Route entry validity duration. If no data passes through an active route for 3 seconds, it is marked expired. Given typical vehicle speeds, 3 seconds prevents stale routing loops.
- **`rreqRetries = 3`**: Maximum RREQ broadcast attempts before declaring a destination unreachable.
- **`rreqRatelimit = 20`**: Limits RREQ broadcasts to 20 packets per second to mitigate broadcast storm problems.
- **`nodeTraversalTime = 0.05s`**: Conservative single-hop propagation estimate ($50\text{ ms}$) used to compute RREP waiting timeouts.
