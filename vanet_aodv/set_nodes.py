#!/usr/bin/env python3
"""
Script Sederhana Pengubah Jumlah Node Mobil
Penggunaan:
    python3 set_nodes.py 10    # Mengubah maps.rou.xml menjadi 10 mobil
    python3 set_nodes.py 25    # Mengubah maps.rou.xml menjadi 25 mobil
    python3 set_nodes.py 50    # Mengubah maps.rou.xml menjadi 50 mobil
"""

import sys
import os
import xml.etree.ElementTree as ET

def set_nodes(n):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    master_file = os.path.join(base_dir, "maps.rou.all.xml")
    target_file = os.path.join(base_dir, "maps.rou.xml")

    if not os.path.exists(master_file):
        print(f"Error: Master file {master_file} tidak ditemukan!")
        sys.exit(1)

    tree = ET.parse(master_file)
    root = tree.getroot()
    vehicles = root.findall("vehicle")

    if n > len(vehicles):
        print(f"Peringatan: Jumlah maksimum mobil adalah {len(vehicles)}. Menggunakan {len(vehicles)}.")
        n = len(vehicles)
    elif n < 2:
        print("Error: Minimal harus 2 mobil untuk komunikasi VANET!")
        sys.exit(1)

    new_root = ET.Element("routes")
    for k, v in root.attrib.items():
        new_root.attrib[k] = v

    for v in vehicles[:n]:
        # Pastikan seluruh mobil langsung berangkat di detik 0
        v.set("depart", "0.00")
        v.set("departLane", "best")
        v.set("departSpeed", "max")
        new_root.append(v)

    new_tree = ET.ElementTree(new_root)
    ET.indent(new_tree, space="    ", level=0)
    new_tree.write(target_file, encoding="utf-8", xml_declaration=True)

    print(f"[✓] Berhasil mengupdate maps.rou.xml menjadi {n} mobil (semua depart di t=0.00s).")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Penggunaan: python3 set_nodes.py <jumlah_mobil>")
        print("Contoh    : python3 set_nodes.py 20")
        sys.exit(1)
    try:
        count = int(sys.argv[1])
        set_nodes(count)
    except ValueError:
        print("Error: Masukkan angka bulat!")
        sys.exit(1)
