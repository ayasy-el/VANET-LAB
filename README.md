
<h1 align="center">🚗 VANET-AODV: Vehicular Ad-Hoc Network Simulation Testbed</h1>

<p align="center">
  <strong>Comprehensive Simulation Environment for Ad hoc On-Demand Distance Vector (RFC 3561) Routing over IEEE 802.11p WAVE/DSRC in Realistic Urban Mobility</strong>
</p>

<p align="center">
  <a href="https://omnetpp.org/"><img src="https://img.shields.io/badge/OMNeT%2B%2B-6.4.0-007acc.svg?style=flat-square&logo=c%2B%2B" alt="OMNeT++ 6.4.0"/></a>
  <a href="https://inet.omnetpp.org/"><img src="https://img.shields.io/badge/INET%20Framework-4.5.4-2b9348.svg?style=flat-square" alt="INET 4.5.4"/></a>
  <a href="https://veins.car2x.org/"><img src="https://img.shields.io/badge/Veins-5.3.1-orange.svg?style=flat-square" alt="Veins 5.3.1"/></a>
  <a href="https://eclipse.dev/sumo/"><img src="https://img.shields.io/badge/Eclipse%20SUMO-v1.x-555555.svg?style=flat-square" alt="Eclipse SUMO"/></a>
  <a href="https://datatracker.ietf.org/doc/html/rfc3561"><img src="https://img.shields.io/badge/Routing-AODV%20(RFC%203561)-blueviolet.svg?style=flat-square" alt="RFC 3561 AODV"/></a>
  <a href="https://standards.ieee.org/ieee/802.11p/3929/"><img src="https://img.shields.io/badge/PHY%2FMAC-IEEE%20802.11p%20(5.9%20GHz)-e63946.svg?style=flat-square" alt="IEEE 802.11p"/></a>
  <img src="https://img.shields.io/badge/Documentation-Wiki%20Available-success.svg?style=flat-square" alt="Wiki"/>
  <img src="https://img.shields.io/badge/License-Academic%20%2F%20MIT-informational.svg?style=flat-square" alt="License"/>
</p>

---

## 📑 Daftar Isi

