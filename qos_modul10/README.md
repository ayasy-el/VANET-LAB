# Modul Praktikum 10 — Visualisasi QoS VANET

Modul ini mengolah hasil simulasi OMNeT++ dari Praktikum 8 dan 9 menjadi tabel
QoS dan grafik perbandingan AODV vs GPSR. Fokusnya adalah **pengolahan data dan
visualisasi**, bukan mengubah algoritma routing atau peta.

Status saat ini (2026-11-20):

| Peta | AODV | GPSR | Grafik |
|---|---|---|---|
| Map A | tersedia | tersedia | 4 grafik |
| Map B | tersedia (run 2026-11-20) | tersedia (run ulang 2026-11-20) | 4 grafik |

Total: **8 grafik**, semuanya dibuat dari file `.sca` yang tervalidasi.

> **Catatan provenance Map B:** hasil GPSR Map B yang lama sudah tertimpa oleh
> run Map A. Data Map B yang dipakai sekarang adalah **run ulang 2026-11-20**,
> bukan salinan file lama. Run ulang tersebut mereproduksi angka dokumentasi
> (27/38 ping, 26/38 UDP, 2,88 kbit/s). AODV Map B sebelumnya belum pernah
> dijalankan; run 2026-11-20 adalah run pertamanya. Lihat §3 dan
> `data/map_b_gpsr/SOURCE.md`.

---

## 1. Tujuan

1. Membaca statistik aplikasi dari file `.sca` hasil simulasi.
2. Menghitung Packet Loss, RTT, PDR, dan throughput.
3. Menyimpan hasil dalam CSV yang dapat diperiksa.
4. Membuat grafik batang AODV vs GPSR untuk setiap peta.
5. Memvalidasi bahwa nilai grafik benar-benar berasal dari `.sca`.
6. Menyediakan prosedur yang dapat diulang mahasiswa.

---

## 2. Struktur direktori

```text
qos_modul10/
├── data/
│   ├── manifest.json          # provenance: run ID, launch config, seed, sha256
│   ├── map_a_aodv/            # .sca/.vec/.vci + SOURCE.md
│   ├── map_a_gpsr/            # .sca/.vec/.vci + SOURCE.md
│   ├── map_b_aodv/            # .sca/.vec/.vci + SOURCE.md
│   └── map_b_gpsr/            # .sca/.vec/.vci + SOURCE.md
├── scripts/
│   ├── extract_qos.py         # .sca -> CSV
│   ├── plot_qos_charts.py     # CSV -> PNG
│   └── validate_qos.py        # CSV vs .sca -> laporan validasi
├── grafik/
│   ├── map_a/
│   │   ├── map_a_packet_loss.png
│   │   ├── map_a_avg_rtt.png
│   │   ├── map_a_pdr.png
│   │   └── map_a_throughput.png
│   └── map_b/
│       ├── map_b_packet_loss.png
│       ├── map_b_avg_rtt.png
│       ├── map_b_pdr.png
│       └── map_b_throughput.png
├── hasil/
│   ├── qos_summary.csv
│   └── validasi.md
└── README.md
```

File `.sca`, `.vec`, dan `.vci` di `data/` adalah salinan lokal. Git mengabaikan
ketiganya sesuai `.gitignore` proyek, sehingga yang masuk repositori adalah
manifest, CSV, laporan validasi, grafik, dan `SOURCE.md`. Salinan mentah tetap
diperlukan untuk menjalankan ulang ekstraksi di mesin ini; cara memulihkannya
ada di `SOURCE.md` masing-masing folder.

---

## 3. Status data dan audit provenance

Keempat kombinasi yang diminta modul:

| Kombinasi | Status | Bukti |
|---|---|---|
| Map A + AODV | tersedia | `maps.launchd.xml`, 20 node, seedset 0, 40 s |
| Map A + GPSR | tersedia | `maps.launchd.xml`, 20 node, seedset 0, 40 s |
| Map B + AODV | tersedia | `map2.launchd.xml`, 80 node, seedset 0, 40 s |
| Map B + GPSR | tersedia | `map2.launchd.xml`, 80 node, seedset 0, 40 s |

