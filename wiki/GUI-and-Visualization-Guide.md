# 🎨 Panduan Visualisasi Grafis (GUI Qtenv)

Dokumen ini menjelaskan konfigurasi dan interpretasi grafis pada simulator interaktif **Qtenv** (OMNeT++), fungsi masing-masing komponen visualizer, serta makna semantik dari garis dan lingkaran yang tampil di layar.

---

## 1. Konfigurasi Visualizer Terpusat (`[General]`)

Pada berkas `vanet_aodv/omnetpp.ini`, seluruh parameter visualisasi diletakkan langsung di dalam blok **`[General]`**. Dengan demikian, visualisasi ini bersifat seragam dan otomatis aktif di semua skenario pengujian tanpa perlu konfigurasi tambahan.

```ini
##########################################################
#                GUI: Tampilan Visual Lengkap            #
##########################################################

# 1. Matikan garis rambatan gelombang imajiner (agar tidak salah paham)
*.visualizer.*.mediumVisualizer.displaySignals = false

# 2. Tampilkan LINGKARAN JANGKAUAN SINYAL NYATA (Radius Communication Range)
*.visualizer.*.mediumVisualizer.displayCommunicationRanges = true
*.visualizer.*.mediumVisualizer.communicationRangeLineColor = "deepskyblue"
*.visualizer.*.mediumVisualizer.communicationRangeLineStyle = "solid"
*.visualizer.*.mediumVisualizer.communicationRangeLineWidth = 1.5

# 3. Tampilkan LINK FISIK / MAC LAYER YANG BENAR-BENAR BERHASIL TERHUBUNG (1-Hop)
*.visualizer.*.dataLinkVisualizer.displayLinks = true
*.visualizer.*.dataLinkVisualizer.lineColor = "gold"
*.visualizer.*.dataLinkVisualizer.lineWidth = 2.5
*.visualizer.*.dataLinkVisualizer.lineStyle = "solid"
*.visualizer.*.dataLinkVisualizer.labelFormat = "%n"
*.visualizer.*.dataLinkVisualizer.labelColor = "darkorange"

# 4. Tampilkan RUTE JARINGAN AODV YANG TERBENTUK (Multi-Hop End-to-End)
*.visualizer.*.networkRouteVisualizer.displayRoutes = true
*.visualizer.*.networkRouteVisualizer.lineColor = "lime"
*.visualizer.*.networkRouteVisualizer.lineWidth = 3.5
*.visualizer.*.networkRouteVisualizer.lineStyle = "solid"
*.visualizer.*.networkRouteVisualizer.labelColor = "forestgreen"
```

---

## 2. Tabel Panduan Elemen Grafis & Makna Semantik

<div align="center">

| Elemen Visual | Simbol / Warna | Modul Visualizer | Makna Semantik & Interpretasi Fisik |
|---|:---:|---|---|
| **Radius Sinyal Fisik** | 🔵 **Lingkaran Biru Langit** (`deepskyblue`) | `mediumVisualizer` | **Area jangkauan radio riil**. Mobil lain yang berada di dalam lingkaran ini dapat mendeteksi sinyal radio pemancar ($P_{rx} \ge -85\text{ dBm}$). |
| **Link Data MAC 1-Hop** | 🟡 **Garis Emas / Kuning** (`gold`, 2.5px) | `dataLinkVisualizer` | **Koneksi fisik tetangga langsung**. Muncul sesaat ketika frame data berhasil dipertukarkan dan diakui (ACK) antar 2 mobil bertetangga. |
| **Rute Multi-Hop AODV** | 🟢 **Garis Hijau Terang** (`lime`, 3.5px) | `networkRouteVisualizer` | **Jalur estafet rute jaringan aktif**. Garis panah tebal yang menghubungkan mobil pengirim, mobil-mobil perantara (*relay*), hingga mobil tujuan. |
| **Peta Jaringan Jalan** | 🟤 **Garis Merah Bata** (`firebrick4`) | `roadsCanvasVisualizer` | **Struktur fisik jalan raya**. Menggambarkan bentuk jalan, percabangan, dan persimpangan dari peta SUMO ke kanvas OMNeT++. |
| **Sinyal Rambatan Merah** | ❌ *(Dinonaktifkan)* | `mediumVisualizer.displaySignals` | **Garis imajiner rumus kalkulasi**. Sebelumnya sering disalahartikan sebagai paket yang sampai ke mobil berjarak 2 km, sehingga sengaja dimatikan. |

</div>

---

## 3. Penjelasan Khusus: Garis Merah `(WirelessSignal)`

### Mengapa Sebelumnya Muncul Garis Merah Panjang Melintasi Peta?
Pada pengaturan bawaan INET, opsi `displaySignals = true` akan menggambar panah merah dari antena pemancar ke **seluruh antena node lain di peta** setiap kali ada transmisi.
- **Tujuan Asli INET**: Visualizer hanya ingin menunjukkan bahwa simulator sedang menghitung rumus pelemahan sinyal (*path loss calculation*) antara antena pengirim dan semua calon penerima di dunia simulasi.
- **Kenyataan Fisik**: Pada jarak di atas 500 meter atau 1 km, sinyal daya pancar $10\text{ mW}$ telah melemah hingga berada jauh di bawah ambang batas sensitivitas (misal $-120\text{ dBm}$), sehingga di mobil penerima sinyal dianggap sebagai *noise* dan **paket langsung dibuang (*dropped*)**.
- **Keputusan Desain**: Garis merah ini **dimatikan secara default (`displaySignals = false`)** agar pandangan pengamat tidak tertutup jaring benang merah yang membingungkan.

---

## 4. Tips Navigasi Interaktif di Antarmuka Qtenv

Saat menjalankan simulasi dengan `./run_gui.sh`, Anda dapat menggunakan berbagai fitur interaktif Qtenv:

1. **Memeriksa Tabel Routing AODV Real-Time**:
   - Klik kanan pada mobil mana saja (misal `node[0]` atau `node[4]`).
   - Pilih menu **Open Component > aodv**.
   - Anda dapat melihat entri tabel routing yang sedang aktif, alamat tujuan, *Next Hop IP*, *Destination Sequence Number*, dan sisa masa berlaku rute (*lifetime*).

2. **Memeriksa Antarmuka Radio & Nilai Daya Terima**:
   - Klik kanan pada `node[*] > wlan[0] > radio`.
   - Pilih **Inspect**.
   - Anda dapat memantau status radio secara langsung (*TRANSMITTING*, *RECEIVING*, *IDLE*), frekuensi kanal yang sedang digunakan, dan daya pancar saat ini.

3. **Mengatur Kecepatan Animasi**:
   - Tombol **Run (F5)**: Menjalankan animasi secara halus (*smooth real-time*).
   - Tombol **Fast (F6)**: Menjalankan animasi lebih cepat dengan tetap menampilkan grafik.
   - Tombol **Express (F7)**: Mematikan render grafis sementara untuk menyelesaikan simulasi dalam kecepatan komputasi maksimum prosesor.
