# Simulasi Routing Protokol AODV pada VANET

Projek lengkap simulasi jaringan kendaraan (**VANET - Vehicular Ad-hoc Network**) menggunakan **OMNeT++ 6.x**, **INET Framework 4.5.x**, **Veins 5.3.x**, dan simulator lalu lintas **Eclipse SUMO**. Projek ini menguji kinerja protokol routing **AODV (Ad hoc On-Demand Distance Vector, RFC 3561)** pada peta jalan (`maps.sumocfg`).

---

## 1. Struktur Direktori Projek

Projek telah dirapikan tanpa duplikasi file:

```text
vanet_aodv/
├── .project                # File project OMNeT++ IDE
├── .nedfolders             # Konfigurasi source NED
├── package.ned             # Deklarasi package (vanet_aodv)
├── Scenario.ned            # Topologi jaringan (RadioMedium, TraCI Manager, Visualizer, Nodes, RSU)
├── VeinsAodvCar.ned        # Modul node kendaraan bergerak (IEEE 802.11p + AODV + VeinsInetMobility)
├── VeinsAodvRSU.ned        # Modul Road-Side Unit statis di persimpangan jalan
├── omnetpp.ini             # Konfigurasi simulasi lengkap (studi kasus V2V & V2I)
├── maps.sumocfg            # Konfigurasi utama SUMO
├── maps.net.xml            # Jaringan jalan peta
├── maps.rou.xml            # File rute aktif SUMO (seluruh mobil berangkat di t=0s)
├── maps.rou.all.xml        # Master pool seluruh rute kendaraan
├── maps.launchd.xml        # Bridge TraCI untuk peluncuran SUMO
├── empty.xml               # Lingkungan fisik
├── set_nodes.py            # Script 1-baris untuk mengubah jumlah node mobil secara instan
├── run_cmd.sh              # Script eksekusi simulasi mode Command Line (Cmdenv)
├── run_gui.sh              # Script eksekusi simulasi mode Grafis GUI (Qtenv)
├── run_veins_launchd.sh    # Script kontrol daemon veins_launchd
├── results/                # Direktori penyimpanan hasil simulasi (*.sca, *.vec)
└── README.md               # Dokumentasi projek
```

---

## 2. Skenario Studi Kasus di `omnetpp.ini`

Terdapat 4 konfigurasi kasus pengujian di `omnetpp.ini`:

| Konfigurasi | Kasus Pengujian | Deskripsi & Aliran Data |
|---|---|---|
| **`[Config AODV_V2V_Ping]`** | **V2V Ping (ICMP)** | Mobil 0 menguji route discovery AODV menuju Mobil 1 dengan mengirim Ping berkala sambil melaju. Mobil lain menjadi perantara multi-hop. Mengukur **RTT** dan **packet loss**. |
| **`[Config AODV_V2V_UDP]`** | **V2V UDP Data** | Mobil 0 mengirim aliran data UDP CBR (512B) ke Mobil 1 (`UdpSink`) sambil kedua mobil melaju di jalan. Mengukur **Throughput** dan **PDR**. |
| **`[Config AODV_V2I_RSU]`** | **V2I Telemetri ke RSU** | RSU statis ditempatkan di persimpangan tengah peta. Seluruh mobil yang melaju mengirim laporan data telemetri ke RSU via multi-hop AODV. |
| **`[Config AODV_HelloMessages]`** | **AODV HELLO Mechanism** | Menguji AODV dengan pengiriman pesan HELLO berkala (1s) sesuai RFC 3561 untuk pemeliharaan tabel tetangga (*neighbor sensing*). |
| **`[Config GUI]`** | **Tampilan Visual Lengkap** | Mode interaktif Qtenv dengan animasi pergerakan mobil, garis link fisik, dan visualisasi rute AODV. |

---

## 3. Cara Mengubah Jumlah Node Mobil (Sangat Mudah)

Untuk menambah atau mengurangi jumlah mobil yang melaju di jalan, gunakan script **`set_nodes.py`**:

```bash
cd vanet_aodv

# Mau 10 mobil:
./set_nodes.py 10

# Mau 20 mobil:
./set_nodes.py 20

# Mau 50 mobil:
./set_nodes.py 50
```

> **Catatan:** Script ini langsung meng-overwrite file `maps.rou.xml`. Semua mobil yang dipilih langsung berangkat serentak di awal simulasi ($t=0.00$s) dan melaju di peta jalan.

---

## 4. Cara Menjalankan Simulasi

### Cara A: Melalui Terminal (Script Otomatis)
Script `run_cmd.sh` akan otomatis menyalakan `veins_launchd`, mengeksekusi simulasi, menampilkan log statistik, dan mematikan daemon setelah selesai:

```bash
cd vanet_aodv

# 1. Jalankan V2V Ping (durasi 30 detik):
./run_cmd.sh AODV_V2V_Ping 30s

# 2. Jalankan V2V UDP:
./run_cmd.sh AODV_V2V_UDP 30s

# 3. Jalankan V2I RSU:
./run_cmd.sh AODV_V2I_RSU 30s

# 4. Jalankan AODV dengan Hello Messages:
./run_cmd.sh AODV_HelloMessages 30s

# 5. Jalankan Tampilan Visual GUI (Qtenv):
./run_gui.sh GUI
```

---

### Cara B: Melalui OMNeT++ IDE
1. Jalankan daemon TraCI terlebih dahulu di terminal:
   ```bash
   ./vanet_aodv/run_veins_launchd.sh start
   ```
2. Buka OMNeT++ IDE, klik kanan `omnetpp.ini` > **Run As** > **OMNeT++ Simulation**.
3. Pilih skenario yang diinginkan (misal: `AODV_V2V_Ping`, `AODV_V2V_UDP`, atau `GUI`).
4. Klik **Run**.
5. Jika sudah selesai, hentikan daemon dengan:
   ```bash
   ./vanet_aodv/run_veins_launchd.sh stop
   ```