### Map A

- AODV: run 2026-11-06, `AODV_V2V_Ping-0-20261106-13:30:29-2652` dan
  `AODV_V2V_UDP-0-20261106-13:33:25-3022`.
- GPSR: run 2026-11-12, `GPSR_V2V_Ping-0-20261112-12:36:31-2556` dan
  `GPSR_V2V_UDP-0-20261112-12:38:00-3298`.
- Kedua workspace memakai aset Map A yang sama (`maps.*` byte-identical),
  20 kendaraan, seedset 0, 40 s.

Nama file `GPSR_*` tidak membuktikan peta. Metadata runtime di dalam `.sca`
menunjukkan:

```text
par Scenario.manager launchConfig "<launch>...</launch> at
    .../vanet_gpsr/maps.launchd.xml:2"
```

`maps.launchd.xml` adalah Map A, dan jumlah kendaraannya 20. Jadi file tersebut
valid sebagai **Map A + GPSR**.

### Map B

Map B memakai `map2.launchd.xml`, 80 kendaraan, seedset 0, dan 40 s. Semua run
dijalankan pada 2026-11-20 dengan output terisolasi:

```text
par Scenario.manager launchConfig "<launch>...</launch> at
    .../vanet_aodv/map2.launchd.xml:10"   # AODV
par Scenario.manager launchConfig "<launch>...</launch> at
    .../vanet_gpsr/map2.launchd.xml:10"   # GPSR
```

Run ID:

- AODV Ping: `AODV_V2V_Ping-0-20261120-13:30:59-5942`
- AODV UDP: `AODV_V2V_UDP-0-20261120-13:31:18-5984`
- GPSR Ping: `GPSR_V2V_Ping-0-20261120-13:31:28-6009`
- GPSR UDP: `GPSR_V2V_UDP-0-20261120-13:31:57-6043`

### Riwayat data Map B

`run_cmd.sh` menulis ke `results/<CONFIG>-#0.sca`; opsi `--map` hanya mengganti
launch config, tidak mengganti nama output. Riwayat shell menunjukkan run GPSR
Map B (`--map map2`) kemudian ditimpa run GPSR Map A (`--map maps`) dengan nama
file yang sama. Karena itu file Map B yang lama hilang.

Data Map B sekarang berasal dari run ulang 2026-11-20, bukan file lama. Untuk
GPSR, hasil run ulang sama dengan angka di
`docs/PRAKTIKUM8_GPSR_MAP_B.md` §5: 27/38 ping, 26/38 UDP, 2,88 kbit/s. Untuk
AODV Map B, run 2026-11-20 adalah run pertama.

Semua run Map B memakai `--result-dir` agar `vanet_aodv/results/` dan
`vanet_gpsr/results/` (hasil Map A) tidak tertimpa.

---

## 4. Persyaratan

Untuk ekstraksi dan grafik:

- Python 3.8+
- `pandas`
- `matplotlib`

Cek:

```bash
python3 -c "import pandas, matplotlib; print(pandas.__version__, matplotlib.__version__)"
```

OMNeT++ 6.1, INET, Veins, dan SUMO hanya diperlukan jika akan menjalankan ulang
simulasi. Modul ini tidak mengubah konfigurasi routing atau peta.

---

## 5. Cara menjalankan

Jalankan dari dalam `qos_modul10/`:

```bash
cd qos_modul10

# 1. Ekstraksi statistik .sca -> hasil/qos_summary.csv
python3 scripts/extract_qos.py

# 2. Grafik -> grafik/map_a/*.png dan grafik/map_b/*.png
python3 scripts/plot_qos_charts.py

# 3. Validasi -> hasil/validasi.md
python3 scripts/validate_qos.py
```

Urutannya penting: grafik membaca CSV, dan validasi membaca CSV + `.sca`.

