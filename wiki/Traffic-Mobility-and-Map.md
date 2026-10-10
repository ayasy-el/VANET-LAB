# 🗺️ Mobilitas Lalu Lintas & Peta Jalan

Dokumen ini mendokumentasikan proses pengolahan data geospasial jalan raya, konfigurasi mobilitas mikroskopik kendaraan pada **Eclipse SUMO**, serta mekanisme rekayasa jumlah node kendaraan menggunakan skrip otomasi.

---

## 1. Pemodelan Wilayah Geospasial (OpenStreetMap ke SUMO)

Peta simulasi menggunakan data jalan raya nyata dari kawasan perkotaan Keputih (Surabaya). Alur pemrosesan data dilakukan melalui tahapan pipeline standar SUMO:

```
┌──────────────┐                  ┌──────────────┐                  ┌──────────────┐
│   map.osm    │── netconvert ───►│ maps.net.xml │── duarouter ────►│ maps.rou.xml │
│ (Data Mentah)│                  │(Jalan Kartes)│   trips.trips.xml│(Rute Kendaraan)
└──────────────┘                  └──────────────┘                  └──────────────┘
```

### A. Dimensi & Batas Koordinat Lapangan (`convBoundary`)
Dalam berkas `maps.net.xml`, jaringan jalan diproyeksikan dari koordinat garis lintang/bujur WGS84 ke sistem kartesius lokal menggunakan UTM (*Universal Transverse Mercator*):

```xml
<location netOffset="-698305.12,-9199320.14" 
          convBoundary="0.00,0.00,2080.89,1737.66" 
          origBoundary="112.7915000,-7.3015000,112.8105000,-7.2856000" 
          projParameter="+proj=utm +zone=49 +ellps=WGS84 +datum=WGS84 +units=m +no_defs"/>
```

- **Sumbu Horizontal (X)**: $0{,}00\text{ m} \rightarrow 2.080{,}89\text{ m}$ ($\approx 2{,}08\text{ km}$)
- **Sumbu Vertikal (Y)**: $0{,}00\text{ m} \rightarrow 1.737{,}66\text{ m}$ ($\approx 1{,}74\text{ km}$)
- **Panjang Garis Diagonal Wilayah**:
  $$\text{Diagonal} = \sqrt{(2080{,}89)^2 + (1737{,}66)^2} = \sqrt{4.330.103 + 3.019.462} \approx \mathbf{2.711\text{ meter}}$$
- **Total Luas Cakupan**:
  $$\text{Luas} = 2{,}08089\text{ km} \times 1{,}73766\text{ km} \approx \mathbf{3{,}61\text{ km}^2}$$

---

## 2. Manajemen Rute Kendaraan (`maps.rou.xml`)

Berkas mobilitas kendaraan mendefinisikan rute awal (*origin*) dan akhir (*destination*) tiap mobil, jenis kendaraan, dan model perilaku mengemudi (*car-following model* seperti Krauss).

### Masalah Pola Keberangkatan Bertahap (*Staggered Departures*)
Secara default, generator lalu lintas sering kali menetapkan mobil berangkat secara bertahap (mobil 0 di detik 0, mobil 1 di detik 1, mobil 2 di detik 2, dst.).
- **Dampak Negatif pada Simulasi VANET**: Jika simulasi berjalan selama 30 detik dengan 20 mobil, maka mobil ke-19 baru muncul di detik ke-19. Akibatnya, pada detik-detik awal kepadatan mobil sangat renggang, topologi tidak terhubung (*network partitioned*), dan paket data gagal terkirim.

### Solusi: Keberangkatan Serentak (*Simultaneous Deployment*)
Dalam proyek ini, seluruh mobil diatur agar **berangkat serentak tepat pada $t = 0{,}00\text{ detik}$**:
```xml
<vehicle id="0" type="veh_passenger" depart="0.00" departLane="best" departSpeed="max">
    <route edges="44815464#0 44815464#1 44815464#2 ..."/>
</vehicle>
```
- **`depart="0.00"`**: Mobil langsung muncul di peta sejak awal simulasi.
- **`departLane="best"`**: Mobil langsung memilih lajur jalan terbaik untuk rutenya, menghindari antrean di lajur masuk.
- **`departSpeed="max"`**: Mobil langsung melaju dengan kecepatan maksimal batas jalan tanpa menunggu akselerasi lambat dari 0 km/jam.

---

## 3. Otomasi Pengaturan Node (`set_nodes.py`)

