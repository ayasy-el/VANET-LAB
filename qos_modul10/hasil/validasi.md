# Laporan Validasi QoS — Modul Praktikum 10

Dibuat: 2026-11-26 12:57:53

Python: 3.12.3 | CSV: `hasil/qos_summary.csv`

## 1. Ringkasan

- Pemeriksaan dijalankan: **150**
- Lulus: **150**
- Gagal: **0**
- Kombinasi tidak tersedia: **0**

> Semua pemeriksaan lulus. Delapan grafik (4 Map A + 4 Map B) dibuat dari data yang tervalidasi.

## 2. Provenance data

| Peta | Algoritma | Skenario | File | Run ID | Launch config | Node | Seed | Durasi (s) |
|---|---|---|---|---|---|---|---|---|
| Map A | AODV | ping | AODV_V2V_Ping-#0.sca | AODV_V2V_Ping-0-20261106-13:30:29-2652 | maps.launchd.xml | 20 | 0 | 40 |
| Map A | AODV | udp | AODV_V2V_UDP-#0.sca | AODV_V2V_UDP-0-20261106-13:33:25-3022 | maps.launchd.xml | 20 | 0 | 40 |
| Map A | GPSR | ping | GPSR_V2V_Ping-#0.sca | GPSR_V2V_Ping-0-20261112-12:36:31-2556 | maps.launchd.xml | 20 | 0 | 40 |
| Map A | GPSR | udp | GPSR_V2V_UDP-#0.sca | GPSR_V2V_UDP-0-20261112-12:38:00-3298 | maps.launchd.xml | 20 | 0 | 40 |
| Map B | AODV | ping | AODV_V2V_Ping-#0.sca | AODV_V2V_Ping-0-20261120-13:30:59-5942 | map2.launchd.xml | 80 | 0 | 40 |
| Map B | AODV | udp | AODV_V2V_UDP-#0.sca | AODV_V2V_UDP-0-20261120-13:31:18-5984 | map2.launchd.xml | 80 | 0 | 40 |
| Map B | GPSR | ping | GPSR_V2V_Ping-#0.sca | GPSR_V2V_Ping-0-20261120-13:31:28-6009 | map2.launchd.xml | 80 | 0 | 40 |
| Map B | GPSR | udp | GPSR_V2V_UDP-#0.sca | GPSR_V2V_UDP-0-20261120-13:31:57-6043 | map2.launchd.xml | 80 | 0 | 40 |

## 3. Nilai CSV vs statistik .sca

