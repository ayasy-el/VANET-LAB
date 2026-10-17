# 🧭 GPSR Routing Protocol (Greedy Perimeter Stateless Routing)

This document details the mechanics of the **Greedy Perimeter Stateless Routing (GPSR)** protocol (Karp & Kung, 2000), its behavior in highly dynamic vehicular environments (*VANETs*), and its parameter configurations in INET Framework.

---

## 1. Fundamentals of GPSR in VANET

Unlike topology-based routing protocols (such as AODV or DSR) that maintain end-to-end paths or perform reactive flood-based route discoveries, GPSR is a **geographic (position-based) routing protocol**.

In GPSR:
1. **Stateless Forwarding**: Forwarding decisions are strictly local. Intermediate routers do not maintain per-destination routing state; they only track the physical coordinates of their 1-hop direct neighbors.
2. **Immediate Data Transmission**: Packets are transmitted immediately without a multi-hop discovery phase (such as AODV's RREQ/RREP flood).
3. **Geographic Coordinates**: Packets carry the destination node's spatial coordinates $(x, y)$ in a dedicated network header extension (`GpsrOption`).

```
                    [GREEDY FORWARDING]
  Vehicle (Src) ────► Relay A ────► Relay B ────► Destination (Dst)
      (Each forwarder selects the neighbor geographically closest to Dst)

               [PERIMETER RECOVERY FORWARDING]
                  ┌────── Relay N2 ◄──────┐
                  ▼                       │  (Right-Hand Rule
             Relay N3                     │   along planarized face)
                  │                       ▲
                  └─────► Relay N1 ───────┘
```

---

## 2. Core Routing Mechanics

GPSR operates using two distinct forwarding modes: **Greedy Forwarding** and **Perimeter Forwarding**.

### A. Greedy Forwarding Mode

Under Greedy Forwarding, a node $x$ forwarding a datagram addressed to destination $D$ at position $\mathbf{x}_D$ inspects its 1-hop neighbor table:

$$\text{NextHop} = \arg\min_{y \in \mathcal{N}(x)} \|\mathbf{x}_y - \mathbf{x}_D\|$$

Subject to the greedy progress constraint:

$$\|\mathbf{x}_{\text{NextHop}} - \mathbf{x}_D\| < \|\mathbf{x}_x - \mathbf{x}_D\|$$

If a neighbor $y$ exists that is strictly closer to destination $D$ than node $x$ itself, the packet is forwarded to $y$. This process repeats until the destination is reached.

---

### B. Perimeter Forwarding Mode (Local Void Recovery)

In real urban road layouts with irregular street geometry or sparse vehicular traffic, a packet may encounter a **local minimum** (void), where the current node is closer to the destination than *any* of its 1-hop neighbors:

$$\forall y \in \mathcal{N}(x), \quad \|\mathbf{x}_y - \mathbf{x}_D\| \ge \|\mathbf{x}_x - \mathbf{x}_D\|$$

When a local minimum is detected:
1. The packet transitions from `GPSR_GREEDY_ROUTING` to `GPSR_PERIMETER_ROUTING`.
2. The packet records:
   - `perimeterRoutingStartPosition`: Location where greedy forwarding failed.
   - `currentFaceFirstSenderAddress`: First hop on the planarized face.
3. The node uses the **Right-Hand Rule** to traverse the perimeter of the planarized graph enclosing the void until reaching a node closer to $\mathbf{x}_D$ than `perimeterRoutingStartPosition`.
4. Once progress beyond the void is achieved:
   $$\|\mathbf{x}_{\text{current}} - \mathbf{x}_D\| < \|\mathbf{x}_{\text{start}} - \mathbf{x}_D\|$$
   The packet automatically transitions back to **Greedy Forwarding**.

---

## 3. Planarization Algorithms: GG vs. RNG

Perimeter forwarding requires a **planar graph** (a graph where no two edges cross) to guarantee loop-free right-hand rule traversal. GPSR in INET implements two distributed planarization algorithms:

### 1. Gabriel Graph (GG)
An edge $(u, v)$ is retained in the Gabriel Graph if and only if no other witness node $w$ lies within the circle whose diameter is the line segment $\overline{uv}$:

$$\forall w \notin \{u, v\}, \quad d^2(u, v) < d^2(u, w) + d^2(v, w)$$

### 2. Relative Neighborhood Graph (RNG)
An edge $(u, v)$ is retained in the RNG if and only if no witness node $w$ is closer to both $u$ and $v$ than $d(u, v)$:

$$\forall w \notin \{u, v\}, \quad d(u, v) \le \max(d(u, w), d(v, w))$$

*Properties*:
- The RNG is a subgraph of the GG: $G_{\text{RNG}} \subseteq G_{\text{GG}} \subseteq G$.
- GG preserves higher edge density and lower average hop count than RNG.

---

## 4. Periodic Beaconing & Neighbor Management

To maintain 1-hop geographic awareness without central infrastructure:
1. **Periodic Hello / Beacon**: Each vehicular node periodically broadcasts a 1-hop beacon containing its node ID and current $(x, y, z)$ coordinates.
2. **Jitter Control**: A uniform random delay ($[0, \text{maxJitter}]$) is applied to each beacon transmission to prevent synchronized broadcast collisions across the IEEE 802.11p control channel.
3. **Neighbor Expiration**: If no fresh beacon is received from a neighbor within `neighborValidityInterval`, the stale entry is purged from the neighbor table.

### VANET Calibration Rationale:
In default INET MANET settings (`beaconInterval = 10s`), high-speed vehicular mobility ($50\text{ km/h} \approx 14\text{ m/s}$) causes neighbor tables to become obsolete within seconds. In `vanet_gpsr`, the beacon parameters are calibrated as follows:

| Parameter | Default INET | `vanet_gpsr` Value | Physical Rationale |
|---|:---:|:---:|---|
| `beaconInterval` | $10.0\text{ s}$ | $\mathbf{1.0\text{ s}}$ | Ensures accurate coordinates within $\approx 14\text{ m}$ of movement |
| `maxJitter` | $5.0\text{ s}$ | $\mathbf{0.25\text{ s}}$ | Prevents MAC frame contention |
| `neighborValidityInterval` | $45.0\text{ s}$ | $\mathbf{3.0\text{ s}}$ | Rapidly purges out-of-range vehicular neighbors |

---

## 5. Comparative Evaluation: AODV vs. GPSR in VANET

| Characteristic | AODV (`vanet_aodv`) | GPSR (`vanet_gpsr`) |
|---|---|---|
| **Protocol Class** | Reactive Topology-Based (RFC 3561) | Position-Based Geographic Routing |
| **Route Discovery Overhead** | $O(N)$ broadcast flooding on cache miss | Zero discovery flooding ($O(1)$) |
| **Control Signaling** | On-demand RREQ, RREP, RERR | Periodic 1-hop Beacons |
| **Initial Packet Latency** | High (waits for RREP round-trip) | Low (forwarded immediately) |
| **Link Break Handling** | Route invalidation + RERR to source | Localized re-routing to alternative neighbor |
| **Path Optimality** | Hop-count shortest path | Spatial Euclidean distance progress |
| **Vulnerability** | Broadcast storm during high mobility | Local voids / dead-ends in canyon topologies |