Untuk menjalankan simulasi baru tanpa mengedit file, gunakan wrapper di root repo:

```bash
./run_vanet.sh aodv a both 40s
./plot_qos.sh --map a --run runs/map_a/aodv/<id> --run runs/map_a/gpsr/<id>
```

Salinan `.sca` di `data/` **tidak ikut masuk repositori** (ukurannya 24 MB dan
memuat path absolut mesin pembuatnya). Karena itu, pada clone baru
`plot_qos.sh --map a` memerlukan `.sca` yang dipulihkan dari `SOURCE.md` atau
dihasilkan ulang dengan `run_vanet.sh`. Tabel `hasil/qos_summary.csv`, delapan
grafik, dan `hasil/validasi.md` adalah artefak tervalidasi yang disertakan.

---

## 6. Output

### `hasil/qos_summary.csv`

Satu baris per kombinasi dan skenario (`ping` atau `udp`), total 8 baris. Kolom
penting:

| Kolom | Arti |
|---|---|
| `map`, `algorithm`, `scenario` | identitas kombinasi |
| `status` | `available` atau `missing` |
| `source_file`, `run_id`, `run_datetime` | asal data |
| `seedset`, `sim_time_limit_s`, `node_count` | konfigurasi run |
| `launch_config` | `maps.launchd.xml` (Map A) atau `map2.launchd.xml` (Map B) |
| `ping_sent`, `ping_received`, `packet_loss_pct` | metrik Ping |
| `rtt_min_ms`, `rtt_avg_ms`, `rtt_max_ms` | RTT dari histogram PingApp |
| `udp_tx_packets`, `udp_rx_packets`, `pdr_pct` | metrik UDP |
| `udp_tx_bytes`, `udp_rx_bytes`, `measurement_window_s` | dasar throughput |
| `throughput_kbps` | throughput rata-rata |
| `notes` | catatan provenance |

### Grafik

Delapan grafik, semuanya 300 DPI, batang AODV vs GPSR, sumbu Y dari nol, nilai
data ditampilkan di atas batang:

```text
grafik/map_a/map_a_packet_loss.png
grafik/map_a/map_a_avg_rtt.png
grafik/map_a/map_a_pdr.png
grafik/map_a/map_a_throughput.png
grafik/map_b/map_b_packet_loss.png
grafik/map_b/map_b_avg_rtt.png
grafik/map_b/map_b_pdr.png
grafik/map_b/map_b_throughput.png
```

### `hasil/validasi.md`

Berisi:

- ringkasan pemeriksaan (lulus/gagal),
- tabel provenance setiap run,
- perbandingan nilai CSV dengan hitung ulang dari `.sca`,
- pemeriksaan konsistensi konfigurasi AODV vs GPSR per peta,
- asal data untuk setiap grafik,
- catatan interpretasi.

---

## 7. Rumus dan jendela pengukuran

```text
Packet Loss (%) = (Ping Sent - Ping Received) / Ping Sent * 100
PDR (%)         = Rx Packets / Tx Packets * 100
Throughput      = Total Received Bytes * 8 / (Measurement Duration * 1000)
```

Satuan throughput adalah **kbit/s** (ditulis `kbps` pada grafik).

`Measurement Duration` **tidak** diasumsikan 40 s. Nilainya dibaca dari
parameter aplikasi setiap run:

- Ping: `sendInterval = 1s`, `startTime = 3s`, 38 paket terkirim.
- UDP: `sendInterval = 1s`, `startTime = 3s`, 38 paket terkirim.
- Jendela = (38 − 1) × 1 s = **37 s** (paket pertama sampai paket terakhir).

Jika periode pengiriman berbeda di skenario lain, script akan memakai nilai
`sendInterval`/`startTime` dari run tersebut, bukan angka 37 s yang di-hardcode.

Yang dihitung hanya statistik aplikasi:

