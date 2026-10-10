# 🛠️ Panduan Eksekusi & Troubleshooting

Dokumen ini memuat langkah demi langkah memulai simulasi dari lingkungan terminal, sintaks eksekusi berbagai mode, serta katalog pemecahan masalah (*troubleshooting*) saat mengalami kendala teknis.

---

## 1. Persiapan Lingkungan (Prerequisites)

Sebelum mengeksekusi simulasi, pastikan lingkungan terminal telah memuat variabel lingkungan yang benar untuk OMNeT++, INET, dan SUMO.

```bash
# Berada di direktori root VANET-LAB:
cd /home/ayasy/Documents/Kuliah/Semester_6/VANET/VANET-LAB

# Muat variabel environment sistem (PATH dan LD_LIBRARY_PATH):
source ../setenv
```

### Memverifikasi Kesiapan Tool:
```bash
# 1. Cek compiler & runner OMNeT++:
opp_run -v

# 2. Cek simulator lalu lintas SUMO:
which sumo
which sumo-gui

# 3. Cek versi Python:
python3 --version
```

---

## 2. Alur Eksekusi Simulasi

Tersedia dua opsi utama untuk menjalankan simulasi:

---

### Opsi A: Eksekusi Mode Grafis (Qtenv + SUMO-GUI)
Sangat direkomendasikan saat demonstrasi, observasi visual, atau validasi alur transmisi paket.

#### Langkah 1: Aktifkan SUMO TraCI Daemon
Buka terminal pertama dan jalankan:
```bash
./run_sumo_launchd.sh
```
*Skrip ini akan memvalidasi binary `sumo-gui` dan mengaktifkan pendengar soket TCP pada port 9999.*

#### Langkah 2: Jalankan Antarmuka Grafis OMNeT++
Buka terminal kedua dan jalankan:
```bash
cd vanet_aodv

# Menjalankan skenario default (AODV_V2V_Ping):
./run_gui.sh

# Atau pilih skenario lain:
./run_gui.sh AODV_V2V_UDP
./run_gui.sh AODV_V2I_RSU
./run_gui.sh AODV_HelloMessages
```

Pada jendela Qtenv:
1. Klik tombol **Set Up Network**.
2. Klik tombol **Run (F5)** atau **Fast (F6)** untuk memulai simulasi.

---

### Opsi B: Eksekusi Mode Headless (Cmdenv)
Sangat direkomendasikan untuk pengujian skala besar, *batch simulation*, atau eksekusi pada server komputasi tanpa layar monitor (*display-less*).

```bash
cd vanet_aodv

# Format perintah:
# ./run_cmd.sh <Nama_Skenario> [Batas_Waktu_Simulasi]

# 1. Menjalankan pengujian Ping selama 30 detik:
./run_cmd.sh AODV_V2V_Ping 30s

# 2. Menjalankan transmisi data UDP selama 60 detik:
./run_cmd.sh AODV_V2V_UDP 60s

# 3. Menjalankan telemetri RSU selama 100 detik:
./run_cmd.sh AODV_V2I_RSU 100s
```

*Skrip `run_cmd.sh` akan secara otomatis menyalakan daemon `veins_launchd` di latar belakang jika belum aktif, dan mematikannya kembali dengan aman saat simulasi selesai.*

---

## 3. Matriks Pemecahan Masalah (Troubleshooting)

<div align="center">

| Pesan Kendala / Error | Kemungkinan Penyebab | Tindakan Perbaikan |
|---|---|---|
| **`Connection refused on port 9999`** | Daemon `veins_launchd` belum aktif atau crash sebelum OMNeT++ terhubung. | Jalankan `./run_sumo_launchd.sh` di terminal terpisah sebelum memulai OMNeT++. |
| **`Address already in use: 9999`** | Sisa proses `veins_launchd` atau SUMO dari sesi sebelumnya masih tertahan di memori. | Matikan proses lama: `fuser -k 9999/tcp` atau `pkill -f veins_launchd`. |
| **`sumo-gui: cannot open display`** | Menjalankan mode GUI di terminal SSH tanpa fitur *X11 Forwarding*. | Gunakan mode headless (`run_cmd.sh`) atau tambahkan flag `ssh -X`. |
| **`error while loading shared libraries: libINET.so`** | Library dinamik INET belum terdaftar di `LD_LIBRARY_PATH`. | Jalankan `source setenv` di root direktori proyek. |
| **`Vehicle ID '0' not known` / Mobil diam** | Berkas rute kendaraan tidak sinkron atau belum dimodifikasi. | Jalankan `./set_nodes.py 20` di folder `vanet_aodv/` untuk regenerasi rute baru yang serentak di $t=0\text{s}$. |
| **Simulasi sangat lambat di Qtenv** | Animasi grafis merender terlalu banyak frame per detik. | Ubah mode tombol di Qtenv dari **Run** menjadi **Fast (F6)** atau **Express (F7)**. |

</div>
