# 📚 VANET-AODV Simulation Wiki

Selamat datang di dokumentasi resmi (**Wiki**) proyek **VANET-AODV**. Wiki ini berisi panduan teknis mendalam mengenai arsitektur, konfigurasi protokol, teori perambatan radio, manajemen lalu lintas mobilitas, hingga teknik analisis data simulasi.

---

## 🧭 Navigasi Wiki

| Dokumen | Topik & Cakupan |
|---|---|
| [**1. Arsitektur & Desain Sistem**](Architecture-and-Design.md) | Integrasi 4 komponen simulator (OMNeT++, INET, Veins, SUMO), hierarki modul NED (`Scenario`, `VeinsAodvCar`, `VeinsAodvRSU`), dan protokol TraCI. |
| [**2. Protokol Routing AODV**](Routing-Protocol-AODV.md) | Mekanisme RFC 3561 dalam lingkungan vehicular (RREQ, RREP, RERR, Gratuitous RREP, Expanding Ring Search, serta HELLO Messages). |
| [**3. Lapisan Fisik & MAC (IEEE 802.11p)**](Physical-and-MAC-Layers.md) | Frekuensi DSRC 5.9 GHz, modulasi OFDM, model redaman *Free-Space Path Loss*, kalkulasi radius transmisi, dan konfigurasi antena. |
| [**4. Mobilitas Lalu Lintas & Peta Jalan**](Traffic-Mobility-and-Map.md) | Ekstraksi OpenStreetMap, sistem koordinat UTM, file rute SUMO (`maps.rou.xml`), serta skrip otomasi skala kendaraan `set_nodes.py`. |
| [**5. Panduan Skenario Simulasi**](Simulation-Scenarios.md) | Penjelasan teknis mendalam 4 skenario benchmark (`AODV_V2V_Ping`, `AODV_V2V_UDP`, `AODV_V2I_RSU`, dan `AODV_HelloMessages`). |
| [**6. Panduan Visualisasi Grafis (Qtenv)**](GUI-and-Visualization-Guide.md) | Arti semantik visual: lingkaran jangkauan radio (biru), link MAC 1-hop (emas), rute AODV (hijau), dan filter rambatan gelombang imajiner. |
| [**7. Analisis Data & Metrik Evaluasi**](Data-Analysis-and-Metrics.md) | Metrik performa jaringan (PDR, Latensi RTT, Throughput, Routing Overhead), ekstraksi data skalar (`.sca`) dan vektor (`.vec`). |
| [**8. Panduan Eksekusi & Troubleshooting**](Getting-Started-and-Troubleshooting.md) | Instalasi dependensi, eksekusi mode terminal/GUI, dan solusi terhadap kendala teknis umum. |

---

## 🔍 Ikhtisar Ekosistem

Proyek ini menggabungkan ekosistem perangkat lunak riset standar industri:

```
+-------------------------------------------------------------------------+
|                              Eclipse SUMO                               |
|       (Simulasi Mikro Lalu Lintas: Rute, Kendaraan, Kecepatan, Lajur)   |
+-----------------------------------+-------------------------------------+
                                    | TraCI TCP Socket (:9999)
                                    v
+-------------------------------------------------------------------------+
|                                 Veins                                   |
|      (Sinkronisasi Posisi Kendaraan + IEEE 802.11p WAVE Foundation)     |
+-----------------------------------+-------------------------------------+
                                    | VeinsInetMobility
                                    v
+-------------------------------------------------------------------------+
|                           INET Framework 4.5                            |
|  - Lapisan Aplikasi   : PingApp, UdpBasicApp, UdpSink                   |
|  - Lapisan Routing    : AODV Router (RFC 3561)                          |
|  - Lapisan Network    : IPv4 Stack (10.0.0.0/8), Global ARP             |
|  - Lapisan Link/MAC   : IEEE 802.11p NIC                                |
|  - Lapisan Fisik      : Ieee80211DimensionalRadio (5.9 GHz DSRC)        |
+-----------------------------------+-------------------------------------+
                                    | Discrete Event Engine
                                    v
+-------------------------------------------------------------------------+
|                               OMNeT++ 6.4                               |
|                   (Kernel Simulasi & Visualizer Qtenv)                  |
+-------------------------------------------------------------------------+
```

---

## 💡 Rekomendasi Alur Belajar

1. Pelajari [Arsitektur & Desain Sistem](Architecture-and-Design.md) untuk memahami bagaimana OMNeT++ dan SUMO berkomunikasi.
2. Pahami konsep [Protokol Routing AODV](Routing-Protocol-AODV.md) dan bagaimana mobilitas kendaraan mempengaruhi pemeliharaan rute.
3. Telaah [Lapisan Fisik & MAC](Physical-and-MAC-Layers.md) untuk memahami perhitungan matematis jangkauan sinyal mobil.
4. Pilih skenario pada [Panduan Skenario Simulasi](Simulation-Scenarios.md) dan jalankan menggunakan [Panduan Eksekusi](Getting-Started-and-Troubleshooting.md).
5. Analisis metrik output simulasi menggunakan [Analisis Data & Metrik Evaluasi](Data-Analysis-and-Metrics.md).