| Kombinasi | Skenario | Metrik | CSV | Hitung ulang dari .sca | Selisih |
|---|---|---|---|---|---|
| map_a_aodv | ping | Pings sent | 38.0000 | 38.0000 | 0.000000 |
| map_a_aodv | ping | Pings received | 4.0000 | 4.0000 | 0.000000 |
| map_a_aodv | ping | Packet loss (%) | 89.4737 | 89.4737 | 0.000016 |
| map_a_aodv | ping | Recorded loss (%) | 89.4737 | 89.4737 | 0.000016 |
| map_a_aodv | ping | RTT min (ms) | 45.6728 | 45.6728 | 0.000044 |
| map_a_aodv | ping | RTT avg (ms) | 482.4513 | 482.4513 | 0.000003 |
| map_a_aodv | ping | RTT max (ms) | 1045.3283 | 1045.3283 | 0.000002 |
| map_a_aodv | udp | Tx packets | 38.0000 | 38.0000 | 0.000000 |
| map_a_aodv | udp | Rx packets | 4.0000 | 4.0000 | 0.000000 |
| map_a_aodv | udp | PDR (%) | 10.5263 | 10.5263 | 0.000016 |
| map_a_aodv | udp | Tx bytes | 19456.0000 | 19456.0000 | 0.000000 |
| map_a_aodv | udp | Rx bytes | 2048.0000 | 2048.0000 | 0.000000 |
| map_a_aodv | udp | Window (s) | 37.0000 | 37.0000 | 0.000000 |
| map_a_aodv | udp | Throughput (kbps) | 0.4428 | 0.4428 | 0.000011 |
| map_a_gpsr | ping | Pings sent | 38.0000 | 38.0000 | 0.000000 |
| map_a_gpsr | ping | Pings received | 2.0000 | 2.0000 | 0.000000 |
| map_a_gpsr | ping | Packet loss (%) | 94.7368 | 94.7368 | 0.000042 |
| map_a_gpsr | ping | Recorded loss (%) | 94.7368 | 94.7368 | 0.000042 |
| map_a_gpsr | ping | RTT min (ms) | 1.4256 | 1.4256 | 0.000043 |
| map_a_gpsr | ping | RTT avg (ms) | 2.1462 | 2.1462 | 0.000046 |
| map_a_gpsr | ping | RTT max (ms) | 2.8668 | 2.8668 | 0.000049 |
| map_a_gpsr | udp | Tx packets | 38.0000 | 38.0000 | 0.000000 |
| map_a_gpsr | udp | Rx packets | 2.0000 | 2.0000 | 0.000000 |
| map_a_gpsr | udp | PDR (%) | 5.2632 | 5.2632 | 0.000042 |
| map_a_gpsr | udp | Tx bytes | 19456.0000 | 19456.0000 | 0.000000 |
| map_a_gpsr | udp | Rx bytes | 1024.0000 | 1024.0000 | 0.000000 |
| map_a_gpsr | udp | Window (s) | 37.0000 | 37.0000 | 0.000000 |
| map_a_gpsr | udp | Throughput (kbps) | 0.2214 | 0.2214 | 0.000005 |
| map_b_aodv | ping | Pings sent | 38.0000 | 38.0000 | 0.000000 |
| map_b_aodv | ping | Pings received | 20.0000 | 20.0000 | 0.000000 |
| map_b_aodv | ping | Packet loss (%) | 47.3684 | 47.3684 | 0.000021 |
| map_b_aodv | ping | Recorded loss (%) | 47.3684 | 47.3684 | 0.000021 |
| map_b_aodv | ping | RTT min (ms) | 1.1153 | 1.1153 | 0.000030 |
| map_b_aodv | ping | RTT avg (ms) | 22.6311 | 22.6311 | 0.000029 |
| map_b_aodv | ping | RTT max (ms) | 415.7260 | 415.7260 | 0.000046 |
| map_b_aodv | udp | Tx packets | 38.0000 | 38.0000 | 0.000000 |
| map_b_aodv | udp | Rx packets | 20.0000 | 20.0000 | 0.000000 |
| map_b_aodv | udp | PDR (%) | 52.6316 | 52.6316 | 0.000021 |
| map_b_aodv | udp | Tx bytes | 19456.0000 | 19456.0000 | 0.000000 |
| map_b_aodv | udp | Rx bytes | 10240.0000 | 10240.0000 | 0.000000 |
| map_b_aodv | udp | Window (s) | 37.0000 | 37.0000 | 0.000000 |
| map_b_aodv | udp | Throughput (kbps) | 2.2141 | 2.2141 | 0.000046 |
| map_b_gpsr | ping | Pings sent | 38.0000 | 38.0000 | 0.000000 |
| map_b_gpsr | ping | Pings received | 27.0000 | 27.0000 | 0.000000 |
| map_b_gpsr | ping | Packet loss (%) | 28.9474 | 28.9474 | 0.000032 |
| map_b_gpsr | ping | Recorded loss (%) | 28.9474 | 28.9474 | 0.000032 |
| map_b_gpsr | ping | RTT min (ms) | 1.0875 | 1.0875 | 0.000039 |
| map_b_gpsr | ping | RTT avg (ms) | 1.3998 | 1.3998 | 0.000037 |
| map_b_gpsr | ping | RTT max (ms) | 2.2562 | 2.2562 | 0.000007 |
| map_b_gpsr | udp | Tx packets | 38.0000 | 38.0000 | 0.000000 |
| map_b_gpsr | udp | Rx packets | 26.0000 | 26.0000 | 0.000000 |
| map_b_gpsr | udp | PDR (%) | 68.4211 | 68.4211 | 0.000047 |
| map_b_gpsr | udp | Tx bytes | 19456.0000 | 19456.0000 | 0.000000 |
| map_b_gpsr | udp | Rx bytes | 13312.0000 | 13312.0000 | 0.000000 |
| map_b_gpsr | udp | Window (s) | 37.0000 | 37.0000 | 0.000000 |
| map_b_gpsr | udp | Throughput (kbps) | 2.8783 | 2.8783 | 0.000030 |

## 4. Konsistensi konfigurasi AODV vs GPSR

