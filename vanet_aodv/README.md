# 🚗 Workspace Simulasi VANET-AODV (OMNeT++)

Workspace ini memuat seluruh kode sumber topologi jaringan (*NED files*), skenario simulasi (*omnetpp.ini*), file konfigurasi mobilitas SUMO, serta skrip otomasi eksekusi simulasi routing **AODV (RFC 3561)** pada lingkungan **VANET**.

> 📖 **Dokumentasi Lengkap**: Panduan arsitektur komprehensif, spesifikasi fisik IEEE 802.11p, dan analisis data tersedia di [Root README](../README.md) dan [Wiki Proyek](../wiki/Home.md).

---

## 1. Topologi Jaringan & Modul NED

Topologi jaringan dikembangkan modular menggunakan modul-modul berikut:

- **`Scenario.ned`**: Topologi tingkat atas (*Network Scenario*). Mengintegrasikan modul `radioMedium` (IEEE 802.11p DSRC 5.9 GHz), `manager` (`VeinsInetManager`), `visualizer` (`IntegratedVisualizer`), `roadsCanvasVisualizer`, armada kendaraan bergerak `node[*]`, serta node infrastruktur `rsu[*]`.
- **`VeinsAodvCar.ned`**: Modul kendaraan bergerak yang memperluas (*extends*) `inet.node.aodv.AodvRouter`. Dilengkapi kartu jaringan nirkabel IEEE 802.11p dan adaptor mobilitas TraCI `VeinsInetMobility`.
- **`VeinsAodvRSU.ned`**: Modul Road-Side Unit statis berbasis `AodvRouter` yang ditempatkan di persimpangan jalan perkotaan untuk skenario V2I.

---

## 2. Skenario Studi Kasus (`omnetpp.ini`)

Seluruh skenario pengujian mewarisi konfigurasi global `[General]` (termasuk visualizer multi-layer, frekuensi DSRC 5.9 GHz, dan subnetting 10.0.0.0/8):

| Skenario | Paradigma Komunikasi | Stack Aplikasi | Deskripsi Aliran Data & Evaluasi |
|---|:---:|:---:|---|
| **`AODV_V2V_Ping`** | V2V (1 ke 1) | ICMP (`PingApp`) | Mobil 0 mengirim ping berkala (56 B) ke Mobil 1 sambil melaju. Menguji *Round-Trip Time* (RTT), pembentukan rute simetris, dan latensi *route discovery*. |
| **`AODV_V2V_UDP`** | V2V (1 ke 1) | UDP (`UdpBasicApp`) | Transmisi aliran data kontinu CBR (512 B) dari Mobil 0 ke Mobil 1 (`UdpSink`). Mengukur *Throughput* dan *Packet Delivery Ratio* (PDR). |
| **`AODV_V2I_RSU`** | V2I ($N$ ke 1) | UDP Telemetry | Seluruh armada mobil mengirimkan status telemetri (256 B) secara berkala ke 1 RSU statis di persimpangan. Menguji agregasi multi-hop dan skalabilitas jaringan. |
| **`AODV_HelloMessages`** | V2V (1 ke 1) | UDP + HELLO RFC 3561 | Evaluasi AODV dengan pengaktifan pesan siaran periodik HELLO ($1\text{s}$) untuk membandingkan *routing overhead* terhadap umpan balik layer MAC. |

---

## 3. Impor Peta Baru (`import_map.sh`) & Manajemen Kepadatan

### A. Impor Peta Baru Langsung dari File `.osm`
Untuk mengganti seluruh peta jalan dengan data OpenStreetMap baru, jalankan:

```bash
# Dari root atau folder vanet_aodv:
./import_map.sh <BERKAS_OSM> [JUMLAH_MOBIL]

# Contoh:
./import_map.sh kota_baru.osm 25
```
Skrip ini mengonversi `.osm` ke SUMO via `netconvert --proj.utm`, menghitung luas dan pusat kota, otomatis memperbarui posisi RSU di `omnetpp.ini` dan kanvas di `Scenario.ned`, lalu membuat rute valid serentak di $t=0\text{s}$.

---

### B. Mengubah Kepadatan Kendaraan pada Peta Aktif (`set_nodes.py`)
Skrip **`set_nodes.py`** digunakan untuk mengatur jumlah kendaraan yang aktif melaju di peta jalan yang sedang terpasang tanpa membuat ulang peta:

