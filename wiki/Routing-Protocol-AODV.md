# 🧭 Protokol Routing AODV (RFC 3561)

Dokumen ini membedah mekanisme kerja protokol **Ad hoc On-Demand Distance Vector (AODV)** sesuai standar **RFC 3561**, penerapannya dalam lingkungan mobilitas kendaraan tinggi (*VANET*), serta parameter-parameter konfigurasinya pada INET Framework.

---

## 1. Konsep Dasar AODV

AODV adalah protokol routing **reaktif (on-demand)**. Berbeda dengan protokol proaktif (seperti OLSR atau DSDV) yang terus-menerus memelihara seluruh rute ke setiap tujuan melalui pesan pertukaran topologi periodik, AODV **hanya mencari rute saat ada paket aplikasi yang hendak dikirim**.

Karakteristik reaktif ini sangat menguntungkan di lingkungan VANET karena:
1. **Topologi Sangat Dinamis**: Kecepatan tinggi mobil menyebabkan rute cepat kedaluwarsa (*stale*). Memelihara rute ke semua mobil secara proaktif akan membuang-buang bandwidth frekuensi 5.9 GHz.
2. **Efisiensi Bandwidth**: Mengurangi *overhead* transmisi kontrol jika komunikasi hanya terjadi sesekali antar kendaraan tertentu.
3. **Bebas Perulangan (*Loop-Free*)**: Menjamin tidak terjadi *routing loop* berkat pemanfaatan **Destination Sequence Number (DestSeqNum)**.

---

## 2. Siklus Hidup Rute AODV

```
               [Fase 1: ROUTE DISCOVERY]
  Sumber (Src) ─── RREQ Broadcast (Multi-Hop) ───► Tujuan (Dst)
  Sumber (Src) ◄─── RREP Unicast (Reverse Path) ── Tujuan (Dst)

               [Fase 2: TRANSMISI DATA]
  Sumber (Src) ═══════════ Paket Data ═══════════► Tujuan (Dst)

               [Fase 3: ROUTE MAINTENANCE]
  (Node putus akibat mobilitas menjauh)
  Forwarder ────── RERR (Route Error) ───────────► Sumber (Src)
```

---

### A. Penemuan Rute (*Route Discovery*)

Ketika sebuah node sumber (misal `node[0]`) ingin mengirim data ke node tujuan (`node[1]`), namun tidak memiliki entri rute yang valid di tabel routing-nya:

1. **Pembuatan RREQ (Route Request)**:
   - Node sumber membuat paket `RREQ` yang berisi:
     - `Source IP` & `Source Sequence Number`
     - `Broadcast ID` (dinaikkan setiap kali membuat RREQ baru)
     - `Destination IP` & `Last Known Destination Sequence Number`
     - `Hop Count = 0`
   - Paket RREQ disiarkan (*broadcast*) ke seluruh tetangga dalam radius jangkauan 1-hop.

2. **Pembentukan Reverse Path (Jalur Balik)**:
   - Setiap node tetangga yang menerima RREQ memeriksa pasangan `(Source IP, Broadcast ID)`. Jika sudah pernah diproses, paket diabaikan (*discard duplicate*).
   - Node pencatat membuat entri **Reverse Path** di tabel routing-nya: mencatat alamat pengirim hop sebelumnya sebagai jalur untuk kembali ke sumber.
   - Hop Count dinaikkan 1. Jika node tersebut bukan tujuan dan tidak memiliki rute segar ke tujuan, ia menyiarkan ulang (*re-broadcast*) paket RREQ tersebut.

3. **Pembuatan RREP (Route Reply)**:
   - Ketika RREQ tiba di tujuan (`node[1]`), tujuan menaikkan `Destination Sequence Number` miliknya.
   - Node tujuan membuat paket `RREP` dan mengirimkannya secara **unicast** menyusuri *Reverse Path* yang telah terbentuk.
   - Setiap node perantara yang meneruskan RREP membentuk entri **Forward Path** menuju tujuan di tabel routing-nya.
   - Begitu RREP tiba di sumber, transmisi paket data aplikasi langsung dimulai.

---

### B. Mekanisme Expanding Ring Search

Untuk mencegah banjir paket RREQ ke seluruh jaringan kota jika tujuan ternyata berada dekat dengan sumber, AODV menerapkan algoritma **Expanding Ring Search**:

1. AODV memulai siaran RREQ pertama dengan nilai TTL (*Time To Live*) kecil:
   $$\text{TTL}_{start} = 2$$
2. Jika balasan RREP tidak diterima dalam jendela waktu tertentu, TTL dinaikkan secara bertahap:
   $$\text{TTL}_{next} = \text{TTL}_{prev} + \text{TTL}_{increment} \quad (\text{TTL}_{increment} = 2)$$
3. Proses berulang hingga mencapai batas ambang:
   $$\text{TTL}_{threshold} = 7$$
