# 🛠️ Getting Started & Troubleshooting

This document provides step-by-step execution instructions and a troubleshooting matrix for resolving common simulation errors.

---

## 1. Environment Setup & Verification

Before running simulations, ensure your shell has loaded the OMNeT++, INET, and SUMO environment variables:

```bash
# From repository root:
cd /home/ayasy/Documents/Kuliah/Semester_6/VANET/VANET-LAB

# Source environment variables (PATH and LD_LIBRARY_PATH):
source ../setenv
```

### Tool Verification:
```bash
# 1. Verify OMNeT++ runner:
opp_run -v

# 2. Verify SUMO traffic simulator binaries:
which sumo
which sumo-gui

# 3. Verify Python version:
python3 --version
```

---

## 2. Simulation Execution Modes

---

### Mode A: Interactive Graphical Mode (Qtenv + SUMO-GUI)
Recommended for visual inspections, live demonstrations, and verifying packet routing flows.

#### Step 1: Launch TraCI Daemon
In your first terminal:
```bash
./run_sumo_launchd.sh
```
*Validates the `sumo-gui` binary and begins listening for connections on TCP port 9999.*

#### Step 2: Launch OMNeT++ Visualizer
In a second terminal:
```bash
cd vanet_aodv

# Launch default scenario (AODV_V2V_Ping):
./run_gui.sh

# Or launch other scenarios:
./run_gui.sh AODV_V2V_UDP
./run_gui.sh AODV_V2I_RSU
./run_gui.sh AODV_HelloMessages
```

Inside the Qtenv interface:
1. Click **Set Up Network**.
2. Click **Run (F5)** or **Fast (F6)** to start the simulation.

---

### Mode B: Headless Batch Mode (Cmdenv)
Recommended for long-running benchmarks, parameter sweeps, or running on remote servers without an X11 display:

```bash
cd vanet_aodv

# Command format:
# ./run_cmd.sh <SCENARIO_NAME> [SIMULATION_DURATION]

# 1. Run Ping benchmark for 30 seconds:
./run_cmd.sh AODV_V2V_Ping 30s

# 2. Run UDP streaming for 60 seconds:
./run_cmd.sh AODV_V2V_UDP 60s

# 3. Run RSU telemetry for 100 seconds:
./run_cmd.sh AODV_V2I_RSU 100s
```

*The `run_cmd.sh` script automatically spawns `veins_launchd` in the background if it is not already running, and terminates it safely upon completion.*

---

## 3. Troubleshooting Matrix

<div align="center">

| Error Message / Symptom | Potential Root Cause | Resolution |
|---|---|---|
| **`Connection refused on port 9999`** | `veins_launchd` is not running or crashed before OMNeT++ connected. | Start `./run_sumo_launchd.sh` in a separate terminal before launching OMNeT++. |
| **`Address already in use: 9999`** | An orphaned `veins_launchd` or SUMO process is still bound to the port. | Terminate the process: `fuser -k 9999/tcp` or `pkill -f veins_launchd`. |
| **`sumo-gui: cannot open display`** | Attempting to launch the GUI over SSH without X11 forwarding enabled. | Use headless mode (`run_cmd.sh`) or connect with `ssh -X`. |
| **`error while loading shared libraries: libINET.so`** | INET dynamic libraries are missing from `LD_LIBRARY_PATH`. | Run `source setenv` in the root workspace directory. |
| **`Vehicle ID '0' not known` / Cars stationary** | Route definitions are out of sync or contain staggered start times. | Run `./import_map.sh map.osm 20` or `./set_nodes.py 20` in `vanet_aodv/` to regenerate simultaneous $t=0\text{s}$ departures. |
| **Simulation runs slowly in Qtenv** | Animation rendering overhead is throttling event processing. | Switch Qtenv mode from **Run** to **Fast (F6)** or **Express (F7)**. |

</div>
