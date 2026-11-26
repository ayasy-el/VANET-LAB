# Sumber data — Map B + GPSR

Folder ini berisi hasil run **GPSR di Map B** yang dijalankan ulang pada
2026-11-20. File Map B yang lama sudah tertimpa oleh run Map A, sehingga data
ini adalah **run baru**, bukan salinan file lama.

Nilai run baru ini mereproduksi angka yang tercatat di
`docs/PRAKTIKUM8_GPSR_MAP_B.md` §5: 27/38 ping diterima (loss 28,95 %), 26/38
paket UDP (PDR 68,42 %), dan throughput 2,88 kbit/s. Ini menunjukkan skenario
Map B deterministik dengan seedset 0.

| Item | Nilai |
|---|---|
| Workspace | `vanet_gpsr` |
| Launch config | `map2.launchd.xml` (Map B) |
| Jumlah kendaraan | 80 |
| Seedset | 0 |
| Durasi simulasi | 40 s |
| File | `GPSR_V2V_Ping-#0.sca`, `GPSR_V2V_UDP-#0.sca` |
| Run ID Ping | `GPSR_V2V_Ping-0-20261120-13:31:28-6009` |
| Run ID UDP | `GPSR_V2V_UDP-0-20261120-13:31:57-6043` |

## Cara run

Output diarahkan ke folder terisolasi agar `vanet_gpsr/results/` (hasil Map A)
tidak tertimpa:

```bash
cd vanet_gpsr
mkdir -p ../qos_modul10/data/map_b_gpsr/raw
./run_cmd.sh GPSR_V2V_Ping 40s --map b --result-dir=../qos_modul10/data/map_b_gpsr/raw
./run_cmd.sh GPSR_V2V_UDP  40s --map b --result-dir=../qos_modul10/data/map_b_gpsr/raw
```

Setelah run, seluruh hasil dipindahkan ke folder ini. File `.vec`/`.vci`
disimpan sebagai arsip; pipeline QoS hanya memakai `.sca`.

## Bukti provenance

```text
par Scenario.manager launchConfig "<launch>...</launch> at .../vanet_gpsr/map2.launchd.xml:10"
```

Jumlah kendaraan 80 (`Scenario.node[0]` … `Scenario.node[79]`), seedset 0,
`sim-time-limit = 40s`.

Checksum SHA-256:

```text
dc9a4c89bd678fec92f041390a186182a975c9c5017dbb37783253f806f1c4f1  GPSR_V2V_Ping-#0.sca
705ba50d5c7983a1e78ccd9a14fd3f6a76ca529bc5360fbd8d7a9802f2f6d1a3  GPSR_V2V_UDP-#0.sca
```
