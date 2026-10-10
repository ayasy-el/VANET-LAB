# 📡 Lapisan Fisik & MAC (IEEE 802.11p)

Dokumen ini menguraikan pemodelan lapisan fisik (*Physical Layer*) dan sublapisan kendali akses media (*MAC Layer*) berbasis standar vehicular **IEEE 802.11p (WAVE / DSRC)** serta turunan matematis dari formula jangkauan propagasi radio.

---

## 1. Standar Nirkabel IEEE 802.11p (DSRC)

Standar IEEE 802.11p merupakan amandemen khusus dari IEEE 802.11 yang dirancang khusus untuk komunikasi di lingkungan transportasi bergerak berkecepatan tinggi:

- **Pita Frekuensi**: DSRC dialokasikan pada spektrum $5{,}850\text{ GHz} - 5{,}925\text{ GHz}$ ($5{,}9\text{ GHz}$).
- **Lebar Saluran (*Channel Bandwidth*)**: Menggunakan lebar pita sempit **$10\text{ MHz}$** (setengah dari pita WiFi biasa $20\text{ MHz}$) untuk mengurangi *Doppler spread* dan distorsi *multipath delay spread*.
- **Modulasi & Physical Layer**: Menggunakan OFDM (*Orthogonal Frequency Division Multiplexing*) dengan 52 sub-pembawa (*subcarriers*).
- **Mekanisme Akses Kanal**: CSMA/CA (*Carrier Sense Multiple Access with Collision Avoidance*) dengan prioritas EDCA (*Enhanced Distributed Channel Access*).

---

## 2. Pemodelan Radio di INET Framework

Pada `vanet_aodv/omnetpp.ini`, lapisan fisik dikonfigurasi menggunakan modul **`Ieee80211DimensionalRadio`** dan **`Ieee80211DimensionalRadioMedium`**:

```ini
##########################################################
#                  Physical Environment                  #
##########################################################
*.physicalEnvironment.config = xmldoc("empty.xml")
*.radioMedium.backgroundNoise.power = -110dBm
*.radioMedium.mediumLimitCache.centerFrequency = 5.9 GHz

##########################################################
#              IEEE 802.11p NIC Configuration            #
##########################################################
*.node[*].wlan[0].opMode = "p"
*.node[*].wlan[0].radio.typename = "Ieee80211DimensionalRadio"
*.node[*].wlan[0].radio.bandName = "5.9 GHz"
*.node[*].wlan[0].radio.channelNumber = 3
*.node[*].wlan[0].radio.bandwidth = 10 MHz
*.node[*].wlan[0].radio.transmitter.power = 10mW

# Penempatan Posisi Fisik Antena pada Bodi Kendaraan
*.node[*].wlan[*].radio.antenna.mobility.typename = "AttachedMobility"
*.node[*].wlan[*].radio.antenna.mobility.mobilityModule = "^.^.^.^.mobility"
*.node[*].wlan[*].radio.antenna.mobility.offsetX = -2.5m
*.node[*].wlan[*].radio.antenna.mobility.offsetZ = 1.5m
```

### Parameter Kunci Antena & Lingkungan:
- **`backgroundNoise.power = -110dBm`**: Memodelkan desah termal lingkungan (*thermal noise floor*) pada temperatur ruang $290\text{ K}$ dengan bandwidth $10\text{ MHz}$.
- **`antenna.mobility.offsetZ = 1.5m`**: Antena ditempatkan pada ketinggian $1{,}5\text{ meter}$ di atas permukaan tanah (posisi realistis atap mobil sedan).
- **`antenna.mobility.offsetX = -2.5m`**: Posisi antena digeser ke arah tengah atap kendaraan sesuai dimensi kendaraan SUMO.

---

## 3. Penurunan Matematis Jangkauan Radio (Range Derivation)

Batas jangkauan komunikasi (*Communication Range*) antara pemancar ($Tx$) dan penerima ($Rx$) dihitung berdasarkan model redaman ruang bebas (*Friis Transmission Equation*).

### A. Persamaan Transmisi Friis

Daya terima ($P_{rx}$) pada jarak pemisah $d$ dinyatakan sebagai:

$$P_{rx} = P_{tx} \cdot G_{tx} \cdot G_{rx} \cdot \left(\frac{\lambda}{4\pi d}\right)^2$$

Dengan mengasumsikan antena isotropik tanpa penguatan terarah ($G_{tx} = 1, G_{rx} = 1$):

$$P_{rx} = P_{tx} \cdot \left(\frac{\lambda}{4\pi d}\right)^2$$

Di mana:
- $c = 299.792.458\text{ m/s} \approx 3 \times 10^8\text{ m/s}$ (kecepatan cahaya)
- $f = 5{,}9\text{ GHz} = 5{,}9 \times 10^9\text{ Hz}$
- Panjang gelombang DSRC $\lambda$:
  $$\lambda = \frac{c}{f} = \frac{3 \times 10^8\text{ m/s}}{5{,}9 \times 10^9\text{ Hz}} \approx 0{,}0508136\text{ meter} \approx 5{,}08\text{ cm}$$