- `PingApp`: `Pings sent`, `pingRxSeq:count`, `rtt:histogram`
- `UdpBasicApp` / `UdpSink`: `packetSent:*`, `packetReceived:*`

Paket kontrol AODV/GPSR tidak dipakai.

---

## 8. Hasil

Nilai dari `hasil/qos_summary.csv` (sudah dicocokkan dengan `.sca`).

### Map A

| Metrik | AODV | GPSR |
|---|---|---|
| Packet Loss (V2V Ping) | 89,47 % | 94,74 % |
| RTT min / avg / max (ms) | 45,673 / 482,451 / 1045,328 | 1,426 / 2,146 / 2,867 |
| PDR (V2V UDP) | 10,53 % | 5,26 % |
| Throughput (kbps) | 0,443 | 0,221 |

### Map B

| Metrik | AODV | GPSR |
|---|---|---|
| Packet Loss (V2V Ping) | 47,37 % | 28,95 % |
| RTT min / avg / max (ms) | 1,115 / 22,631 / 415,726 | 1,088 / 1,400 / 2,256 |
| PDR (V2V UDP) | 52,63 % | 68,42 % |
| Throughput (kbps) | 2,214 | 2,878 |

### Cara membaca

- Setiap protokol mengirim 38 paket per run.
- Map A: AODV menerima 4 ping dan 4 paket UDP; GPSR menerima 2 ping dan 2 paket UDP.
- Map B: AODV menerima 20 ping dan 20 paket UDP; GPSR menerima 27 ping dan 26 paket UDP.
- Packet Loss dan PDR berasal dari **dua run berbeda** (Ping vs UDP), bukan
  himpunan paket yang sama.
- RTT Map A GPSR hanya berdasarkan 2 sampel; RTT Map B lebih banyak sampel.
- Rendahnya delivery di Map A adalah sifat skenario lama: pasangan kendaraan
  berjarak sekitar 280 m, sedangkan jangkauan radio sekitar 228 m (lihat
  `docs/PRAKTIKUM8_GPSR_MAP_B.md`).
- Pada data ini GPSR lebih baik di Map B, tetapi ini **satu run, satu seed**.
  Jangan menyimpulkan keunggulan umum algoritma dari satu skenario.

---

## 9. Cara menjalankan ulang simulasi Map B

Gunakan `--result-dir` agar output tidak menimpa hasil Map A. OMNeT++ menerima
`--result-dir` sebagai configuration option.

```bash
cd vanet_aodv
mkdir -p ../qos_modul10/data/map_b_aodv/raw
./run_cmd.sh AODV_V2V_Ping 40s --map b --result-dir=../qos_modul10/data/map_b_aodv/raw
./run_cmd.sh AODV_V2V_UDP  40s --map b --result-dir=../qos_modul10/data/map_b_aodv/raw

cd ../vanet_gpsr
mkdir -p ../qos_modul10/data/map_b_gpsr/raw
./run_cmd.sh GPSR_V2V_Ping 40s --map b --result-dir=../qos_modul10/data/map_b_gpsr/raw
./run_cmd.sh GPSR_V2V_UDP  40s --map b --result-dir=../qos_modul10/data/map_b_gpsr/raw
```

Setelah run:

1. Pindahkan hasil dari `raw/` ke `data/map_b_aodv/` atau `data/map_b_gpsr/`.
2. Perbarui `data/manifest.json` (run ID, datetime, sha256, jumlah node).
3. Jalankan ulang:

```bash
cd qos_modul10
python3 scripts/extract_qos.py
python3 scripts/plot_qos_charts.py
python3 scripts/validate_qos.py
```

`extract_qos.py` menolak file jika sha256 tidak cocok dengan manifest. Ini
sengaja untuk mencegah tertukarnya data antar kombinasi.

---

## 10. Panduan singkat untuk mahasiswa (Praktikum 10)

1. **Siapkan hasil simulasi.** Jalankan kombinasi yang ditugaskan
   (Map A/B × AODV/GPSR, V2V Ping dan V2V UDP, 40 s) dengan `run_cmd.sh`.