- [📌 Overview](#-overview)
- [✨ Key Features](#-key-features)
- [🏗️ System Architecture](#️-system-architecture)
- [📡 Radio & Network Specifications](#-radio--network-specifications)
- [🧪 Simulation Scenarios & Benchmark Matrix](#-simulation-scenarios--benchmark-matrix)
- [🖥️ Multi-Layer Network Visualizer (Qtenv)](#️-multi-layer-network-visualizer-qtenv)
- [🗺️ Map Import & Traffic Scaling](#️-map-import--traffic-scaling)
- [🚀 Quick Start Guide](#-quick-start-guide)
- [📊 Evaluation Metrics & Output Files](#-evaluation-metrics--output-files)
- [📚 Project Wiki & Documentation](#-project-wiki--documentation)
- [📂 Directory Layout](#-directory-layout)
- [📄 References & License](#-references--license)

---

## 📌 Overview

**VANET-AODV** adalah *testbed* simulasi jaringan vehicular terpadu yang dirancang untuk menganalisis performa protokol routing reaktif **AODV (Ad hoc On-Demand Distance Vector, RFC 3561)** pada lalu lintas kendaraan perkotaan nyata. 

Simulator ini menggabungkan dinamika mobilitas lalu lintas mikroskopik dari **Eclipse SUMO** dengan pemodelan propagasi radio fisik dan stack jaringan lengkap dari **INET Framework** melalui jembatan **Veins TraCI**. Karena topologi jaringan perkotaan membentang seluas $2{,}08\text{ km} \times 1{,}74\text{ km}$ sementara jangkauan radio efektif kendaraan dibatasi $\approx 227\text{ meter}$, protokol AODV bertugas membangun dan memelihara rute *multi-hop relay* secara adaptif terhadap perubahan posisi kendaraan.

```
┌─────────────────┐             ┌─────────────────┐             ┌─────────────────┐
│ Vehicle 0 (Src) │             │ Vehicle Relay   │             │ Vehicle 1 (Dst) │
└────────┬────────┘             └────────┬────────┘             └────────┬────────┘
         │                               │                               │
         ├────── RREQ (Broadcast) ──────►│                               │
         │                               ├────── RREQ (Broadcast) ──────►│
         │                               │◄───── RREP (Unicast) ─────────┤
         │◄───── RREP (Unicast) ─────────┤                               │
         │                                                               │
         │══════ MULTI-HOP DATA STREAM (ICMP / UDP) ════════════════════►│
```

---

## ✨ Key Features

- **Quad-Simulator Coupling**: Sinkronisasi *real-time* dua arah antara OMNeT++ 6.4, INET 4.5.4, Veins 5.3.1, dan SUMO.
- **Full RFC 3561 Compliance**: Implementasi lengkap siklus hidup AODV (RREQ broadcast, RREP unicast, RERR route error, expanding ring search, dan pesan periodik HELLO).
- **Realistic DSRC/WAVE Physical Layer**: Transceiver IEEE 802.11p pada frekuensi $5{,}9\text{ GHz}$, *channel bandwidth* $10\text{ MHz}$, *thermal noise floor* $-110\text{ dBm}$, dan redaman *Free-Space Path Loss*.
- **Real-World Urban Geospatial Model**: Peta jalan nyata kawasan perkotaan Keputih seluas $\approx 3{,}61\text{ km}^2$ yang diekstraksi langsung dari OpenStreetMap.
- **Simultaneous Zero-Second Fleet Deployment**: Seluruh kendaraan aktif dan melaju serentak pada $t = 0{,}00\text{ s}$ dengan akselerasi optimal (`departSpeed="max"` dan `departLane="best"`).
- **V2V & V2I Evaluation Suite**: Menyediakan skenario terstandar untuk komunikasi antar-mobil (*Vehicle-to-Vehicle*) dan telemetri ke *Road-Side Unit* (*Vehicle-to-Infrastructure*).
- **Clean Multi-Layer Visualization**: Render visual visualizer Qtenv terkalibrasi yang memisahkan jangkauan radio fisik, koneksi MAC 1-hop, dan rute jaringan multi-hop.
- **Dynamic Node Scaler CLI**: Utilitas instan untuk mengubah skala kepadatan lalu lintas (10 hingga 91 kendaraan) tanpa perlu menyunting file XML manual.

---

## 🏗️ System Architecture

Arsitektur sistem dibangun di atas prinsip pemisahan domain lalu lintas dan domain telekomunikasi:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                   ECLIPSE SUMO                                         │
│       Microscopic Traffic Simulator: Car-Following, Collision Avoidance, Speeds        │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │ TraCI TCP Socket (Port 9999)
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              VEINS (veins_launchd Bridge)                              │
│       Coordinate System Translation & Dynamic OMNeT++ Vehicle Instantiation            │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │ VeinsInetMobility
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                  INET FRAMEWORK 4.5                                    │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│  │ APPLICATION LAYER   : PingApp (ICMP) / UdpBasicApp / UdpSink                     │  │
│  ├──────────────────────────────────────────────────────────────────────────────────┤  │
│  │ ROUTING LAYER       : AODV Routing Engine (RFC 3561 Dynamic Discovery & Repair)  │  │
│  ├──────────────────────────────────────────────────────────────────────────────────┤  │
│  │ NETWORK LAYER       : IPv4 Auto-Configuration (10.0.0.0/8) & Global ARP          │  │
│  ├──────────────────────────────────────────────────────────────────────────────────┤  │
│  │ MAC / LINK LAYER    : IEEE 802.11p Network Interface Controller (NIC)            │  │
│  ├──────────────────────────────────────────────────────────────────────────────────┤  │
│  │ PHYSICAL LAYER      : Ieee80211DimensionalRadioMedium (5.9 GHz DSRC Channel 3)   │  │
│  └──────────────────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📡 Radio & Network Specifications

Konfigurasi parameter lapisan fisik dan jaringan disesuaikan dengan profil standar vehicular:

| Parameter | Kendaraan Bergerak (*Car*) | Infrastruktur (*RSU*) | Satuan / Nilai |
|---|:---:|:---:|:---:|
| **Pita Frekuensi (*Center Frequency*)** | $5{,}9\text{ GHz}$ | $5{,}9\text{ GHz}$ | DSRC Band |
| **Nomor Kanal (*Channel Number*)** | Channel 3 | Channel 3 | Standar 802.11p |
| **Lebar Pita (*Channel Bandwidth*)** | $10\text{ MHz}$ | $10\text{ MHz}$ | Half-clocked OFDM |
| **Daya Pemancar ($P_{tx}$)** | $10\text{ mW}$ ($+10\text{ dBm}$) | $100\text{ mW}$ ($+20\text{ dBm}$) | Sesuai regulasi DSRC |
| **Ambang Sensitivitas Penerima ($P_{rx\_min}$)** | $-85\text{ dBm}$ | $-85\text{ dBm}$ | Ambang batas modulasi |
| **Radius Jangkauan Teoretis ($d_{max}$)** | $\approx \mathbf{227\text{ meter}}$ | $\approx \mathbf{718\text{ meter}}$ | Free-Space Path Loss |
| **Desah Termal Lingkungan (*Noise Floor*)** | $-110\text{ dBm}$ | $-110\text{ dBm}$ | Thermal noise |
| **Ketinggian Antena ($Z$)** | $1{,}5\text{ meter}$ (atap mobil) | $5{,}0\text{ meter}$ (tiang tower) | Koordinat Z kartesius |
| **Subnet IPv4** | `10.0.0.0/8` | `10.0.0.0/8` | Privat Kelas A |

> 📖 **Penurunan Rumus Matematis**: Penjelasan kalkulasi analitis formula redaman Friis tersedia lengkap di dokumen [Lapisan Fisik & MAC](wiki/Physical-and-MAC-Layers.md).

---

## 🧪 Simulation Scenarios & Benchmark Matrix

Semua skenario pengujian didefinisikan secara deklaratif di `vanet_aodv/omnetpp.ini`:

| Skenario | Paradigma | Protokol Aplikasi | Beban Trafik | Fokus Evaluasi Performa |
|---|:---:|:---:|:---:|---|
| **`AODV_V2V_Ping`** | V2V (1:1) | ICMP (`PingApp`) | 56 B / $1\text{s}$ | Latensi RTT bolak-balik, overhead RREQ/RREP, packet loss |
| **`AODV_V2V_UDP`** | V2V (1:1) | UDP (`UdpBasicApp`) | 512 B / $1\text{s}$ | Throughput kontinu ($kbps$), Packet Delivery Ratio (PDR) |
| **`AODV_V2I_RSU`** | V2I ($N$:1) | UDP Telemetry | 256 B / $2\sim4\text{s}$ | Agregasi data masal ke RSU, ketahanan kongesti kanal |
| **`AODV_HelloMessages`** | V2V (1:1) | UDP + HELLO RFC 3561 | 512 B / $1\text{s}$ + Hello $1\text{s}$ | Perbandingan overhead kontrol beaconing vs MAC feedback |

---

## 🖥️ Multi-Layer Network Visualizer (Qtenv)

Visualizer grafis pada antarmuka Qtenv dikonfigurasi secara global di bawah blok `[General]` agar seragam di semua skenario:

| Layer Visualisasi | Tampilan Grafis | Komponen Visualizer | Arti Fungsional di Simulasi |
|---|:---:|---|---|
| **Physical Radio Range** | 🔵 **Lingkaran Biru Langit** (`deepskyblue`) | `mediumVisualizer` | Lingkaran radius jangkauan fisik riil kendaraan ($P_{rx} \ge -85\text{ dBm}$). |
| **1-Hop MAC Data Link** | 🟡 **Garis Emas / Kuning** (`gold`, 2.5px) | `dataLinkVisualizer` | Menunjukkan pertukaran frame unicast 802.11p yang sukses dan ter-ACK. |
| **AODV Multi-Hop Route** | 🟢 **Garis Hijau Terang** (`lime`, 3.5px) | `networkRouteVisualizer` | Jalur estafet jaringan aktif *end-to-end* yang tersimpan di tabel routing. |
| **Road Network Geometry** | 🟤 **Garis Merah Bata** (`firebrick4`) | `roadsCanvasVisualizer` | Struktur segmen jalan raya yang diproyeksikan dari SUMO ke kanvas. |

> [!NOTE]
> Garis panah merah rambatan gelombang imajiner (`mediumVisualizer.displaySignals`) sengaja dinonaktifkan secara global untuk mengeliminasi distorsi visual pada layar dan menjaga fokus pengamatan pada link komunikasi riil.

---

## 🗺️ Map Import & Traffic Scaling

### A. Impor Peta Baru dari File `.osm` Secara Otomatis
Jika Anda ingin mengganti peta dengan area baru dari OpenStreetMap (`.osm`), gunakan skrip otomatis **`import_map.sh`**:

```bash
# Sintaks: ./import_map.sh <BERKAS_OSM> [JUMLAH_MOBIL]

# Contoh: Import peta baru dengan 30 kendaraan aktif
./import_map.sh surabaya_pusat.osm 30

# Atau gunakan peta default (map.osm):
./import_map.sh map.osm 20
```

**Alur Otomasi Skrip `import_map.sh`:**
1. **`netconvert`**: Mengonversi `.osm` menjadi `maps.net.xml` dengan proyeksi UTM kartesius riil (`--proj.utm`).
2. **Auto Center RSU**: Menghitung titik tengah kota dari `convBoundary` dan otomatis memperbarui posisi `initialX` / `initialY` RSU di `omnetpp.ini` serta `Scenario.ned`.
3. **Auto Resize Canvas**: Menyesuaikan dimensi kanvas `@display("bgb=...")` di `Scenario.ned` dengan luas peta baru.
4. **`randomTrips.py` & `duarouter`**: Membangkitkan rute perjalanan terpendek yang valid pada jaringan jalan.
5. **Fleet Synchronization**: Memformat armada kendaraan agar berangkat serentak di $t=0{,}00\text{ s}$ (`departSpeed="max"`).
6. **Instant Ready**: Menyinkronkan berkas ke folder `vanet_aodv/` sehingga simulasi langsung siap dijalankan.

---

### B. Mengubah Kepadatan Kendaraan pada Peta Aktif (`set_nodes.py`)
Untuk peta yang sudah terpasang, jumlah armada mobil dapat diubah kapan saja tanpa regenerasi peta:

```bash
cd vanet_aodv

# Mengatur armada kendaraan:
./set_nodes.py 10    # 10 kendaraan (kepadatan rendah)
./set_nodes.py 25    # 25 kendaraan (kepadatan sedang)
./set_nodes.py 50    # 50 kendaraan (kepadatan tinggi)
```

```text
[✓] Berhasil mengupdate maps.rou.xml menjadi 25 mobil (semua depart di t=0.00s).
```

---

## 🚀 Quick Start Guide

### 1. Inisialisasi Environment

Pastikan OMNeT++ 6.4, INET 4.5, dan SUMO telah terpasang dan diekspor ke environment sistem:

```bash
cd /path/to/VANET-LAB
source ../setenv
```

### 2. Menjalankan Simulasi Mode Grafis (Interactive Qtenv)

Jalankan daemon TraCI dengan antarmuka visual SUMO-GUI di terminal pertama:
```bash
./run_sumo_launchd.sh
```

Buka terminal kedua dan jalankan visualizer grafis OMNeT++:
```bash
cd vanet_aodv

# Menjalankan skenario default (AODV_V2V_Ping):
./run_gui.sh

# Atau pilih skenario lain:
./run_gui.sh AODV_V2V_UDP
./run_gui.sh AODV_V2I_RSU
./run_gui.sh AODV_HelloMessages
```

### 3. Menjalankan Simulasi Mode Headless (Cmdenv)

Untuk keperluan *batch benchmarking* atau eksekusi pada server tanpa layar GUI:
```bash
cd vanet_aodv

# Format: ./run_cmd.sh <Nama_Skenario> [Durasi]
./run_cmd.sh AODV_V2V_Ping 30s
./run_cmd.sh AODV_V2V_UDP 60s
./run_cmd.sh AODV_V2I_RSU 100s
```

---

## 📊 Evaluation Metrics & Output Files

Setiap eksekusi simulasi menghasilkan berkas rekaman di folder **`vanet_aodv/results/`**:
- **`*.sca` (Scalar)**: Ringkasan statistik akhir (total paket dikirim/diterima, rata-rata latensi RTT).
- **`*.vec` (Vector)**: Deret waktu (*time-series*) metrik dinamis (RTT per paket, fluktuasi throughput).

### Formula Metrik Kunci:

1. **Packet Delivery Ratio (PDR)**:
   $$\text{PDR} = \left(\frac{\sum \text{Paket Diterima}}{\sum \text{Paket Dikirim}}\right) \times 100\%$$
2. **Average End-to-End Latency / RTT**:
   $$\text{RTT}_{\text{avg}} = \frac{1}{N} \sum_{i=1}^N \text{RTT}_i$$
3. **Network Throughput**:
   $$\text{Throughput (kbps)} = \frac{\sum \text{Bits Diterima}}{\Delta t \times 1000}$$

---

## 📚 Project Wiki & Documentation

Dokumentasi teknis mendalam telah disusun ke dalam folder **`wiki/`**:

| Dokumen Wiki | Deskripsi Materi |
|---|---|
| [**Home**](wiki/Home.md) | Indeks navigasi utama dokumentasi proyek. |
| [**Architecture & Design**](wiki/Architecture-and-Design.md) | Rincian arsitektur 4 simulator, hierarki NED, dan loop TraCI. |
| [**AODV Routing Protocol**](wiki/Routing-Protocol-AODV.md) | Bedah mekanisme RFC 3561, expanding ring search, dan parameter tabel routing. |
| [**Physical & MAC Layers**](wiki/Physical-and-MAC-Layers.md) | Turunan matematis formula Friis, frekuensi DSRC 5.9 GHz, dan kalibrasi antena. |
| [**Traffic & Mobility Model**](wiki/Traffic-Mobility-and-Map.md) | Data geospasial OSM Keputih, koordinat UTM, dan strategi keberangkatan serentak. |
| [**Simulation Scenarios Guide**](wiki/Simulation-Scenarios.md) | Parameter detail 4 skenario benchmark dan analisis alur paket. |
| [**GUI Visualization Guide**](wiki/GUI-and-Visualization-Guide.md) | Panduan inspeksi visual, inspektur modul runtime, dan arti semantik warna. |
| [**Data Analysis & Metrics**](wiki/Data-Analysis-and-Metrics.md) | Prosedur ekstraksi `opp_scavetool` dan skrip parser otomatis Python. |
| [**Execution & Troubleshooting**](wiki/Getting-Started-and-Troubleshooting.md) | Panduan eksekusi sistematis dan solusi penanganan kode galat umum. |

---

## 📂 Directory Layout

```text
VANET-LAB/
├── inet/                  # INET Framework 4.5 (Network & Physical layers)
├── veins/                 # Veins 5.3 (TraCI client & vehicular model)
├── veins_inet/            # Veins-INET subproject (Mobility adapter)
├── map.osm                # Sumber geospasial mentah OpenStreetMap
├── maps.net.xml           # Jaringan jalan SUMO (proyeksi UTM kartesius)
├── maps.rou.xml           # Rute aktif kendaraan yang digunakan simulasi
├── maps.sumocfg           # Konfigurasi simulasi mikroskopik SUMO
├── run_sumo_launchd.sh    # Runner otomatis daemon veins_launchd + SUMO-GUI
├── wiki/                  # Dokumentasi teknis komprehensif proyek
│   ├── Home.md
│   ├── Architecture-and-Design.md
│   ├── Routing-Protocol-AODV.md
│   ├── Physical-and-MAC-Layers.md
│   ├── Traffic-Mobility-and-Map.md
│   ├── Simulation-Scenarios.md
│   ├── GUI-and-Visualization-Guide.md
│   ├── Data-Analysis-and-Metrics.md
│   └── Getting-Started-and-Troubleshooting.md
├── vanet_aodv/            # DIREKTORI UTAMA OMNeT++
│   ├── Scenario.ned       # Topologi simulasi jaringan tingkat atas
│   ├── VeinsAodvCar.ned   # Modul kendaraan bergerak berbasis AodvRouter
│   ├── VeinsAodvRSU.ned   # Modul Road-Side Unit infrastruktur statis
│   ├── omnetpp.ini        # Parameter simulasi & 4 skenario benchmark
│   ├── maps.rou.all.xml   # Master rute 91 kendaraan SUMO
│   ├── set_nodes.py       # Generator skala kepadatan armada mobil
│   ├── run_cmd.sh         # Skrip eksekusi otomatis mode headless
│   ├── run_gui.sh         # Skrip eksekusi otomatis mode grafis Qtenv
│   └── results/           # Direktori penyimpanan data (*.sca, *.vec)
└── README.md              # Gerbang dokumentasi utama proyek
```

---

## 📄 References & License

- **Lisensi**: Proyek ini dilisensikan untuk keperluan riset akademis dan edukasi (*Academic Public License*).
- **Referensi Standar**:
  - RFC 3561: *Ad hoc On-Demand Distance Vector (AODV) Routing*, IETF.
  - IEEE Std 802.11p-2010: *Wireless Access in Vehicular Environments (WAVE)*.
  - Sommer, C., German, R., & Dressler, F. (2011). *Bidirectionally Coupled Network and Road Traffic Simulation for Improved IVC Analysis*. IEEE Transactions on Mobile Computing.
