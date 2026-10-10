#!/usr/bin/env python3
"""
==============================================================================
import_map.py - Otomasi Konversi Peta .osm ke Lingkungan Simulasi VANET-AODV
==============================================================================

Alur Kerja:
1. Mengonversi berkas OpenStreetMap (.osm) menjadi jaringan jalan SUMO (maps.net.xml)
   menggunakan netconvert dengan proyeksi UTM kartesius.
2. Mengekstrak koordinat batas peta (convBoundary), menghitung dimensi & luas,
   serta menentukan titik koordinat tengah kota untuk penempatan Road-Side Unit (RSU).
3. Membangkitkan rute perjalanan kendaraan acak menggunakan randomTrips.py dan duarouter.
4. Memformat seluruh armada kendaraan agar langsung berangkat serentak pada t=0.00s
   (depart="0.00", departLane="best", departSpeed="max") dengan penomoran indeks
   berurutan (0, 1, 2, ... N-1).
5. Menyinkronkan konfigurasi ke:
   - maps.net.xml, maps.rou.xml, maps.rou.all.xml, maps.sumocfg
   - vanet_aodv/Scenario.ned (ukuran kanvas @display bgb dan posisi RSU)
   - vanet_aodv/omnetpp.ini (koordinat initialX dan initialY modul RSU)
6. Menghasilkan topologi yang langsung siap dieksekusi oleh OMNeT++ (Qtenv/Cmdenv).

Penggunaan:
    ./import_map.py [path_ke_file.osm] [--cars JUMLAH_MOBIL] [--trips JUMLAH_TRIP]

Contoh:
    ./import_map.py map.osm
    ./import_map.py surabaya_barat.osm --cars 30
    ./import_map.py /tmp/bandung.osm --cars 50 --trips 200
"""

import sys
import os
import shutil
import subprocess
import argparse
import xml.etree.ElementTree as ET
import re

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
VANET_DIR = os.path.join(ROOT_DIR, "vanet_aodv")

def locate_tool(name):
    """Mencari path binary pada PATH sistem."""
    path = shutil.which(name)
    if path:
        return path
    venv_bin = os.path.join(ROOT_DIR, "../omnetpp-6.4.0/.venv/bin", name)
    if os.path.exists(venv_bin):
        return venv_bin
    return None

def locate_random_trips():
    """Mencari lokasi skrip randomTrips.py SUMO."""
    candidates = []
    if "SUMO_HOME" in os.environ:
        candidates.append(os.path.join(os.environ["SUMO_HOME"], "tools", "randomTrips.py"))
    try:
        import sumo
        sumo_dir = os.path.dirname(sumo.__file__)
        candidates.append(os.path.join(sumo_dir, "tools", "randomTrips.py"))
    except ImportError:
        pass

    # Jalur virtual environment proyek
    candidates.append(os.path.join(ROOT_DIR, "../omnetpp-6.4.0/.venv/lib/python3.14/site-packages/sumo/tools/randomTrips.py"))
    candidates.append("/usr/share/sumo/tools/randomTrips.py")
    candidates.append("/usr/lib/sumo/tools/randomTrips.py")

    which_path = shutil.which("randomTrips.py")
    if which_path:
        candidates.append(which_path)

    for cand in candidates:
        if cand and os.path.exists(cand):
            return cand
    return None

def run_command(cmd, desc):
    """Menjalankan perintah eksternal dengan penanganan error."""
    print(f"[*] {desc}...")
    try:
        res = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return res
    except subprocess.CalledProcessError as e:
        print(f"[!] ERROR saat {desc}:")
        print(e.stderr or e.stdout)
        sys.exit(1)

