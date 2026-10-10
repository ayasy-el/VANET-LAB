# 🏗️ Arsitektur & Desain Sistem

Dokumen ini menjelaskan rancangan arsitektur perangkat lunak, integrasi antar-simulator, dan struktur modul NED (*Network Description*) yang menyusun sistem simulasi VANET-AODV.

---

## 1. Integrasi Multi-Simulator (Bi-directional Coupling)

Simulasi jaringan kendaraan membutuhkan dua domain yang berbeda secara fundamental:
1. **Mobilitas Fisik Kendaraan**: Akselerasi, pengereman, perubahan lajur, kepatuhan lampu lalu lintas, dan interaksi jarak aman antar mobil. Ini ditangani oleh **Eclipse SUMO**.
2. **Komunikasi Nirkabel Jaringan**: Propagasi gelombang radio, interferensi sinyal, paket antrean MAC, protokol routing multi-hop, dan aplikasi jaringan. Ini ditangani oleh **OMNeT++** bersama **INET Framework**.

Jembatan sinkronisasi antara kedua simulator ini dihubungkan secara *real-time* oleh **Veins** (*Vehicular Network Open, Integrated with OMNeT++*) melalui protokol TCP bernama **TraCI (Traffic Control Interface)**.

```
       OMNeT++ (Client)                             SUMO (Server)
    ┌──────────────────────┐                     ┌─────────────────┐
    │ VeinsInetManager     │─── TraCI Connect ──►│ Port 9999       │
    │                      │◄── Handshake OK ────│ (sumo / -gui)   │
    │                      │                     │                 │
    │ Loop Waktu (dt=0.1s):│                     │                 │
    │                      │─── Timestep (t) ───►│ Simulasi Fisik  │
    │                      │◄── Data Kendaraan ──│ Posisi, Speed   │
    │                      │    (X, Y, Heading)  │ Lajur, Status   │
    │ Update Node INET     │                     │                 │
    │ (VeinsInetMobility)  │                     │                 │
    └──────────────────────┘                     └─────────────────┘
```

### Siklus Waktu Per-Langkah (Timestep Loop):
1. OMNeT++ mengirimkan perintah `timestep` ke daemon SUMO melalui soket TCP port 9999.
2. SUMO memajukan simulasi fisik kendaraan sebesar interval yang dikonfigurasi (`*.manager.updateInterval = 0.1s`).
3. SUMO merespons dengan daftar mobil aktif beserta posisi koordinat kartesius $(x, y, z)$, kecepatan, dan arah hadap (*heading*).
4. `VeinsInetManager` di sisi OMNeT++ secara dinamis:
   - Membuat instance modul `node[i]` baru jika ada mobil yang baru muncul.
   - Memperbarui koordinat fisik pada submodul `mobility` (`VeinsInetMobility`).
   - Menghapus modul `node[i]` jika mobil telah menyelesaikan rutenya dan keluar dari peta SUMO.

---

## 2. Struktur Modul Jaringan (NED Hierarchy)

Topologi simulasi didefinisikan secara deklaratif dalam bahasa NED (*Network Description*).

### A. Topologi Utama: `Scenario.ned`

```ned
package vanet_aodv;

import inet.physicallayer.wireless.ieee80211.packetlevel.Ieee80211DimensionalRadioMedium;
import org.car2x.veins.subprojects.veins_inet.VeinsInetManager;
import inet.visualizer.common.IntegratedVisualizer;
import inet.environment.common.PhysicalEnvironment;
import org.car2x.veins.visualizer.roads.RoadsCanvasVisualizer;

network Scenario
{
    parameters:
        int numRsu = default(0);
        @display("bgb=2500,2000");
    submodules:
        radioMedium: Ieee80211DimensionalRadioMedium {
            @display("p=150,100");
        }
        manager: VeinsInetManager {
            @display("p=150,200");
        }
        visualizer: IntegratedVisualizer {
            @display("p=150,300");
        }
        physicalEnvironment: PhysicalEnvironment {
            @display("p=150,400");
        }
        roadsCanvasVisualizer: RoadsCanvasVisualizer {
            @display("p=150,500");
        }
        rsu[numRsu]: VeinsAodvRSU {
            @display("p=1025,870");
        }
        node[0]: VeinsAodvCar;
}
```