2. **Salin hasil.** Letakkan `.sca` ke folder `data/<peta>_<algoritma>/`.
   Jangan menimpa hasil kombinasi lain.
3. **Catat provenance.** Isi `manifest.json`: run ID, launch config, jumlah
   kendaraan, seed, durasi, sha256.
4. **Ekstraksi.** Jalankan `python3 scripts/extract_qos.py`, lalu buka
   `hasil/qos_summary.csv`. Periksa bahwa `map`, `algorithm`, dan
   `launch_config` sesuai.
5. **Grafik.** Jalankan `python3 scripts/plot_qos_charts.py`. Buka PNG di
   `grafik/<peta>/`. Pastikan judul, satuan, dan nilai terbaca.
6. **Validasi.** Jalankan `python3 scripts/validate_qos.py`. Baca
   `hasil/validasi.md`; semua pemeriksaan harus lulus.
7. **Interpretasi.** Bandingkan AODV vs GPSR pada peta yang sama. Sebutkan
   jumlah run/seed dan jangan menggeneralisasi dari satu skenario.

### Fungsi setiap script

| Script | Input | Fungsi | Output |
|---|---|---|---|
| `extract_qos.py` | `data/manifest.json` + `.sca` | parse statistik aplikasi, hitung QoS, cek sha256 | `hasil/qos_summary.csv` |
| `plot_qos_charts.py` | `hasil/qos_summary.csv` | grafik batang AODV vs GPSR, 300 DPI | `grafik/<peta>/*.png` |
| `validate_qos.py` | CSV + `.sca` + manifest | hitung ulang, cek rentang, konsistensi konfigurasi | `hasil/validasi.md` |

---

## 11. Troubleshooting

| Gejala | Penyebab | Solusi |
|---|---|---|
| `ModuleNotFoundError: pandas` | dependensi belum ada | `python3 -m pip install pandas matplotlib` (minta izin lab) |
| `ERROR: .../qos_summary.csv not found` | ekstraksi belum dijalankan | jalankan `extract_qos.py` lebih dulu |
| `missing data file` | salinan `.sca` tidak ada | pulihkan dari `SOURCE.md` atau jalankan ulang simulasi |
| `sha256 mismatch` | file berubah / tertukar | salin ulang file asli, perbarui manifest |
| Grafik kosong / tidak terbuka | CSV tidak valid | cek `qos_summary.csv`, jalankan validasi |
| `--result-dir` tidak membuat folder | folder belum ada | `mkdir -p` seperti pada §9 |

---

## 12. Batasan

- Tidak mengubah konfigurasi AODV/GPSR, Map A, atau Map B.
- Tidak menghapus atau memindahkan hasil Praktikum 8/9.
- Tidak memakai angka ilustratif atau data sintetis.
- Tidak mengklaim satu algoritma lebih unggul dari satu run/satu seed.
- Modul ini tidak melakukan commit atau push otomatis.

---

## 13. Catatan efisiensi (audit 2026-11-20)

- Parser `.sca` hanya membaca baris yang relevan: `bin`, `attr` yang tidak
  dipakai, dan `par` yang tidak dipakai dilewati sebelum parsing string.
  Pada mesin ini, ekstraksi 8 file turun dari sekitar 28 s menjadi sekitar
  1,3 s.
- `validate_qos.py` memakai cache hasil parse untuk pemeriksaan konsistensi,
  sehingga file Ping tidak diparse dua kali. Waktu validasi sekitar 1,2 s untuk
  150 pemeriksaan.
- Pembuatan grafik sekitar 5,5 s untuk 8 PNG 300 DPI; sebagian besar waktu
  berasal dari rendering Matplotlib, bukan pengolahan data.
- Pipeline QoS hanya membaca `.sca`. File `.vec`/`.vci` disimpan sebagai arsip
  dan tidak memengaruhi waktu ekstraksi.