def parse_boundary(net_file):
    """Mengekstrak convBoundary dari maps.net.xml."""
    tree = ET.parse(net_file)
    root = tree.getroot()
    location = root.find("location")
    if location is None or "convBoundary" not in location.attrib:
        raise ValueError(f"Atribut convBoundary tidak ditemukan pada {net_file}!")

    conv = location.attrib["convBoundary"]
    parts = [float(x.strip()) for x in conv.split(",")]
    min_x, min_y, max_x, max_y = parts[0], parts[1], parts[2], parts[3]
    return min_x, min_y, max_x, max_y

def format_routes(input_rou_file, output_all_file, output_active_file, num_active_cars):
    """Memfilter dan menormalisasi rute kendaraan agar berangkat di t=0s."""
    tree = ET.parse(input_rou_file)
    root = tree.getroot()
    raw_vehicles = root.findall("vehicle")

    valid_vehicles = []
    for v in raw_vehicles:
        route = v.find("route")
        if route is not None and route.attrib.get("edges"):
            valid_vehicles.append(v)

    if not valid_vehicles:
        print("[!] ERROR: Tidak ada rute kendaraan valid yang berhasil digenerate oleh duarouter!")
        sys.exit(1)

    print(f"[✓] Berhasil menemukan {len(valid_vehicles)} rute valid pada jaringan jalan.")

    # Buat XML Master Pool (maps.rou.all.xml)
    all_root = ET.Element("routes")
    for k, v in root.attrib.items():
        all_root.attrib[k] = v

    for idx, v in enumerate(valid_vehicles):
        v.set("id", str(idx))
        v.set("type", "veh_passenger")
        v.set("depart", "0.00")
        v.set("departLane", "best")
        v.set("departSpeed", "max")
        all_root.append(v)

    all_tree = ET.ElementTree(all_root)
    ET.indent(all_tree, space="    ", level=0)
    all_tree.write(output_all_file, encoding="utf-8", xml_declaration=True)

    # Buat XML Aktif (maps.rou.xml)
    active_count = min(num_active_cars, len(valid_vehicles))
    active_root = ET.Element("routes")
    for k, v in root.attrib.items():
        active_root.attrib[k] = v

    for v in all_root.findall("vehicle")[:active_count]:
        active_root.append(v)

    active_tree = ET.ElementTree(active_root)
    ET.indent(active_tree, space="    ", level=0)
    active_tree.write(output_active_file, encoding="utf-8", xml_declaration=True)

    return len(valid_vehicles), active_count

def update_ned_and_ini(max_x, max_y, rsu_x, rsu_y):
    """Memperbarui kanvas Scenario.ned dan posisi RSU di omnetpp.ini."""
    canvas_w = max(2500, int(max_x * 1.15))
    canvas_h = max(2000, int(max_y * 1.15))
    rsu_x_int = int(rsu_x)
    rsu_y_int = int(rsu_y)

    ned_file = os.path.join(VANET_DIR, "Scenario.ned")
    if os.path.exists(ned_file):
        with open(ned_file, "r") as f:
            ned_content = f.read()

        # Update bgb=canvas_w,canvas_h
        ned_content = re.sub(
            r'@display\("bgb=\d+,\d+"\);',
            f'@display("bgb={canvas_w},{canvas_h}");',
            ned_content
        )
        # Update RSU display position
        ned_content = re.sub(
            r'rsu\[numRsu\]:\s*VeinsAodvRSU\s*\{[^}]*@display\("p=\d+,\d+"\);',
            f'rsu[numRsu]: VeinsAodvRSU {{\n            @display("p={rsu_x_int},{rsu_y_int}");',
            ned_content
        )
        with open(ned_file, "w") as f:
            f.write(ned_content)
        print(f"[✓] Memperbarui Scenario.ned: Kanvas ({canvas_w}x{canvas_h}), RSU display ({rsu_x_int}, {rsu_y_int}).")

    ini_file = os.path.join(VANET_DIR, "omnetpp.ini")
    if os.path.exists(ini_file):
        with open(ini_file, "r") as f:
            ini_content = f.read()

        ini_content = re.sub(
            r'\*\.rsu\[0\]\.mobility\.initialX\s*=\s*\d+m',
            f'*.rsu[0].mobility.initialX = {rsu_x_int}m',
            ini_content
        )
        ini_content = re.sub(
            r'\*\.rsu\[0\]\.mobility\.initialY\s*=\s*\d+m',
            f'*.rsu[0].mobility.initialY = {rsu_y_int}m',
            ini_content
        )
        with open(ini_file, "w") as f:
            f.write(ini_content)
        print(f"[✓] Memperbarui omnetpp.ini: Posisi RSU koordinat ({rsu_x_int}m, {rsu_y_int}m).")

