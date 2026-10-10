# 🎨 GUI & Visualization Guide (Qtenv)

This document explains the interactive visualization features of **Qtenv** (OMNeT++), the roles of individual visualizer components, and the physical semantics of rendered lines and circles.

---

## 1. Global Visualizer Architecture (`[General]`)

In `vanet_aodv/omnetpp.ini`, visualizer rules are placed directly within the `[General]` configuration block, ensuring consistent and clear presentation across all scenarios:

```ini
##########################################################
#                GUI: Multi-Layer Visualizer             #
##########################################################

# 1. Disable imaginary propagation rays to maintain clear views
*.visualizer.*.mediumVisualizer.displaySignals = false

# 2. Render PHYSICAL COMMUNICATION RANGE (Calculated Radio Circle)
*.visualizer.*.mediumVisualizer.displayCommunicationRanges = true
*.visualizer.*.mediumVisualizer.communicationRangeLineColor = "deepskyblue"
*.visualizer.*.mediumVisualizer.communicationRangeLineStyle = "solid"
*.visualizer.*.mediumVisualizer.communicationRangeLineWidth = 1.5

# 3. Render 1-HOP MAC DATA LINKS (Successful Unicast Frame & ACK)
*.visualizer.*.dataLinkVisualizer.displayLinks = true
*.visualizer.*.dataLinkVisualizer.lineColor = "gold"
*.visualizer.*.dataLinkVisualizer.lineWidth = 2.5
*.visualizer.*.dataLinkVisualizer.lineStyle = "solid"
*.visualizer.*.dataLinkVisualizer.labelFormat = "%n"
*.visualizer.*.dataLinkVisualizer.labelColor = "darkorange"

# 4. Render END-TO-END AODV NETWORK ROUTES (Multi-Hop Paths)
*.visualizer.*.networkRouteVisualizer.displayRoutes = true
*.visualizer.*.networkRouteVisualizer.lineColor = "lime"
*.visualizer.*.networkRouteVisualizer.lineWidth = 3.5
*.visualizer.*.networkRouteVisualizer.lineStyle = "solid"
*.visualizer.*.networkRouteVisualizer.labelColor = "forestgreen"
```

---

## 2. Visual Elements & Semantic Legend

<div align="center">

| Visual Element | Graphical Appearance | Visualizer Component | Physical Meaning & Protocol Semantics |
|---|:---:|---|---|
| **Physical Radio Range** | 🔵 **DeepSkyBlue Circle** | `mediumVisualizer` | **Real physical transmission boundary**. Other vehicles inside this boundary receive sufficient signal power ($P_{rx} \ge -85\text{ dBm}$) to demodulate frames. |
| **1-Hop MAC Data Link** | 🟡 **Gold Solid Line** (2.5px) | `dataLinkVisualizer` | **Direct 1-hop physical link**. Appears momentarily when an IEEE 802.11p unicast frame is transmitted and confirmed by an ACK. |
| **AODV Multi-Hop Route** | 🟢 **Lime Green Arrow** (3.5px) | `networkRouteVisualizer` | **Active end-to-end network route**. A thick arrow showing the complete multi-hop relay path from source, through relay nodes, to the destination. |
| **Road Network Geometry** | 🟤 **Firebrick Line** | `roadsCanvasVisualizer` | **SUMO road infrastructure**. Renders physical street lanes and intersection layouts onto the OMNeT++ canvas. |
| **Propagation Rays** | ❌ *(Globally Disabled)* | `mediumVisualizer.displaySignals` | **Mathematical path loss calculation lines**. Disabled to eliminate distracting red lines extending across the entire map. |

</div>

---

## 3. Disabling Imaginary Red Rays (`WirelessSignal`)

### Why Were Red Lines Previously Drawn Across the Entire Map?
By default, INET's `mediumVisualizer.displaySignals = true` draws red arrows connecting the transmitting antenna to **every other antenna in the entire simulation world**.
- **Theoretical Intent**: INET indicates that it is computing path loss equations between the transmitter and potential receivers.
- **Physical Reality**: At distances beyond 500 meters or 1 km, a 10mW signal has attenuated below the receiver sensitivity threshold (e.g., $-120\text{ dBm}$). Receivers treat it as noise and immediately discard the packet.
- **Design Decision**: `displaySignals` is **explicitly disabled** to ensure the canvas reflects only verified communication events.

---

## 4. Interactive Qtenv Runtime Inspection

When running in GUI mode (`./run_gui.sh`), you can inspect internal protocol states during simulation runtime:

1. **Inspecting AODV Routing Tables in Real Time**:
   - Right-click any vehicle (e.g., `node[0]` or `node[4]`).
   - Select **Open Component > aodv**.
   - View destination IP addresses, next-hop IPs, sequence numbers, hop counts, and remaining route lifetimes.

2. **Inspecting Radio Transceiver States**:
   - Right-click `node[*] > wlan[0] > radio`.
   - Select **Inspect**.
   - Monitor the instantaneous radio status (*TRANSMITTING*, *RECEIVING*, *IDLE*), current center frequency, and transmission power.

3. **Animation Speed Controls**:
   - **Run (F5)**: Standard smooth real-time animation.
   - **Fast (F6)**: Accelerated execution while still rendering graphics.
   - **Express (F7)**: Maximum computation speed (temporarily disables GUI rendering to process events as quickly as possible).