```bash
./set_nodes.py <JUMLAH_KENDARAAN>
```

### Contoh Penggunaan:
```bash
# Menetapkan kepadatan rendah (10 kendaraan):
./set_nodes.py 10

# Menetapkan kepadatan sedang (25 kendaraan):
./set_nodes.py 25

# Menetapkan kepadatan tinggi (50 kendaraan):
./set_nodes.py 50
```

### Karakteristik Teknis:
- Mengekstrak rute dari master `maps.rou.all.xml` (menyimpan 91 rute kendaraan unik) dan memperbarui `maps.rou.xml`.
- Memaksa seluruh kendaraan untuk berangkat serentak pada $t = 0{,}00\text{ s}$ (`depart="0.00"`).
- Mengatur akselerasi optimal instan (`departSpeed="max"`) dan penempatan lajur terbaik (`departLane="best"`).

---

## 4. Panduan Eksekusi Simulasi

### Mode A: Terminal Headless (`run_cmd.sh`)
Dirancang untuk eksekusi otomatis tanpa antarmuka grafis (ideal untuk *batch benchmarking*):

```bash
# Sintaks: ./run_cmd.sh <NAMA_SKENARIO> [DURASI]

./run_cmd.sh AODV_V2V_Ping 30s
./run_cmd.sh AODV_V2V_UDP 60s
./run_cmd.sh AODV_V2I_RSU 60s
./run_cmd.sh AODV_HelloMessages 60s
```

*Skrip ini secara otomatis memverifikasi dan menyalakan daemon `veins_launchd` di latar belakang, menjalankan simulasi, serta mematikan daemon secara aman saat selesai.*

---

### Mode B: Visual Grafis Interaktif (`run_gui.sh`)
Membuka antarmuka interaktif Qtenv lengkap dengan visualisasi jangkauan radio fisik, koneksi data-link MAC 1-hop, dan rute multi-hop AODV:

```bash
# Menjalankan skenario default (AODV_V2V_Ping):
./run_gui.sh

# Menjalankan skenario tertentu secara eksplisit:
./run_gui.sh AODV_V2V_UDP
./run_gui.sh AODV_V2I_RSU
./run_gui.sh AODV_HelloMessages
```

---

### Mode C: Menjalankan via OMNeT++ IDE
1. Jalankan daemon TraCI di terminal:
   ```bash
   ./run_veins_launchd.sh start
   ```
2. Buka OMNeT++ IDE, klik kanan berkas `omnetpp.ini` > **Run As** > **OMNeT++ Simulation**.
3. Pilih skenario target (misal: `AODV_V2V_Ping`) lalu klik **OK**.
4. Hentikan daemon setelah pengujian selesai:
   ```bash
   ./run_veins_launchd.sh stop
   ```

---

## 5. Struktur Direktori Workspace

```text
vanet_aodv/
├── .project                # Metadata proyek OMNeT++ IDE
├── .nedfolders             # Konfigurasi path modul NED
├── package.ned             # Deklarasi package vanet_aodv
├── Scenario.ned            # Topologi utama jaringan
├── VeinsAodvCar.ned        # Modul node kendaraan bergerak
├── VeinsAodvRSU.ned        # Modul Road-Side Unit statis
├── omnetpp.ini             # Konfigurasi simulasi & skenario benchmark
├── empty.xml               # Lingkungan fisik tanpa rintangan buatan
├── maps.net.xml            # Jaringan jalan SUMO (proyeksi UTM kartesius)
├── maps.rou.xml            # Rute kendaraan aktif yang disimulasikan
├── maps.rou.all.xml        # Master pool rute 91 kendaraan SUMO
├── maps.sumocfg            # Berkas konfigurasi utama simulasi SUMO
├── maps.launchd.xml        # Konfigurasi TraCI launchd untuk SUMO
├── set_nodes.py            # Utilitas CLI pengubah skala jumlah kendaraan
├── run_cmd.sh              # Skrip runner mode terminal (Cmdenv)
├── run_gui.sh              # Skrip runner mode grafis (Qtenv)
├── run_veins_launchd.sh    # Skrip kontrol daemon veins_launchd
├── results/                # Output rekaman statistik (*.sca, *.vec)
└── README.md               # Dokumentasi teknis workspace ini
```
