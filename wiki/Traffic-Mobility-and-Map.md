# 🗺️ Traffic Mobility & Road Map

This document describes the processing of urban geospatial road data, microscopic vehicular mobility configuration in **Eclipse SUMO**, fleet scaling utilities, and the automated OSM import pipeline.

---

## 1. Geospatial Road Modeling (OpenStreetMap to SUMO)

The baseline simulation uses road network data exported from OpenStreetMap (`map.osm`) covering an urban district. The conversion follows SUMO's processing pipeline:

```
┌──────────────┐                  ┌──────────────┐                  ┌──────────────┐
│   map.osm    │── netconvert ───►│ maps.net.xml │── duarouter ────►│ maps.rou.xml │
│ (Raw OSM XML)│                  │(Cartesian Net│   trips.trips.xml│(Active Routes│
└──────────────┘                  └──────────────┘                  └──────────────┘
```

### A. Dimensions & Boundary Box (`convBoundary`)
In `maps.net.xml`, longitude/latitude WGS84 coordinates are projected into local cartesian meters using UTM (*Universal Transverse Mercator*):

```xml
<location netOffset="-698305.12,-9199320.14" 
          convBoundary="0.00,0.00,2080.89,1737.66" 
          origBoundary="112.7915000,-7.3015000,112.8105000,-7.2856000" 
          projParameter="+proj=utm +zone=49 +ellps=WGS84 +datum=WGS84 +units=m +no_defs"/>
```

- **Horizontal Width (X-axis)**: $0.00\text{ m} \rightarrow 2080.89\text{ m}$ ($\approx 2.08\text{ km}$)
- **Vertical Height (Y-axis)**: $0.00\text{ m} \rightarrow 1737.66\text{ m}$ ($\approx 1.74\text{ km}$)
- **Maximum Diagonal**:
  $$\text{Diagonal} = \sqrt{(2080.89)^2 + (1737.66)^2} \approx \mathbf{2,711\text{ meters}}$$
- **Total Area**:
  $$\text{Area} = 2.08089\text{ km} \times 1.73766\text{ km} \approx \mathbf{3.61\text{ km}^2}$$

---

## 2. Vehicle Route Management (`maps.rou.xml`)

Route files dictate origin-destination paths, vehicular classes, and microscopic driving behaviors (e.g., the Krauss car-following model).

### The Staggered Departure Problem
By default, random trip generators assign staggered departure times (Vehicle 0 at $t=0\text{s}$, Vehicle 1 at $t=1\text{s}$, Vehicle 2 at $t=2\text{s}$, etc.).
- **Impact on VANET Research**: In a 30-second run, later vehicles only enter the simulation toward the very end. The network remains heavily partitioned during the initial seconds, preventing early multi-hop packet routing.

### The Simultaneous Deployment Solution
In this testbed, all active vehicles are scheduled to **deploy simultaneously at $t = 0.00\text{ seconds}$**:
```xml
<vehicle id="0" type="veh_passenger" depart="0.00" departLane="best" departSpeed="max">
    <route edges="44815464#0 44815464#1 44815464#2 ..."/>
</vehicle>
```
- **`depart="0.00"`**: Vehicles populate the road network from second zero.
- **`departLane="best"`**: Cars immediately occupy optimal lanes for their respective paths, avoiding merge bottlenecks.
- **`departSpeed="max"`**: Cars start at road speed limits rather than accelerating slowly from a dead stop.

---

## 3. Dynamic Vehicle Density Scaling (`set_nodes.py`)

To quickly benchmark different traffic densities without editing XML manually, the Python utility **`vanet_aodv/set_nodes.py`** extracts a chosen subset from the master route pool (`maps.rou.all.xml`):

```bash
cd vanet_aodv

# Low density (10 vehicles):
./set_nodes.py 10

# Medium density (25 vehicles):
./set_nodes.py 25

# High density (50 vehicles):
./set_nodes.py 50
```

```text
[✓] Berhasil mengupdate maps.rou.xml menjadi 25 mobil (semua depart di t=0.00s).
```

---

## 4. Automated Map Import Pipeline (`import_map.py` / `import_map.sh`)

To import any new urban area from OpenStreetMap (`.osm`) in a **single automated step**:

```bash
# General syntax:
./import_map.sh <OSM_FILE> [ACTIVE_VEHICLES]

# Example:
./import_map.sh new_city.osm 30
```

### ⚙️ Pipeline Execution Steps:
1. **Road Network Extraction (`netconvert`)**:
   Applies UTM cartesian projection (`--proj.utm`) and cleans junction geometries (`--geometry.remove`, `--roundabouts.guess`, `--junctions.join`, `--tls.guess-signals`).
2. **Boundary & Centroid Calculation**:
   Parses `convBoundary` to extract physical width and height ($km^2$) and computes the urban midpoint $(X_{center}, Y_{center})$.
3. **NED & INI Synchronization**:
   - Updates canvas boundaries `@display("bgb=W,H")` in `Scenario.ned`.
   - Repositions the Road-Side Unit in `Scenario.ned` and updates `*.rsu[0].mobility.initialX` / `initialY` in `omnetpp.ini`.
4. **Random Trip Generation (`randomTrips.py`)**:
   Invokes SUMO's `randomTrips.py` to create valid origin-destination pairs.
5. **Shortest-Path Routing (`duarouter`)**:
   Computes valid Dijkstra paths across reachable road edges.
6. **Fleet Normalization**:
   Assigns contiguous integer IDs (`0, 1, 2, ... N-1`) and enforces simultaneous $t=0.00\text{s}$ departures.
7. **File Deployment**:
   Deploys `maps.net.xml`, `maps.rou.xml`, `maps.rou.all.xml`, and `maps.sumocfg` across both root and `vanet_aodv/`. The simulation is immediately runnable.

---

## 5. SUMO & TraCI Configurations

### A. SUMO Master Configuration: `maps.sumocfg`
```xml
<configuration>
    <input>
        <net-file value="maps.net.xml"/>
        <route-files value="maps.rou.xml"/>
    </input>
    <time>
        <begin value="0"/>
        <end value="1000"/>
        <step-length value="0.1"/>
    </time>
</configuration>
```
- **`step-length = 0.1`**: Synchronizes SUMO physics at $100\text{ ms}$ steps, matching OMNeT++'s TraCI update interval.

### B. TraCI Launcher: `vanet_aodv/maps.launchd.xml`
```xml
<launch>
    <copy file="maps.net.xml"/>
    <copy file="maps.rou.xml"/>
    <copy file="maps.sumocfg"/>
</launch>
```
Instructs `veins_launchd` to mirror network and route definitions into its execution sandbox.