---

### B. Menentukan Jarak Maksimum ($d_{max}$)

Penerima dapat mendekode sinyal jika daya terima tidak lebih kecil dari batas ambang sensitivitas modulasi radio ($P_{rx} \ge P_{rx\_min}$):

$$P_{rx\_min} = P_{tx} \cdot \left(\frac{\lambda}{4\pi d_{max}}\right)^2$$

Membagi kedua sisi dengan $P_{tx}$:

$$\frac{P_{rx\_min}}{P_{tx}} = \left(\frac{\lambda}{4\pi d_{max}}\right)^2$$

Mengambil akar kuadrat pada kedua sisi:

$$\sqrt{\frac{P_{rx\_min}}{P_{tx}}} = \frac{\lambda}{4\pi d_{max}}$$

Menyelesaikan untuk $d_{max}$:

$$\mathbf{d_{max} = \frac{\lambda}{4\pi} \cdot \sqrt{\frac{P_{tx}}{P_{rx\_min}}} = \frac{c}{4\pi f} \cdot \sqrt{\frac{P_{tx}}{P_{rx\_min}}}}$$

---

### C. Pembuktian Numerik dengan Parameter Simulasi

Dalam konfigurasi standar INET:
- Daya pancar kendaraan: $P_{tx} = 10\text{ mW} = 0{,}01\text{ Watt}$ ($+10\text{ dBm}$)
- Ambang sensitivitas: $P_{rx\_min} = -85\text{ dBm} = 10^{\frac{-85}{10}}\text{ mW} = 10^{-8{,}5}\text{ mW} \approx 3{,}16228 \times 10^{-12}\text{ Watt}$

Menghitung rasio daya:
$$\frac{P_{tx}}{P_{rx\_min}} = \frac{10^{-2}\text{ W}}{3{,}16228 \times 10^{-12}\text{ W}} \approx 3{,}16228 \times 10^9$$

$$\sqrt{\frac{P_{tx}}{P_{rx\_min}}} = \sqrt{3{,}16228 \times 10^9} \approx 56.234{,}13$$

Menghitung konstanta skala ruang bebas:
$$\frac{\lambda}{4\pi} = \frac{0{,}0508136}{4 \times 3{,}14159265} \approx 0{,}0040436\text{ meter}$$

Mengalikan keduanya:
$$d_{max} = 0{,}0040436 \times 56.234{,}13 \approx \mathbf{226{,}7\text{ meter}} \approx \mathbf{227\text{ meter}}$$

Maka pada daya pancar $10\text{ mW}$, jangkauan lingkaran fisik mobil adalah tepat **$\approx 227\text{ meter}$**.

---

## 4. Tabel Lookup Variasi Daya vs Radius Jangkauan

Berdasarkan formula di atas, berikut adalah tabel radius jangkauan efektif pada frekuensi $5{,}9\text{ GHz}$ dan sensitivitas $-85\text{ dBm}$:

| Daya Pemancar ($P_{tx}$) | Nilai dalam dBm | Radius Jangkauan Teoretis ($d_{max}$) | Rekomendasi Kasus Uji |
|:---:|:---:|:---:|---|
| **$2\text{ mW}$** | $+3\text{ dBm}$ | $\approx \mathbf{101\text{ meter}}$ | Kepadatan mobil sangat tinggi (mencegah tabrakan paket) |
| **$5\text{ mW}$** | $+7\text{ dBm}$ | $\approx \mathbf{160\text{ meter}}$ | Lingkungan urban gang sempit / perkantoran |
| **$10\text{ mW}$** *(Default)* | $+10\text{ dBm}$ | $\approx \mathbf{227\text{ meter}}$ | **Standar industri DSRC V2V pada jalan raya kota** |
| **$50\text{ mW}$** | $+17\text{ dBm}$ | $\approx \mathbf{508\text{ meter}}$ | Kendaraan prioritas (Ambulans, Pemadam Kebakaran) |
| **$100\text{ mW}$** *(RSU)* | $+20\text{ dBm}$ | $\approx \mathbf{718\text{ meter}}$ | **Infrastruktur persimpangan (Road-Side Unit gateway)** |

---

## 5. Mengapa Diperlukan Pengaturan `centerFrequency`?

Secara default, jika parameter tidak dideklarasikan, submodul `mediumLimitCache` pada INET Framework akan mengasumsikan frekuensi kerja pada frekuensi WiFi standar ($2{,}4\text{ GHz}$).
Pada $2{,}4\text{ GHz}$, panjang gelombangnya jauh lebih panjang ($\lambda \approx 12{,}5\text{ cm}$), sehingga rumus menghasilkan radius lingkaran palsu sebesar $\approx 560\text{ meter}$.

Oleh karena itu, baris berikut **wajib diaktifkan** di `omnetpp.ini`:
```ini
*.radioMedium.mediumLimitCache.centerFrequency = 5.9 GHz
```
Dengan parameter ini, INET menghitung redaman gelombang dan merender lingkaran visual jangkauan dengan akurasi fisik penuh sesuai karakteristik DSRC 5.9 GHz.
