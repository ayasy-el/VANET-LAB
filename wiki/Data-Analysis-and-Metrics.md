# 📊 Analisis Data & Metrik Evaluasi

Dokumen ini menjelaskan metodologi ekstraksi data hasil simulasi, metrik performa evaluasi protokol routing VANET, serta contoh skrip pengolahan data menggunakan Python dan `opp_scavetool`.

---

## 1. Direktori & Format Berkas Output

Setiap kali simulasi dijalankan (baik via `run_cmd.sh` maupun `run_gui.sh`), data hasil perekaman tersimpan di direktori **`vanet_aodv/results/`**:

- **Berkas Skalar (`*.sca`)**: Menyimpan nilai statistik tunggal ringkasan di akhir simulasi (misalnya: total paket terkirim, total paket diterima, nilai rata-rata RTT, deviasi standar, min, dan max).
- **Berkas Vektor (`*.vec`)**: Menyimpan deret waktu (*time-series event*) dari setiap sinyal yang dicatat (misalnya: RTT tiap paket ke-n pada detik ke-t, fluktuasi throughput per detik).
- **Berkas Indeks Vektor (`*.vci`)**: Indeks biner internal OMNeT++ untuk mempercepat pencarian data pada berkas `.vec`.

---

## 2. Definisi Matematis Metrik Evaluasi

Empat metrik utama yang digunakan untuk mengevaluasi efektivitas protokol AODV di lingkungan VANET:

### A. Packet Delivery Ratio (PDR)
Persentase keberhasilan pengiriman paket dari lapisan aplikasi sumber ke lapisan aplikasi tujuan:

$$\mathbf{\text{PDR} = \left( \frac{\sum \text{Paket Data Diterima}}{\sum \text{Paket Data Dikirim}} \right) \times 100\%}$$

- **Konteks VANET**: Nilai PDR dipengaruhi oleh kepadatan kendaraan (ketersediaan node perantara) dan mobilitas (frekuensi putusnya tautan radio).

### B. End-to-End Latency & Round-Trip Time (RTT)
Waktu tempuh paket dari node pengirim melintasi beberapa hop kendaraan perantara hingga tiba di tujuan (dan kembali untuk ICMP Ping):

$$\mathbf{\text{RTT}_{\text{avg}} = \frac{1}{N} \sum_{i=1}^{N} (t_{\text{reply}, i} - t_{\text{send}, i})}$$

- **Konteks VANET**: Latensi awal biasanya lebih tinggi karena membutuhkan fase *Route Discovery* (RREQ/RREP). Begitu rute terbentuk, paket data berikutnya meluncur jauh lebih cepat.

### C. Throughput Jaringan
Jumlah bit data aplikasi efektif yang berhasil diterima oleh node penerima per satuan waktu:

$$\mathbf{\text{Throughput (kbps)} = \frac{\sum \text{Byte Diterima} \times 8}{(t_{\text{selesai}} - t_{\text{mulai}}) \times 1000}}$$

### D. Normalized Routing Overhead (NRO)
Rasio jumlah paket kontrol routing AODV terhadap jumlah paket data aplikasi yang berhasil dihantarkan:

$$\mathbf{\text{NRO} = \frac{\sum (\text{RREQ} + \text{RREP} + \text{RERR} + \text{HELLO})}{\sum \text{Paket Data Diterima}}}$$

- **Konteks VANET**: Semakin tinggi nilai NRO, semakin banyak kapasitas bandwidth 5.9 GHz yang terbuang hanya untuk lalu lintas kontrol daripada data pengguna.

---

## 3. Ekstraksi Hasil Menggunakan `opp_scavetool`

OMNeT++ menyediakan utilitas baris perintah bawaan bernama `opp_scavetool` untuk mengekspor data hasil simulasi ke format CSV:

```bash
cd vanet_aodv/results

# 1. Ekspor seluruh data skalar ke berkas CSV:
opp_scavetool x -o scalars_summary.csv *.sca

# 2. Ekspor vektor tertentu (misal: RTT ping) ke CSV:
opp_scavetool export -F csv -o rtt_data.csv -f 'name =~ "*rtt*"' *.vec
```

---

## 4. Contoh Skrip Python Analisis PDR & Latensi

Anda dapat menggunakan skrip Python sederhana berikut untuk membaca file `.sca` secara langsung:

```python
#!/usr/bin/env python3
import sys
import re

def parse_sca(filepath):
    sent = 0
    received = 0
    rtt_mean = 0.0

    with open(filepath, 'r') as f:
        for line in f:
            if "packetSent:count" in line:
                match = re.search(r'count\s+(\d+)', line)
                if match:
                    sent += int(match.group(1))
            elif "packetReceived:count" in line:
                match = re.search(r'count\s+(\d+)', line)
                if match:
                    received += int(match.group(1))
            elif "rtt:mean" in line:
                match = re.search(r'mean\s+([\d\.]+)', line)
                if match:
                    rtt_mean = float(match.group(1))

    pdr = (received / sent * 100.0) if sent > 0 else 0.0
    print("=" * 45)
    print(f" Analisis Hasil: {filepath}")
    print("=" * 45)
    print(f" Paket Terkirim : {sent}")
    print(f" Paket Diterima : {received}")
    print(f" PDR            : {pdr:.2f} %")
    if rtt_mean > 0:
        print(f" Rata-rata RTT  : {rtt_mean * 1000:.2f} ms")
    print("=" * 45)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        parse_sca(sys.argv[1])
    else:
        print("Penggunaan: python3 parse_results.py results/<nama_file>.sca")
```