Untuk mempermudah eksperimen tanpa harus menyunting file XML yang panjang, disediakan skrip Python **`vanet_aodv/set_nodes.py`**.

Skrip ini membaca berkas induk **`maps.rou.all.xml`** (yang menyimpan total **91 kendaraan unik**) dan memotongnya sesuai jumlah node yang diminta pengguna:

```python
# Cara kerja inti set_nodes.py
tree = ET.parse("maps.rou.all.xml")
vehicles = tree.getroot().findall("vehicle")

# Mengambil N mobil pertama dan memaksakan depart=0.00s
for v in vehicles[:n]:
    v.set("depart", "0.00")
    v.set("departLane", "best")
    v.set("departSpeed", "max")
    new_root.append(v)
```

### Panduan Penggunaan Skrip:
```bash
cd vanet_aodv

# Mengatur kepadatan rendah (10 mobil):
./set_nodes.py 10

# Mengatur kepadatan sedang (25 mobil):
./set_nodes.py 25

# Mengatur kepadatan tinggi (50 mobil):
./set_nodes.py 50

# Mengatur kapasitas penuh (91 mobil):
./set_nodes.py 91
```

---

## 4. Pipeline Otomatis Impor Peta Baru (`import_map.py` / `import_map.sh`)

Untuk mengganti peta simulasi dengan peta kota mana pun dari OpenStreetMap (`.osm`) dalam **1 langkah instan**, telah disediakan pipeline otomasi terpadu:

```bash
# Sintaks umum:
./import_map.sh <path_ke_file.osm> [jumlah_mobil_aktif]

# Contoh:
./import_map.sh peta_jakarta.osm 30
```

### ⚙️ Detail Alur Kerja Pipeline:
1. **Ekstraksi Jaringan Jalan (`netconvert`)**:
   Menerapkan proyeksi UTM kartesius (`--proj.utm`) dan membersihkan geometri persimpangan (`--geometry.remove`, `--roundabouts.guess`, `--junctions.join`, `--tls.guess-signals`).
2. **Kalkulasi Geometri & Pemosisian RSU**:
   Mengekstrak `convBoundary` secara otomatis, menghitung luas wilayah ($km^2$), dan menetapkan titik pusat $(X_{center}, Y_{center})$.
3. **Pembaruan Deklarasi NED & INI**:
   - Menyesuaikan ukuran kanvas `@display("bgb=W,H")` pada `Scenario.ned`.
   - Menggeser posisi RSU di `Scenario.ned` dan parameter `*.rsu[0].mobility.initialX` / `initialY` di `omnetpp.ini` tepat ke pusat kota baru.
4. **Pembangkitan Trip Acak (`randomTrips.py`)**:
   Memanggil `randomTrips.py` (yang terintegrasi dalam environment python SUMO) untuk menghasilkan ratusan pasangan rute asal-tujuan yang realistis.
5. **Perutean Jalan Raya (`duarouter`)**:
   Menghitung jalur terpendek (*shortest path Dijkstra*) di jaringan jalan dengan mengabaikan edge yang tidak terhubung.
6. **Sinkronisasi & Normalisasi Armada**:
   Memformat seluruh kendaraan agar berangkat serentak di $t=0{,}00\text{ s}$ dengan penomoran indeks berurutan (`0, 1, 2, ... N-1`).
7. **Penyebaran Berkas**:
   Menyinkronkan file output (`maps.net.xml`, `maps.rou.xml`, `maps.rou.all.xml`, `maps.sumocfg`) ke root dan `vanet_aodv/`. Simulasi OMNeT++ langsung siap dijalankan seketika.

---

## 5. Konfigurasi SUMO & TraCI Launcher

### A. Konfigurasi SUMO: `maps.sumocfg`
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
- **`step-length = 0.1`**: Menyelaraskan langkah waktu fisik kendaraan SUMO ke resolusi $100\text{ ms}$, persis sesuai dengan interval update manajer Veins di OMNeT++.

### B. Konfigurasi TraCI: `vanet_aodv/maps.launchd.xml`
```xml
<launch>
    <copy file="maps.net.xml"/>
    <copy file="maps.rou.xml"/>
    <copy file="maps.sumocfg"/>
</launch>
```
File ini memberi instruksi kepada `veins_launchd` untuk mengkopi berkas konfigurasi lalu lintas ke direktori sementara (*sandbox*) saat simulasi dijalankan.
