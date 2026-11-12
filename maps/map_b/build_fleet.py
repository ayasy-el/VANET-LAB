#!/usr/bin/env python3
"""
build_fleet.py - build a dense, single-departure fleet for Map B (map2).

The stock map2.rou.xml spreads 300 trips over 600 s, so only a couple of
vehicles are on the road during the first seconds of a 40 s simulation and the
vehicles are kilometres apart.  For a V2V scenario we need the whole fleet on
the road from the start and a source/destination pair that stays reachable.

This script rewrites a route file so that

  * the source vehicle departs first, the destination second and every other
    vehicle afterwards.  VeinsInetManager creates one OMNeT++ module per SUMO
    vehicle in the order the vehicles appear, therefore this staggered
    schedule makes the mapping deterministic:
        --src -> node[0], --dst -> node[1]
    (without it SUMO decides the insertion order and node[0]/node[1] end up on
    arbitrary vehicles, possibly kilometres apart),
  * the rest of the fleet departs together so that the map is populated for the
    whole measurement window.

Usage:
    python3 build_fleet.py --pool map2.pool.xml --out map2.rou.xml \
            --count 80 --src 29 --dst 66

The pool file is produced once from the original trip file:
    duarouter -n map2.net.xml --route-files map2.trips.xml \
              -o map2.pool.xml --ignore-errors true
"""

import argparse
import xml.etree.ElementTree as ET


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--pool", required=True, help="route pool produced by duarouter")
    p.add_argument("--out", required=True, help="route file to write")
    p.add_argument("--count", type=int, default=80, help="number of vehicles (default 80)")
    p.add_argument("--src", required=True, help="vehicle id used as OMNeT++ node[0]")
    p.add_argument("--dst", required=True, help="vehicle id used as OMNeT++ node[1]")
    p.add_argument("--speed", default="max", help="departSpeed (default max)")
    p.add_argument("--src-depart", default="0.00")
    p.add_argument("--dst-depart", default="0.20")
    p.add_argument("--other-depart", default="1.00")
    args = p.parse_args()

    root = ET.parse(args.pool).getroot()
    pool = {v.get("id"): v for v in root.findall("vehicle")}
    for vid in (args.src, args.dst):
        if vid not in pool:
            raise SystemExit(f"vehicle id {vid} not found in {args.pool}")

    order = [args.src, args.dst]
    order += [v.get("id") for v in root.findall("vehicle") if v.get("id") not in order]
    selected = order[: args.count]

    out = ET.Element("routes")
    ET.SubElement(out, "vType", {"id": "veh_passenger", "vClass": "passenger"})
    for vid in selected:
        veh = pool[vid]
        if vid == args.src:
            depart = args.src_depart
        elif vid == args.dst:
            depart = args.dst_depart
        else:
            depart = args.other_depart
        veh.set("depart", depart)
        veh.set("departLane", "best")
        veh.set("departSpeed", args.speed)
        out.append(veh)

    tree = ET.ElementTree(out)
    ET.indent(tree, space="    ", level=0)
    tree.write(args.out, encoding="utf-8", xml_declaration=True)
    print(f"wrote {len(selected)} vehicles to {args.out} "
          f"(node[0]={args.src} @{args.src_depart}s, node[1]={args.dst} @{args.dst_depart}s)")


if __name__ == "__main__":
    main()
