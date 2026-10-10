#!/usr/bin/env python3
"""
Dynamic Fleet Density Scaler for VANET-AODV
Usage:
    python3 set_nodes.py 10    # Set active fleet to 10 vehicles
    python3 set_nodes.py 25    # Set active fleet to 25 vehicles
    python3 set_nodes.py 50    # Set active fleet to 50 vehicles
"""

import sys
import os
import xml.etree.ElementTree as ET

def set_nodes(n):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    master_file = os.path.join(base_dir, "maps.rou.all.xml")
    target_file = os.path.join(base_dir, "maps.rou.xml")

    if not os.path.exists(master_file):
        print(f"Error: Master route pool '{master_file}' not found!")
        sys.exit(1)

    tree = ET.parse(master_file)
    root = tree.getroot()
    vehicles = root.findall("vehicle")

    if n > len(vehicles):
        print(f"Warning: Maximum available vehicles is {len(vehicles)}. Using {len(vehicles)}.")
        n = len(vehicles)
    elif n < 2:
        print("Error: Minimum of 2 vehicles required for VANET communications!")
        sys.exit(1)

    new_root = ET.Element("routes")
    for k, v in root.attrib.items():
        new_root.attrib[k] = v

    for v in vehicles[:n]:
        v.set("depart", "0.00")
        v.set("departLane", "best")
        v.set("departSpeed", "max")
        new_root.append(v)

    new_tree = ET.ElementTree(new_root)
    ET.indent(new_tree, space="    ", level=0)
    new_tree.write(target_file, encoding="utf-8", xml_declaration=True)

    print(f"[✓] Successfully updated maps.rou.xml to {n} vehicles (all departing at t=0.00s).")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 set_nodes.py <vehicle_count>")
        print("Example: python3 set_nodes.py 20")
        sys.exit(1)
    try:
        count = int(sys.argv[1])
        set_nodes(count)
    except ValueError:
        print("Error: Please provide a valid integer!")
        sys.exit(1)