def generate_sumocfg(net_filename, rou_filename, sumocfg_path):
    """Membuat berkas maps.sumocfg standar."""
    content = f"""<?xml version="1.0" encoding="UTF-8"?>
<configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/sumoConfiguration.xsd">
    <input>
        <net-file value="{net_filename}"/>
        <route-files value="{rou_filename}"/>
    </input>
    <time>
        <begin value="0"/>
        <end value="1000"/>
        <step-length value="0.1"/>
    </time>
</configuration>
"""
    with open(sumocfg_path, "w") as f:
        f.write(content)

def main():
    parser = argparse.ArgumentParser(description="Konversi Peta .osm Menjadi Lingkungan Simulasi VANET Siap Pakai")
    parser.add_argument("osm_file", nargs="?", default="map.osm", help="Path berkas .osm sumber (default: map.osm)")
    parser.add_argument("--cars", type=int, default=20, help="Jumlah mobil aktif yang melaju (default: 20)")
    parser.add_argument("--trips", type=int, default=150, help="Jumlah kandidat trip acak yang digenerate (default: 150)")
    args = parser.parse_args()

    osm_path = os.path.abspath(args.osm_file)
    if not os.path.exists(osm_path):
        print(f"[!] ERROR: Berkas peta '{osm_path}' tidak ditemukan!")
        sys.exit(1)

    print("==================================================================")
    print("  VANET-AODV MAP IMPORT & PIPELINE GENERATOR")
    print("==================================================================")
    print(f" Peta Sumber   : {osm_path}")
    print(f" Mobil Aktif   : {args.cars}")
    print(f" Target Trips  : {args.trips}")
    print("------------------------------------------------------------------")

    # 1. Cek Tools
    netconvert_bin = locate_tool("netconvert")
    duarouter_bin = locate_tool("duarouter")
    random_trips_py = locate_random_trips()

    if not netconvert_bin:
        print("[!] ERROR: 'netconvert' tidak ditemukan di PATH!")
        sys.exit(1)
    if not duarouter_bin:
        print("[!] ERROR: 'duarouter' tidak ditemukan di PATH!")
        sys.exit(1)
    if not random_trips_py:
        print("[!] ERROR: 'randomTrips.py' tidak ditemukan!")
        sys.exit(1)

    tmp_dir = "/tmp/vanet_map_build"
    os.makedirs(tmp_dir, exist_ok=True)

    tmp_net = os.path.join(tmp_dir, "maps.net.xml")
    tmp_trips = os.path.join(tmp_dir, "trips.trips.xml")
    tmp_rou = os.path.join(tmp_dir, "duarouter_out.rou.xml")
    tmp_rou_all = os.path.join(tmp_dir, "maps.rou.all.xml")
    tmp_rou_active = os.path.join(tmp_dir, "maps.rou.xml")
    tmp_sumocfg = os.path.join(tmp_dir, "maps.sumocfg")

    # 2. Jalankan netconvert
    cmd_netconvert = [
        netconvert_bin,
        "--osm-files", osm_path,
        "-o", tmp_net,
        "--geometry.remove",
        "--roundabouts.guess",
        "--ramps.guess",
        "--junctions.join",
        "--tls.guess-signals",
        "--tls.discard-simple",
        "--proj.utm"
    ]
    run_command(cmd_netconvert, "Mengonversi .osm ke SUMO net (netconvert)")

    # 3. Baca Dimensi Bounding Box
    min_x, min_y, max_x, max_y = parse_boundary(tmp_net)
    width = max_x - min_x
    height = max_y - min_y
    rsu_x = (min_x + max_x) / 2.0
    rsu_y = (min_y + max_y) / 2.0
    area_km2 = (width * height) / 1_000_000.0

    print(f"[✓] Batas Peta (UTM): [0.00, 0.00] s/d [{max_x:.2f}, {max_y:.2f}]")
    print(f"    - Lebar (X)     : {width:.2f} m ({width/1000:.2f} km)")
    print(f"    - Tinggi (Y)    : {height:.2f} m ({height/1000:.2f} km)")
    print(f"    - Luas Wilayah  : {area_km2:.2f} km²")
    print(f"    - Pusat RSU     : ({rsu_x:.2f}m, {rsu_y:.2f}m)")

    # 4. Bangkitkan Random Trips
    cmd_trips = [
        sys.executable,
        random_trips_py,
        "-n", tmp_net,
        "-o", tmp_trips,
        "-e", str(args.trips),
        "-l",
        "--validate"
    ]
    run_command(cmd_trips, f"Membangkitkan {args.trips} rute trip kendaraan acak (randomTrips.py)")

    # 5. Jalankan duarouter
    cmd_duarouter = [
        duarouter_bin,
        "-n", tmp_net,
        "--route-files", tmp_trips,
        "-o", tmp_rou,
        "--ignore-errors"
    ]
    run_command(cmd_duarouter, "Menghitung jalur rute terpendek di jalan raya (duarouter)")

    # 6. Format Rute (depart=0.00s, consecutive IDs)
    total_valid, active_cars = format_routes(tmp_rou, tmp_rou_all, tmp_rou_active, args.cars)

    # 7. Generate maps.sumocfg
    generate_sumocfg("maps.net.xml", "maps.rou.xml", tmp_sumocfg)

    # 8. Sinkronkan ke Root dan Direktori vanet_aodv
    target_dirs = [ROOT_DIR, VANET_DIR]
    files_to_sync = [
        (tmp_net, "maps.net.xml"),
        (tmp_trips, "trips.trips.xml"),
        (tmp_rou_all, "maps.rou.all.xml"),
        (tmp_rou_active, "maps.rou.xml"),
        (tmp_sumocfg, "maps.sumocfg")
    ]

    for d in target_dirs:
        for src_path, fname in files_to_sync:
            dest_path = os.path.join(d, fname)
            shutil.copyfile(src_path, dest_path)

    # Simpan juga peta asli ke direktori root jika berbeda nama
    dest_osm = os.path.join(ROOT_DIR, "map.osm")
    if osm_path != dest_osm:
        shutil.copyfile(osm_path, dest_osm)

    # 9. Update Scenario.ned dan omnetpp.ini
    update_ned_and_ini(max_x, max_y, rsu_x, rsu_y)

    print("==================================================================")
    print("  [✓] PROSES IMPORT PETA BERHASIL & SELESAI!")
    print("==================================================================")
    print(f" • Total Rute Tersedia : {total_valid} mobil")
    print(f" • Mobil Aktif (t=0s)  : {active_cars} mobil")
    print(f" • Posisi RSU Otomatis : ({int(rsu_x)}m, {int(rsu_y)}m)")
    print(f" • Ukuran Kanvas OMNeT : {max(2500, int(max_x * 1.15))} x {max(2000, int(max_y * 1.15))}")
    print("")
    print(" Sekarang simulasi langsung siap dijalankan:")
    print("   1. Mode Grafis GUI   : cd vanet_aodv && ./run_gui.sh")
    print("   2. Mode Terminal     : cd vanet_aodv && ./run_cmd.sh AODV_V2V_Ping 30s")
    print("==================================================================")

if __name__ == "__main__":
    main()