#### Komponen Kunci `Scenario.ned`:
- **`radioMedium` (`Ieee80211DimensionalRadioMedium`)**: Submodul ruang perambatan gelombang radio nirkabel. Menghitung daya sinyal terima, pelemahan ruang bebas (*path loss*), derau lingkungan, dan tabrakan paket (*collision*).
- **`manager` (`VeinsInetManager`)**: Manajer TraCI yang terhubung ke daemon SUMO. Bertanggung jawab atas siklus hidup (*lifecycle*) mobil `node[*]`.
- **`roadsCanvasVisualizer` (`RoadsCanvasVisualizer`)**: Menggambar garis bentuk jalan raya dari `maps.net.xml` ke kanvas GUI OMNeT++.
- **`visualizer` (`IntegratedVisualizer`)**: Engine visualisasi grafis untuk merender jangkauan radio, koneksi data-link MAC, dan rute multi-hop AODV.
- **`rsu[numRsu]` (`VeinsAodvRSU`)**: Node infrastruktur statis (opsional, aktif jika `numRsu > 0`).
- **`node[0]` (`VeinsAodvCar`)**: Placeholder node dinamis. Di waktu *runtime*, `manager` akan mengekspansi array ini menjadi `node[0]`, `node[1]`, ..., `node[N-1]` sesuai jumlah mobil di SUMO.

---

### B. Modul Kendaraan: `VeinsAodvCar.ned`

```ned
package vanet_aodv;

import inet.node.aodv.AodvRouter;

module VeinsAodvCar extends AodvRouter
{
    parameters:
        @display("i=veins/node/car;is=vs");
}
```

`VeinsAodvCar` mewarisi (*extends*) modul **`AodvRouter`** dari INET Framework. Hal ini memberikan kapabilitas penuh sebuah node IP bergerak:
- **Stack Aplikasi (`app[*]`)**: Mendukung pengujian ICMP `PingApp`, `UdpBasicApp`, maupun `UdpSink`.
- **Protokol Routing (`aodv`)**: Engine AODV RFC 3561 dengan tabel routing dan buffer paket.
- **Lapisan Jaringan (`ipv4`)**: IP routing, fragmentasi, dan `GlobalArp`.
- **Antarmuka Nirkabel (`wlan[*]`)**: NIC IEEE 802.11p yang terintegrasi dengan radio dimensional.
- **Submodul Mobilitas (`mobility`)**: Diarahkan ke tipe `VeinsInetMobility` untuk menerima koordinat dinamis dari SUMO.

---

### C. Modul Road-Side Unit: `VeinsAodvRSU.ned`

```ned
package vanet_aodv;

import inet.node.aodv.AodvRouter;

module VeinsAodvRSU extends AodvRouter
{
    parameters:
        @display("i=device/antennatower;is=m");
}
```

Sama halnya dengan kendaraan, RSU merupakan varian dari `AodvRouter`. Perbedaannya terletak pada konfigurasinya di `omnetpp.ini`:
- Menggunakan `StationaryMobility` dengan posisi koordinat tetap $(X=1025\text{m}, Y=870\text{m}, Z=5\text{m})$.
- Memiliki daya transmisi lebih besar ($100\text{ mW}$) untuk menyediakan jangkauan cakupan area persimpangan yang luas.

---

## 3. Skema Pengalamatan Jaringan (IPv4 & ARP)

Pengalamatan IP pada topologi nirkabel dinamis dikonfigurasi secara otomatis menggunakan **`HostAutoConfigurator`**:

```ini
*.node[*].ipv4.configurator.typename = "HostAutoConfigurator"
*.node[*].ipv4.configurator.interfaces = "wlan0"
*.node[*].ipv4.configurator.addressBase = "10.0.0.0"
*.node[*].ipv4.configurator.netmask = "255.0.0.0"
*.node[*].ipv4.configurator.mcastGroups = "224.0.0.1"
*.node[*].ipv4.arp.typename = "GlobalArp"
```

- **Blok Subnet**: Seluruh node mobil dan RSU berada dalam satu subnet privat kelas A (`10.0.0.0/8`).
  - Mobil 0: `10.0.0.1`
  - Mobil 1: `10.0.0.2`
  - Mobil $k$: `10.0.0.(k+1)`
  - RSU 0: `10.0.0.X`
- **Global ARP**: Menggunakan `GlobalArp` untuk menyederhanakan resolusi MAC-ke-IP tanpa perlu membanjiri spektrum frekuensi dengan broadcast ARP berkala. Hal ini menjaga kanal nirkabel tetap murni untuk evaluasi protokol routing AODV dan trafik data aplikasi.
