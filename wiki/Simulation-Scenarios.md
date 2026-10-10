# 🧪 Panduan Skenario Simulasi

Dokumen ini menjelaskan secara rinci keempat skenario studi kasus operasional VANET yang didefinisikan dalam berkas `vanet_aodv/omnetpp.ini`.

---

## 1. Ikhtisar Skenario Pengujian

Semua skenario dibangun di atas modul topologi jaringan `vanet_aodv.Scenario` dan mewarisi konfigurasi global `[General]`:

```
                           ┌───────────────────────────┐
                           │      [Config General]     │
                           │   Radio 5.9GHz, Visual,   │
                           │     AODV Base, TraCI      │
                           └─────────────┬─────────────┘
                                         │
         ┌───────────────────────────────┼───────────────────────────────┐
         ▼                               ▼                               ▼
┌──────────────────┐            ┌──────────────────┐            ┌──────────────────┐
│  AODV_V2V_Ping   │            │   AODV_V2V_UDP   │            │   AODV_V2I_RSU   │
│  V2V Ping (ICMP) │            │  V2V Stream UDP  │            │  V2I Telemetri   │
└──────────────────┘            └────────┬─────────┘            └──────────────────┘
                                         │ extends
                                         ▼
                                ┌──────────────────┐
                                │AODV_HelloMessages│
                                │  UDP + HELLO Msg │
                                └──────────────────┘
```

---

## 2. Bedah Teknis Skenario

---

### Skenario 1: `[Config AODV_V2V_Ping]`
*Pengujian Penemuan Rute Bolak-Balik (Round-Trip Route Discovery) Menggunakan ICMP*

```ini
[Config AODV_V2V_Ping]
description = "Simulasi routing AODV V2V menggunakan Ping (ICMP) antar kendaraan bergerak"

*.node[0].numApps = 1
*.node[0].app[0].typename = "PingApp"
*.node[0].app[0].destAddr = "node[1](ipv4)"
*.node[0].app[0].sendInterval = 1s
*.node[0].app[0].startTime = 3s
*.node[0].app[0].stopTime = 80s
*.node[0].app[0].printPing = true

*.node[*].numApps = 0
```

#### Alur & Karakteristik:
1. **Pengirim (`node[0]`)**: Mengirim paket ICMP Echo Request berukuran $56\text{ Byte}$ setiap $1\text{ detik}$ ke Mobil 1.
2. **Penerima (`node[1]`)**: Merespons dengan paket ICMP Echo Reply.
3. **Node Perantara (`node[2..N]`)**: Beroperasi murni sebagai *router forwarder* AODV.
4. **Tujuan Evaluasi**:
   - Memvalidasi pembentukan rute simetris dua arah (maju dan mundur).
   - Mengukur latensi inisiasi rute pertama kali (saat RREQ/RREP berlangsung).
   - Mengamati fluktuasi latensi *Round-Trip Time* (RTT) saat kedua mobil saling menjauh di jalan raya.

---

### Skenario 2: `[Config AODV_V2V_UDP]`
*Pengujian Transmisi Data Kontinu Antar Kendaraan Bergerak*

```ini
[Config AODV_V2V_UDP]
description = "Simulasi routing AODV V2V pengiriman paket data UDP antar kendaraan bergerak"

*.node[1].numApps = 1
*.node[1].app[0].typename = "UdpSink"
*.node[1].app[0].localPort = 5000

*.node[0].numApps = 1
*.node[0].app[0].typename = "UdpBasicApp"
*.node[0].app[0].destAddresses = "node[1](ipv4)"
*.node[0].app[0].destPort = 5000
*.node[0].app[0].messageLength = 512B
*.node[0].app[0].sendInterval = 1s
*.node[0].app[0].startTime = 3s
*.node[0].app[0].stopTime = 80s

*.node[*].numApps = 0
```

#### Alur & Karakteristik:
1. **Aliran Data Satu Arah**: Mobil 0 secara kontinu mengirim paket data UDP sebesar $512\text{ Byte}$ ke Mobil 1 pada port 5000.
2. **Uji Ketahanan Rute Dinamis**: Berbeda dengan ICMP ping yang menunggu balasan, UDP terus menyemprotkan data. Jika mobil perantara berbelok di persimpangan dan memutus rute, paket data akan tertahan di buffer AODV sementara proses *Local Repair* atau *RREQ rediscovery* dipicu.
3. **Tujuan Evaluasi**:
   - Mengukur *Packet Delivery Ratio* (PDR): persentase paket yang berhasil sampai ke `UdpSink`.
   - Mengukur *Throughput* rata-rata ($kbps$).
   - Menganalisis *packet drop* saat transisi putus-sambung rute (*route link breakage*).

---

