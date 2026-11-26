# Sumber data — Map A + AODV

Folder ini berisi salinan `.sca` dari hasil Praktikum 8/9 yang sudah diverifikasi
berasal dari **Map A**.

| Item | Nilai |
|---|---|
| Workspace asal | `vanet_aodv/results/` |
| Launch config | `maps.launchd.xml` (Map A) |
| Jumlah kendaraan | 20 |
| Seedset | 0 |
| Durasi simulasi | 40 s |
| File | `AODV_V2V_Ping-#0.sca`, `AODV_V2V_UDP-#0.sca` |
| Run ID | `AODV_V2V_Ping-0-20261106-13:30:29-2652`, `AODV_V2V_UDP-0-20261106-13:33:25-3022` |

File `.sca` di folder ini **diabaikan oleh Git** karena `.gitignore` proyek
mengabaikan seluruh hasil simulasi. Salinan tetap disimpan lokal agar pipeline
dapat dijalankan ulang. Metadata, checksum, dan run ID dicatat di
`../manifest.json`.

Untuk memulihkan salinan dari hasil asli:

```bash
cp -p vanet_aodv/results/AODV_V2V_Ping-#0.sca qos_modul10/data/map_a_aodv/
cp -p vanet_aodv/results/AODV_V2V_UDP-#0.sca  qos_modul10/data/map_a_aodv/
```

Checksum SHA-256:

```text
169dd2bf2cc5f61bd42158994eec5002b0779e5bcce258c5432745e280e8090c  AODV_V2V_Ping-#0.sca
0f80d27326e3de553c722ed67f04a2cff420cdb09dc6a9f3fdb523761e45e39b  AODV_V2V_UDP-#0.sca
```