4. Jika masih belum ditemukan rute pada $\text{TTL}_{threshold}$, RREQ disiarkan ke seluruh diameter jaringan:
   $$\text{TTL} = \text{NetDiameter} = 30$$

---

### C. Pemeliharaan Rute (*Route Maintenance & Error Handling*)

Tantangan terbesar VANET adalah tingginya mobilitas mobil yang menyebabkan *link breakage* (putusnya sambungan antar mobil yang saling menjauh keluar dari radius jangkauan).

1. **Deteksi Link Putus**:
   - Terdeteksi ketika transmisi frame MAC 802.11p gagal menerima sinyal ACK setelah mencapai batas maksimum *retry*.
   - Atau (jika diaktifkan) terdeteksi saat tidak menerima paket *AODV HELLO* dari tetangga selama batas waktu tertentu.
2. **Penyebaran Pesan RERR (Route Error)**:
   - Node yang mendeteksi putusnya sambungan menandai entri rute sebagai *invalid*.
   - Node tersebut mengirimkan paket `RERR` yang berisi daftar IP tujuan yang tidak lagi dapat dijangkau ke seluruh node perantara sebelumnya (*precursor list*).
3. **Perbaikan Rute (Local Repair / Re-discovery)**:
   - Node sumber yang menerima RERR membatalkan rute lama dan dapat memulai inisiasi *Route Discovery* baru.

---

## 3. Fitur Pesan HELLO (RFC 3561) vs Link Layer Feedback

Pada berkas `omnetpp.ini`, terdapat skenario khusus `[Config AODV_HelloMessages]` untuk menguji dampak fitur pesan periodik HELLO:

```ini
[Config AODV_HelloMessages]
extends = AODV_V2V_UDP
**.aodv.useHelloMessages = true
**.aodv.helloInterval = 1s
**.aodv.allowedHelloLoss = 2
**.aodv.activeRouteTimeout = 3s
```

| Parameter Perbandingan | Tanpa Hello Messages (Default `omnetpp.ini`) | Dengan Hello Messages (`AODV_HelloMessages`) |
|---|---|---|
| **Metode Deteksi Tetangga** | Mengandalkan *MAC layer acknowledgment* (802.11p ACK failure). | Siaran berkala paket kontrol HELLO setiap $1\text{ detik}$. |
| **Beban Kanal (*Channel Overhead*)** | Sangat rendah. Kanal nirkabel hanya terpakai saat ada trafik data nyata. | Bertambah secara proporsional terhadap jumlah kendaraan aktif di jalan. |
| **Kecepatan Deteksi Putus** | Sangat cepat saat sedang aktif mengirimkan paket data. | Bergantung pada interval: $2 \times \text{helloInterval} = 2\text{ detik}$. |
| **Rekomendasi di Lingkungan VANET** | Dianjurkan untuk jaringan padat agar spektrum radio tidak jenuh oleh siaran kontrol. | Bermanfaat untuk evaluasi riset *neighbor sensing* dan pemantauan topologi. |

---

## 4. Rangkuman Parameter Konfigurasi AODV di INET

Berikut adalah parameter implementasi AODV pada proyek ini yang tertuang di `vanet_aodv/omnetpp.ini`:

```ini
##########################################################
#             AODV Routing Protocol Parameters           #
##########################################################
**.aodv.interface = "wlan0"
**.aodv.activeRouteTimeout = 3s
**.aodv.useHelloMessages = false
**.aodv.askGratuitousRREP = false
**.aodv.destinationOnlyFlag = false
**.aodv.rreqRetries = 3
**.aodv.rreqRatelimit = 20
**.aodv.rerrRatelimit = 20
**.aodv.ttlStart = 2
**.aodv.ttlIncrement = 2
**.aodv.ttlThreshold = 7
**.aodv.netDiameter = 30
**.aodv.nodeTraversalTime = 0.05s
```

### Arti Fungsional Parameter:
- **`activeRouteTimeout = 3s`**: Masa kedaluwarsa rute aktif. Jika sebuah rute tidak dilalui paket data selama 3 detik, rute dinyatakan tidak aktif (*expired*). Mengingat kendaraan bergerak cepat, nilai 3 detik ideal mencegah penggunaan rute lapuk.
- **`rreqRetries = 3`**: Jumlah percobaan ulang siaran RREQ sebelum menyatakan tujuan tidak dapat dihubungi.
- **`rreqRatelimit = 20`**: Pembatasan laju pengiriman paket RREQ maksimal 20 paket per detik untuk mencegah *broadcast storm problem*.
- **`nodeTraversalTime = 0.05s`**: Estimasi konservatif waktu perambatan paket melintasi 1 hop node ($50\text{ ms}$), digunakan untuk mengkalkulasi waktu tunggu timeout balasan RREP.
