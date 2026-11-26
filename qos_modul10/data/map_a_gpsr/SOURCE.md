# Sumber data — Map A + GPSR

Folder ini berisi salinan `.sca` dari hasil GPSR yang, setelah diaudit, terbukti
berjalan di **Map A**, bukan Map B. Nama file tetap `GPSR_*` karena itu nama
output asli dari workspace `vanet_gpsr`.

| Item | Nilai |
|---|---|
| Workspace asal | `vanet_gpsr/results/` |
| Launch config (runtime) | `maps.launchd.xml` (Map A) |
| Jumlah kendaraan | 20 |
| Seedset | 0 |
| Durasi simulasi | 40 s |
| File | `GPSR_V2V_Ping-#0.sca`, `GPSR_V2V_UDP-#0.sca` |
| Run ID | `GPSR_V2V_Ping-0-20261112-12:36:31-2556`, `GPSR_V2V_UDP-0-20261112-12:38:00-3298` |

## Bukti provenance

Di dalam `.sca`:

```text
par Scenario.manager launchConfig "<launch>...</launch> at .../vanet_gpsr/maps.launchd.xml:2"
```

Jumlah kendaraan hanya 20 (`Scenario.node[0]` … `Scenario.node[19]`), sedangkan
Map B memakai 80 kendaraan. Karena itu file ini **tidak boleh** dipakai sebagai
data Map B.

## Catatan Git

File `.sca` di folder ini diabaikan oleh Git (kebijakan `.gitignore` proyek).
Metadata, checksum, dan run ID dicatat di `../manifest.json`.

Untuk memulihkan salinan dari hasil asli:

```bash
cp -p vanet_gpsr/results/GPSR_V2V_Ping-#0.sca qos_modul10/data/map_a_gpsr/
cp -p vanet_gpsr/results/GPSR_V2V_UDP-#0.sca  qos_modul10/data/map_a_gpsr/
```

Checksum SHA-256:

```text
918d67b5cbc3ca8eedd1d30428bc78f48ef4a937fcc79f13bbf08a591475011c  GPSR_V2V_Ping-#0.sca
4b6e34be7be6e1dc1a28ec5e37bc1e5b76d7d18692358cc78ef96aebadec5eb5  GPSR_V2V_UDP-#0.sca
```