| Peta | Parameter | AODV | GPSR | Status |
|---|---|---|---|---|
| Map A | launch config | maps.launchd.xml | maps.launchd.xml | OK |
| Map A | vehicle count | 20 | 20 | OK |
| Map A | seedset | 0 | 0 | OK |
| Map A | sim-time-limit | 40 | 40 | OK |
| Map A | radio opMode | p | p | OK |
| Map A | radio type | Ieee80211DimensionalRadio | Ieee80211DimensionalRadio | OK |
| Map A | radio band | 5.9 GHz | 5.9 GHz | OK |
| Map A | radio channel | 3 | 3 | OK |
| Map A | radio bandwidth | 10 MHz | 10 MHz | OK |
| Map A | tx power | 10mW | 10mW | OK |
| Map A | sendInterval | 1s | 1s | OK |
| Map A | startTime | 3s | 3s | OK |
| Map A | stopTime | 80s | 80s | OK |
| Map A | maps.launchd.xml | file AODV | file GPSR | OK (byte-identical) |
| Map A | maps.rou.xml | file AODV | file GPSR | OK (byte-identical) |
| Map A | maps.net.xml | file AODV | file GPSR | OK (byte-identical) |
| Map A | maps.sumocfg | file AODV | file GPSR | OK (byte-identical) |
| Map B | launch config | map2.launchd.xml | map2.launchd.xml | OK |
| Map B | vehicle count | 80 | 80 | OK |
| Map B | seedset | 0 | 0 | OK |
| Map B | sim-time-limit | 40 | 40 | OK |
| Map B | radio opMode | p | p | OK |
| Map B | radio type | Ieee80211DimensionalRadio | Ieee80211DimensionalRadio | OK |
| Map B | radio band | 5.9 GHz | 5.9 GHz | OK |
| Map B | radio channel | 3 | 3 | OK |
| Map B | radio bandwidth | 10 MHz | 10 MHz | OK |
| Map B | tx power | 10mW | 10mW | OK |
| Map B | sendInterval | 1s | 1s | OK |
| Map B | startTime | 3s | 3s | OK |
| Map B | stopTime | 80s | 80s | OK |
| Map B | map2.launchd.xml | file AODV | file GPSR | OK (byte-identical) |
| Map B | map2.rou.xml | file AODV | file GPSR | OK (byte-identical) |
| Map B | map2.net.xml | file AODV | file GPSR | OK (byte-identical) |
| Map B | map2.sumocfg | file AODV | file GPSR | OK (byte-identical) |

## 5. Asal data per grafik

| Grafik | Metrik | Run AODV | Run GPSR | Status |
|---|---|---|---|---|
| map_a_packet_loss.png | Packet Loss | AODV_V2V_Ping-0-20261106-13:30:29-2652 | GPSR_V2V_Ping-0-20261112-12:36:31-2556 | dibuat |
| map_a_avg_rtt.png | Average RTT | AODV_V2V_Ping-0-20261106-13:30:29-2652 | GPSR_V2V_Ping-0-20261112-12:36:31-2556 | dibuat |
| map_a_pdr.png | PDR | AODV_V2V_UDP-0-20261106-13:33:25-3022 | GPSR_V2V_UDP-0-20261112-12:38:00-3298 | dibuat |
| map_a_throughput.png | Throughput | AODV_V2V_UDP-0-20261106-13:33:25-3022 | GPSR_V2V_UDP-0-20261112-12:38:00-3298 | dibuat |
| map_b_packet_loss.png | Packet Loss | AODV_V2V_Ping-0-20261120-13:30:59-5942 | GPSR_V2V_Ping-0-20261120-13:31:28-6009 | dibuat |
| map_b_avg_rtt.png | Average RTT | AODV_V2V_Ping-0-20261120-13:30:59-5942 | GPSR_V2V_Ping-0-20261120-13:31:28-6009 | dibuat |
| map_b_pdr.png | PDR | AODV_V2V_UDP-0-20261120-13:31:18-5984 | GPSR_V2V_UDP-0-20261120-13:31:57-6043 | dibuat |
| map_b_throughput.png | Throughput | AODV_V2V_UDP-0-20261120-13:31:18-5984 | GPSR_V2V_UDP-0-20261120-13:31:57-6043 | dibuat |

## 6. Kombinasi yang belum tersedia

Tidak ada. Keempat kombinasi (Map A/B × AODV/GPSR) tersedia dan tervalidasi.

Delapan grafik dibuat dari data mentah yang tersedia; tidak ada angka pengganti atau data sintetis yang digunakan.

## 7. Catatan interpretasi

- Setiap kombinasi hanya memiliki **satu run** dengan seedset 0. Hasil ini belum cukup untuk menyimpulkan keunggulan algoritma secara umum.
- Packet Loss berasal dari run PingApp; PDR dan throughput berasal dari run UDP (UdpBasicApp/UdpSink), bukan dari paket kontrol AODV/GPSR.
- Pada data Map A ini Packet Loss dan PDR tampak saling melengkapi karena kedua run memakai 38 paket dan jumlah penerimaan yang sama; keduanya tetap berasal dari dua run yang berbeda.
- Throughput memakai jendela pengukuran aktual: dari paket pertama sampai paket terakhir, yaitu (38 − 1) × 1 s = 37 s, bukan 40 s durasi simulasi.
- Menurut dokumentasi Praktikum 8, pasangan kendaraan Map A berjarak sekitar 280 m sedangkan jangkauan radio sekitar 228 m; nilai delivery yang rendah adalah sifat skenario Map A, bukan bukti bahwa satu protokol selalu lebih baik.
