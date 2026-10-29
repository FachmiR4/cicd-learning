# Tracker kompetensi dan bukti belajar

[README](../README.md) · [Roadmap](roadmap.md)

Gunakan dokumen ini sebagai catatan Anda. Isi status berdasarkan bukti, bukan keberadaan file atau lama belajar. Tanggal penyusunan: 29 Oktober 2026.

## Baseline yang diketahui

| Area | Informasi yang tersedia | Tindakan berikutnya |
|---|---|---|
| API lokal + smoke | Hasil berhasil pernah dibagikan | Ulangi jika lingkungan berubah |
| Git dan PR | Commit/push/PR/merge telah dilatih | Pertahankan review diff sebelum commit |
| Test | 17 metode ditemukan; hasil test awal dan CI pernah berhasil | Catat run aktual untuk commit berikutnya |
| Container CI | Build dan smoke berhasil pada screenshot run sebelumnya | Pertahankan keterlacakan commit |
| GHCR | File publish tersedia | Masukkan tautan run sukses dan digest asli |
| Staging/production | Belum ada bukti deployment tetap | Tentukan target dan kontrak deployment |
| Security/senior | Materi baru, bukan implementasi yang diverifikasi | Pilih satu lab setelah prasyarat terpenuhi |

## Checklist level

Checklist sengaja belum dicentang otomatis. Anda dapat mengisinya dengan bukti dari latihan yang telah selesai.

- [ ] Level 0: server, port, request, dan smoke dipahami; bukti: ...
- [ ] Level 1: Git/PR dan test negatif dapat diulang; bukti: ...
- [ ] Level 2: CI dan gate merge dapat dijelaskan; bukti: ...
- [ ] Level 3: commit→run→digest registry terlacak; bukti: ...
- [ ] Level 4: staging dan pemulihan terbukti; bukti: ...
- [ ] Level 5: trust boundary, gate security, dan IaC diuji; bukti: ...
- [ ] Level 6: insiden/data/platform memiliki bukti operasi; bukti: ...
- [ ] Level 7: ADR, review independen, dan mentoring dilakukan; bukti: ...

## Catatan satu sesi

```text
Tanggal:
Level dan topik:
Tujuan perilaku yang ingin dibuktikan:
Prasyarat yang telah diperiksa:
Lingkungan (lokal/runner/staging):
Perintah atau perubahan:
Prediksi hasil:
Hasil sebenarnya:
Kegagalan yang diamati:
Penyebab yang dibuktikan (pisahkan dari dugaan):
Perbaikan dan verifikasi:
Commit / PR / URL run / digest:
Keterbatasan pengujian:
Langkah berikutnya:
```

## Rencana empat sesi berikutnya

| Sesi | Tujuan | Bukti selesai |
|---|---|---|
| 1 | Verifikasi run publish GHCR | Status push/capture digest, commit, digest |
| 2 | Jelaskan perbedaan tag dan digest | Contoh dari artifact nyata dan sumber commit |
| 3 | Verifikasi pull image di runner | Image ditarik berdasarkan digest dan smoke berhasil |
| 4 | Rancang staging tanpa provisioning dahulu | Target, akses, config, storage, health, rollback dan kebutuhan biaya |

Jika publish gagal, alihkan sesi berikutnya ke diagnosis; jangan isi digest rekaan. Template [release-record.md](release-record.md) dan [incident-report.md](incident-report.md) dipakai untuk catatan rilis/insiden aktual. Jangan menaruh secret, token, data produksi, atau log sensitif di tracker.
