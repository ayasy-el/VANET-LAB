#!/usr/bin/env python3
"""
==============================================================================
set_nodes.py - Dynamic Fleet Density, Speed, and Acceleration Scaler for VANET
==============================================================================

Adjusts active vehicle count and kinematics (speed, acceleration, deceleration)
in SUMO route files (`maps.rou.xml`) across all workspaces (vanet_aodv, vanet_gpsr).

Usage:
    ./set_nodes.py <VEHICLE_COUNT> [OPTIONS]

Examples:
    # 1. Scale fleet density only (default kinematics):
    ./set_nodes.py 20

    # 2. Slow urban traffic (30 km/h, gentle acceleration 1.2 m/s²):
    ./set_nodes.py 20 --speed 30 --accel 1.2 --decel 2.5

    # 3. High-speed highway traffic (100 km/h, aggressive acceleration 3.5 m/s²):
    ./set_nodes.py 20 --speed 100 --accel 3.5 --decel 4.5

    # 4. Moderate city traffic departing from a dead stop (0 km/h):
    ./set_nodes.py 25 --speed 50 --accel 2.0 --depart-speed 0
"""

import sys
import os
import argparse
import xml.etree.ElementTree as ET

def find_master_file(current_dir, root_dir):
    """Finds maps.rou.all.xml from candidate search paths."""
    candidates = [
        os.path.join(current_dir, "maps.rou.all.xml"),
        os.path.join(root_dir, "maps.rou.all.xml"),
        os.path.join(root_dir, "vanet_aodv", "maps.rou.all.xml"),
        os.path.join(root_dir, "vanet_gpsr", "maps.rou.all.xml")
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None

def set_fleet_parameters(args):
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Identify project root
    if os.path.exists(os.path.join(current_dir, "vanet_aodv")):
        root_dir = current_dir
    elif os.path.basename(current_dir) in ["vanet_aodv", "vanet_gpsr"]:
        root_dir = os.path.abspath(os.path.join(current_dir, ".."))
    else:
        root_dir = current_dir

    master_file = find_master_file(current_dir, root_dir)
    if not master_file:
        print("[!] Error: Master route pool 'maps.rou.all.xml' not found in workspace!")
        sys.exit(1)

    tree = ET.parse(master_file)
    root = tree.getroot()
    vehicles = root.findall("vehicle")

    n = args.count
    if n > len(vehicles):
        print(f"[!] Warning: Maximum available vehicles is {len(vehicles)}. Using {len(vehicles)}.")
        n = len(vehicles)
    elif n < 2:
        print("[!] Error: Minimum of 2 vehicles required for VANET communications!")
        sys.exit(1)

    new_root = ET.Element("routes")
    for k, v in root.attrib.items():
        new_root.attrib[k] = v

    # Build <vType> with kinematic attributes
    vtype_attribs = {
        "id": "veh_passenger",
        "vClass": "passenger"
    }

    max_speed_ms = None
    if args.speed is not None:
        if args.speed <= 0:
            print("[!] Error: Speed must be greater than 0 km/h!")
            sys.exit(1)
        max_speed_ms = round(args.speed / 3.6, 2)
        vtype_attribs["maxSpeed"] = f"{max_speed_ms:.2f}"

    if args.accel is not None:
        if args.accel <= 0:
            print("[!] Error: Acceleration must be greater than 0 m/s²!")
            sys.exit(1)
        vtype_attribs["accel"] = f"{args.accel:.2f}"

    if args.decel is not None:
        if args.decel <= 0:
            print("[!] Error: Deceleration must be greater than 0 m/s²!")
            sys.exit(1)
        vtype_attribs["decel"] = f"{args.decel:.2f}"

    if args.emergency_decel is not None:
        vtype_attribs["emergencyDecel"] = f"{args.emergency_decel:.2f}"
    elif args.decel is not None:
        vtype_attribs["emergencyDecel"] = f"{max(9.0, args.decel * 2):.2f}"

    new_root.append(ET.Element("vType", vtype_attribs))

    # Add active vehicles
    depart_speed_str = str(args.depart_speed)
    for v in vehicles[:n]:
        v.set("depart", "0.00")
        v.set("departLane", "best")
        v.set("departSpeed", depart_speed_str)
        new_root.append(v)

    new_tree = ET.ElementTree(new_root)
    ET.indent(new_tree, space="    ", level=0)

    # Synchronize to all existing workspace target files
    targets = [
        os.path.join(root_dir, "maps.rou.xml"),
        os.path.join(root_dir, "vanet_aodv", "maps.rou.xml"),
        os.path.join(root_dir, "vanet_gpsr", "maps.rou.xml")
    ]

    updated_targets = []
    for target in targets:
        target_dir = os.path.dirname(target)
        if os.path.exists(target_dir):
            new_tree.write(target, encoding="utf-8", xml_declaration=True)
            updated_targets.append(os.path.relpath(target, current_dir))

    # Display clear summary
    print("==========================================================")
    print("  VANET FLEET DENSITY & KINEMATICS SCALER")
    print("==========================================================")
    print(f"  • Active Fleet       : {n} vehicles")
    if args.speed is not None:
        print(f"  • Max Speed          : {args.speed:.1f} km/h ({max_speed_ms:.2f} m/s)")
    else:
        print(f"  • Max Speed          : Default (Follows road speed limits)")
    if args.accel is not None:
        print(f"  • Acceleration       : {args.accel:.2f} m/s²")
    else:
        print(f"  • Acceleration       : Default (2.60 m/s²)")
    if args.decel is not None:
        print(f"  • Deceleration       : {args.decel:.2f} m/s²")
    else:
        print(f"  • Deceleration       : Default (4.50 m/s²)")
    print(f"  • Departure Speed    : {depart_speed_str}")
    print("----------------------------------------------------------")
    print("  [✓] Successfully updated maps.rou.xml across workspaces:")
    for t in updated_targets:
        print(f"      - {t}")
    print("==========================================================")

def main():
    parser = argparse.ArgumentParser(
        description="Dynamic Fleet Density, Speed, and Acceleration Scaler for VANET simulations (SUMO + OMNeT++)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  ./set_nodes.py 20
  ./set_nodes.py 20 --speed 30 --accel 1.2 --decel 2.5
  ./set_nodes.py 20 --speed 100 --accel 3.5 --decel 4.5
  ./set_nodes.py 25 --speed 50 --accel 2.0 --depart-speed 0
"""
    )
    parser.add_argument("count", type=int, help="Number of active vehicles deployed (minimum: 2)")
    parser.add_argument("--speed", "-s", type=float, default=None, help="Maximum vehicle speed in km/h (e.g., 30, 60, 100)")
    parser.add_argument("--accel", "-a", type=float, default=None, help="Maximum acceleration in m/s² (e.g., 1.2, 2.6, 5.0)")
    parser.add_argument("--decel", "-d", type=float, default=None, help="Normal deceleration / braking in m/s² (e.g., 2.5, 4.5)")
    parser.add_argument("--emergency-decel", "-e", type=float, default=None, help="Emergency braking deceleration in m/s² (default: 9.0)")
    parser.add_argument("--depart-speed", default="max", help="Initial departure speed ('max', '0', or numeric m/s) (default: 'max')")

    args = parser.parse_args()
    set_fleet_parameters(args)

if __name__ == "__main__":
    main()