### Skenario 3: `[Config AODV_V2I_RSU]`
*Pengujian Komunikasi Kendaraan-ke-Infrastruktur (Telemetri Cerdas Kota)*

```ini
[Config AODV_V2I_RSU]
description = "Simulasi routing AODV V2I ke Road-Side Unit (RSU) statis"

*.numRsu = 1

*.rsu[0].mobility.typename = "StationaryMobility"
*.rsu[0].mobility.initialX = 1025m
*.rsu[0].mobility.initialY = 870m
*.rsu[0].mobility.initialZ = 5m
*.rsu[0].mobility.initFromDisplayString = false

*.rsu[0].wlan[0].radio.transmitter.power = 100mW

*.rsu[0].numApps = 1
*.rsu[0].app[0].typename = "UdpSink"
*.rsu[0].app[0].localPort = 5000

*.node[*].numApps = 1
*.node[*].app[0].typename = "UdpBasicApp"
*.node[*].app[0].destAddresses = "rsu[0](ipv4)"
*.node[*].app[0].destPort = 5000
*.node[*].app[0].messageLength = 256B
*.node[*].app[0].sendInterval = uniform(2s, 4s)
*.node[*].app[0].startTime = uniform(2s, 5s)
```

#### Alur & Karakteristik:
1. **RSU Terpusat**: Ditempatkan di titik koordinat persimpangan strategis $(X=1025\text{m}, Y=870\text{m})$ dengan daya pancar tinggi $100\text{ mW}$ ($\approx 718\text{ m}$ radius).
2. **Pelaporan Masal (*Many-to-One*)**: Seluruh armada mobil (`node[*]`) yang melintas di jalan raya secara periodik ($2 \sim 4\text{ detik}$) mengirimkan paket telemetri status kendaraan ($256\text{ Byte}$) menuju RSU.
3. **Tujuan Evaluasi**:
   - Menguji performa routing saat banyak sumber secara serentak mencari rute ke tujuan yang sama (*Hotspot Destination*).
   - Mengamati degradasi performa akibat tabrakan paket (*packet collision*) di sekitar zona RSU.
   - Mengukur area cakupan efektif layanan infrastruktur pintar.

---

### Skenario 4: `[Config AODV_HelloMessages]`
*Evaluasi Dampak Protokol HELLO Periodik terhadap Routing Overhead*

```ini
[Config AODV_HelloMessages]
extends = AODV_V2V_UDP
description = "AODV dengan HELLO message periodik (RFC 3561) untuk pemeliharaan tetangga"

**.aodv.useHelloMessages = true
**.aodv.helloInterval = 1s
**.aodv.allowedHelloLoss = 2
**.aodv.activeRouteTimeout = 3s
```

#### Alur & Karakteristik:
1. Mewarisi seluruh pengaturan `AODV_V2V_UDP`, namun mengaktifkan transmisi broadcast berkala paket *AODV HELLO*.
2. Setiap node menyiarkan pesan HELLO setiap $1\text{ detik}$. Jika tetangga tidak mengirim HELLO selama $2 \times 1\text{s} = 2\text{ detik}$, rute langsung diputus tanpa menunggu kegagalan pengiriman paket data MAC.
3. **Tujuan Evaluasi**:
   - Membandingkan konsumsi *bandwidth* kontrol (*Routing Overhead*) antara mekanisme berbasis HELLO vs berbasis umpan balik ACK MAC layer.
   - Mengamati apakah deteksi tetangga yang lebih proaktif mampu mempercepat pemulihan rute atau justru membebani kanal nirkabel.

---

## 3. Matriks Perbandingan Parameter Skenario

| Parameter | `AODV_V2V_Ping` | `AODV_V2V_UDP` | `AODV_V2I_RSU` | `AODV_HelloMessages` |
|---|:---:|:---:|:---:|:---:|
| **Pola Komunikasi** | V2V (1 ke 1) | V2V (1 ke 1) | V2I ($N$ ke 1) | V2V (1 ke 1) |
| **Protokol Lapisan 4** | ICMP | UDP | UDP | UDP |
| **Ukuran Payload** | $56\text{ Byte}$ | $512\text{ Byte}$ | $256\text{ Byte}$ | $512\text{ Byte}$ |
| **Interval Pengiriman** | $1{,}0\text{s}$ tetap | $1{,}0\text{s}$ tetap | `uniform(2s, 4s)` | $1{,}0\text{s}$ tetap |
| **Jumlah RSU Aktif** | $0$ | $0$ | $1$ | $0$ |
| **Pesan AODV HELLO** | Nonaktif | Nonaktif | Nonaktif | **Aktif ($1\text{s}$)** |
| **Fokus Evaluasi** | RTT & Loss Latency | PDR & Throughput | Skalabilitas Jaringan | Overhead Kontrol Kanal |
