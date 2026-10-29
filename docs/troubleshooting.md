# Kendala yang pernah ditemukan

[README](../README.md) · [Roadmap](roadmap.md)

| Gejala | Penyebab / pelajaran | Penanganan |
|---|---|---|
| `python is not recognized` | Alias/PATH `python` tidak tersedia | Gunakan launcher `py` yang sudah berfungsi |
| `Python 3.12 not found` | Versi itu belum terpasang lokal | Gunakan runtime lokal yang tersedia dan uji kompatibilitas; CI tetap memakai runtime yang dikonfigurasi |
| Test mengambil `site-packages/tests`, meminta pytest | Command dijalankan dari folder induk | Masuk ke `cicd-practice` dan pilih `./tests` |
| Smoke 8080 gagal, endpoint 404 | Pada saat diagnosis port 8080 dipakai proses `httpd` | API lokal dipindahkan ke 8081 |
| `Connection reset by peer` pada CI | Koneksi terputus; script belum menangani kategori error tersebut ketika menunggu readiness | Tambahkan retry untuk `ConnectionError`, lalu cek log bila tetap gagal |
| `IndentationError` | Spasi tidak konsisten; pernah ada 5 spasi sebelum `for` yang seharusnya 4 | Sejajarkan blok dan periksa sintaks |
| `ValueError: Empty module name` di Git Bash | Path CMD `.\tests` dibaca keliru oleh Bash | Gunakan `./tests` |
| File untracked bernama `NUL` | `1>NUL` adalah sintaks CMD yang menghasilkan file di Git Bash | Gunakan `1>/dev/null`; hapus hanya file `NUL` yang tidak sengaja dibuat |
| `docker: command not found` | Docker CLI belum ditemukan | Docker lokal tidak diperlukan dalam jalur belajar yang dipilih |
| Docker pipe error / engine 500 | CLI tersedia tetapi engine lokal tidak merespons | Gunakan runner GitHub untuk latihan container |
| `wsl --version` hanya menampilkan bantuan | Mengarah pada WSL lama atau setup belum lengkap; bukan bukti tunggal keterbatasan hardware | Setup lokal ditunda; lanjutkan Python lokal + runner remote |

## Retry readiness yang sudah diperbaiki

Blok di dalam fungsi `smoke` menggunakan empat spasi pada tingkat `for`, delapan pada `try`/`except`:

```python
    for attempt in range(20):
        try:
            request("/ready")
            break
        except (URLError, TimeoutError, ConnectionError):
            if attempt == 19:
                raise RuntimeError("Layanan belum ready; periksa log dan konfigurasi")
            time.sleep(0.5)
```

Retry ini terbatas pada pemeriksaan readiness. Ia tidak membuat semua kegagalan boleh diabaikan. Jika terus gagal, baca log container dan penyebab aplikasi berhenti/tidak siap.

Periksa sintaks setelah edit:

```bash
py -m py_compile scripts/smoke.py
```

## Git Bash versus CMD

| Kebutuhan | Git Bash — digunakan sekarang | CMD — latihan sebelumnya |
|---|---|---|
| Folder test | `./tests` | `.\tests` |
| Sembunyikan stdout | `1>/dev/null` | `1>NUL` |
| Set variable | `export PORT=8081` | `set PORT=8081` |
| Baca file | `cat README.md` | `type README.md` |

Jangan mengetik simbol prompt `$` atau potongan `C:\...>` sebagai bagian command. Jika file `NUL` muncul kembali, periksa folder dengan `pwd`/`git status` sebelum menjalankan `rm -- NUL` pada file tersebut.


## Urutan diagnosis yang digunakan

1. Pastikan lokasi terminal dan branch: `pwd`, `git status`.
2. Cocokkan sintaks dengan shell: panduan aktif memakai Git Bash.
3. Periksa proses/lokasi yang diuji: API lokal 8081, container di runner 8080.
4. Temukan step gagal pertama dan baca error, bukan hanya warna workflow.
5. Ubah satu penyebab yang sudah dibuktikan, lalu jalankan ulang pemeriksaan terkait.
6. Jika error belum diketahui, simpan pesan lengkap tanpa secret dan tulis hipotesis sebagai dugaan.

## Kesalahan memahami status

- `Everything up-to-date` berarti ref yang didorong tidak memerlukan pembaruan saat push; bukan bukti PR sudah merged.
- `working tree clean` berarti tidak ada perubahan yang dilaporkan Git, bukan bukti aplikasi bebas bug.
- CI berhasil berarti check yang dijalankan lulus; runtime target lain tetap perlu verifikasi.
- Package atau YAML tersedia belum membuktikan deployment berjalan.
- Digest perlu dicatat dari hasil nyata; jangan mengganti placeholder dengan hash yang ditebak.

Untuk recovery Git, baca [referensi Git](git-reference.md). Untuk pola retry, readiness, dan batas pemulihan data, baca [container dan CD](container-dan-cd.md).
