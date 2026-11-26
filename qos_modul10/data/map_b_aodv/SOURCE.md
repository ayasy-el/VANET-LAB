# Sumber data — Map B + AODV

Folder ini berisi hasil run **AODV di Map B** yang dijalankan ulang pada
2026-11-20. Sebelumnya kombinasi ini belum pernah menghasilkan file `.sca`.

| Item | Nilai |
|---|---|
| Workspace | `vanet_aodv` |
| Launch config | `map2.launchd.xml` (Map B) |
| Jumlah kendaraan | 80 |
| Seedset | 0 |
| Durasi simulasi | 40 s |
| File | `AODV_V2V_Ping-#0.sca`, `AODV_V2V_UDP-#0.sca` |
| Run ID Ping | `AODV_V2V_Ping-0-20261120-13:30:59-5942` |
| Run ID UDP | `AODV_V2V_UDP-0-20261120-13:31:18-5984` |

## Cara run

Output diarahkan ke folder terisolasi agar `vanet_aodv/results/` (hasil Map A)
tidak tertimpa:

```bash
cd vanet_aodv
mkdir -p ../qos_modul10/data/map_b_aodv/raw
./run_cmd.sh AODV_V2V_Ping 40s --map b --result-dir=../qos_modul10/data/map_b_aodv/raw
./run_cmd.sh AODV_V2V_UDP  40s --map b --result-dir=../qos_modul10/data/map_b_aodv/raw
```

Setelah run, seluruh hasil dipindahkan ke folder ini. File `.vec`/`.vci`
disimpan sebagai arsip; pipeline QoS hanya memakai `.sca`.

## Bukti provenance

```text
par Scenario.manager launchConfig "<launch>...</launch> at .../vanet_aodv/map2.launchd.xml:10"
```

Jumlah kendaraan 80 (`Scenario.node[0]` … `Scenario.node[79]`), seedset 0,
`sim-time-limit = 40s`.

Checksum SHA-256:

```text
24293f01afd98106d15632aae76399bdeabd8d8507196c3757392b8a5c5eda59  AODV_V2V_Ping-#0.sca
7e79502f74a1d427166f41f238742538a025ebe0ca07fc404a57437278400788  AODV_V2V_UDP-#0.sca
```
