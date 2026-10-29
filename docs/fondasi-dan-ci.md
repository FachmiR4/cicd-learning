# Fondasi aplikasi, Git, testing, dan CI

[Beranda](../README.md) · [Roadmap](roadmap.md) · [Referensi Git](git-reference.md) · [Lanjut: container dan CD](container-dan-cd.md)

Modul ini mencakup level 0–2 pada roadmap. Gunakan satu sesi untuk satu latihan; lanjutkan setelah bisa menjelaskan hasilnya. Perintah **lokal** ditujukan untuk **Git Bash di Windows**, sesuai terminal `MINGW64` yang digunakan dalam pembelajaran.

Proyek adalah Task API Python dengan database SQLite. Sumber yang diperiksa memuat 17 test. Aplikasi menggunakan pustaka standar Python; latihan ini tidak membutuhkan instalasi `pytest`. Angka test akan bertambah ketika Anda menambah kasus baru. Dokumen ini menjelaskan langkah dan hasil yang diharapkan, bukan laporan bahwa semua latihan lanjutan sudah dijalankan.

## 1. Gambaran kerja yang akan dibangun

```text
Kebutuhan → perubahan kode → test lokal → commit → pull request
          → CI otomatis → review → merge → artifact → deployment
```

**CI (Continuous Integration)** memeriksa perubahan secara otomatis agar masalah ditemukan lebih cepat. **Continuous Delivery** menyiapkan perubahan yang layak dirilis, dengan keputusan rilis yang dapat dilakukan manusia. **Continuous Deployment** mengotomatiskan rilis setelah seluruh persyaratan terpenuhi. Ketiganya membutuhkan test yang bermakna dan mekanisme pemulihan.

Sasaran awal bukan menghafal seluruh tool. Anda harus mampu menjawab: kode apa yang berubah, test apa yang membuktikan perilakunya, proses mana yang gagal, dan apakah versi yang diuji sama dengan versi yang akan dirilis.

| Tempat kerja | Pekerjaan |
|---|---|
| Komputer Anda | Menulis kode, menjalankan Python, test, Git |
| GitHub Actions | Test lintas versi Python, build dan menjalankan container |
| Registry | Menyimpan image hasil build |
| Target deployment | Menjalankan aplikasi setelah pipeline selesai; belum dipilih |

## 2. Lab 0 — mengenali terminal dan folder

**Jalankan lokal di Git Bash:**

```bash
cd ~/Videos/cicd/cicd-practice
pwd
ls
py --version
git --version
git status
```

`pwd` menjawab “saya sedang berada di mana?”, sedangkan `ls` menampilkan isi folder. Pastikan `app.py`, `tests`, dan `scripts` terlihat. `git status` memeriksa perubahan dan branch aktif. Jangan mengetik teks prompt seperti `$`, nama komputer, atau `(main)`.

| Kebutuhan | Git Bash yang dipakai di sini | CMD lama |
|---|---|---|
| Path folder test | `./tests` | `.\tests` |
| Membuang stdout | `1>/dev/null` | `1>NUL` |
| Variabel untuk satu perintah | `PORT=8081 py app.py` | `set PORT=8081`, lalu perintah berikutnya |

Jika perintah CMD `1>NUL` pernah dijalankan di Git Bash dan `git status` menampilkan file `NUL`, periksa file tersebut sebelum menghapusnya. Jangan memasukkannya ke commit. Jika `py` bekerja tetapi `python` tidak, gunakan `py` pada Windows; runner Linux memakai `python` setelah langkah setup.

**Bukti selesai:** catat lokasi folder, versi Python lokal, versi Git, dan branch. Python lokal Anda dapat berbeda dari matrix CI; perbedaan ini justru alasan untuk memiliki pemeriksaan lintas versi.

## 3. Lab 1 — aplikasi, port, dan request

**Git Bash pertama, lokal:**

```bash
HOST=127.0.0.1 PORT=8081 APP_VERSION=dev FAIL_READY=0 py app.py
```

Biarkan terminal ini aktif. Aplikasi mendengarkan port 8081; gunakan **Ctrl+C** untuk menghentikannya. Port 8080 pernah berbenturan dengan layanan lain, sehingga latihan lokal memakai 8081.

**Git Bash kedua, lokal:**

```bash
cd ~/Videos/cicd/cicd-practice
curl -i http://127.0.0.1:8081/health
curl -i http://127.0.0.1:8081/ready
curl -i http://127.0.0.1:8081/version
py scripts/smoke.py http://127.0.0.1:8081 --expect-version dev
```

`curl -i` memperlihatkan status HTTP dan body. `/health` memeriksa apakah proses dapat merespons. `/ready` juga memeriksa akses ke tabel database. `/version` mengembalikan identitas versi. Smoke test membuat data sintetis, membaca, lalu menghapusnya. Gunakan pada lingkungan latihan yang Anda miliki.

**Hasil yang diharapkan:** health dan readiness menghasilkan 200; smoke test menampilkan `SMOKE OK {'version': 'dev'}`. Angka 200 sendiri belum membuktikan versi benar, sehingga versi diperiksa terpisah.

**Eksperimen gagal lalu pulih:** hentikan server, lalu jalankan smoke test. Ia harus gagal setelah percobaan terbatas. Nyalakan server kembali dan ulangi. Catat perbedaan “proses tidak berjalan” dengan “proses berjalan tetapi belum ready”. Jangan langsung mengganti port tanpa memeriksa alamat yang benar.

## 4. Lab 2 — membaca 17 test yang tersedia

**Lokal:**

```bash
py -m unittest discover -s ./tests -p test_api.py -v 1>/dev/null
```

`discover` mencari test, `-s` menentukan folder awal, `-p` membatasi nama file, dan `-v` menampilkan setiap kasus. Pengalihan stdout menyembunyikan log JSON aplikasi; laporan `unittest` masih muncul melalui stderr. Saat mencari masalah log aplikasi, jalankan kembali tanpa `1>/dev/null`.

`unittest` menyediakan assertion dan fixture untuk menyiapkan serta membersihkan kondisi test. Dalam proyek ini, `setUp` membuat database sementara dan server dengan port bebas, lalu `tearDown` membersihkannya. Karena itu, test tidak memerlukan aplikasi manual pada 8081. [Dokumentasi unittest](https://docs.python.org/3/library/unittest.html)

| Kelompok | Contoh | Hal yang dibuktikan |
|---|---|---|
| Unit | `test_strip_spaces` | Spasi tepi dibuang |
| Unit | `test_boundary` | Judul tepat 120 karakter diterima |
| Unit | `test_unicode_title` | Teks Unicode diterima utuh |
| Integrasi | `test_create_list_delete` | HTTP dan SQLite bekerja bersama |
| Integrasi | `test_unicode_title_round_trip` | Unicode bertahan setelah disimpan dan dibaca |
| Penolakan | `test_long_title_rejected_without_saving` | 121 karakter ditolak tanpa mengubah data |
| Ketahanan | `test_readiness_detects_broken_schema` | Kerusakan skema terdeteksi melalui readiness |

**Hasil yang diharapkan pada baseline:** `Ran 17 tests` dan `OK`. Kode HTTP 400, 404, 413, atau 503 pada log dapat menjadi perilaku yang sengaja diuji. Assertion dan ringkasan test menentukan keberhasilan, bukan apakah setiap request menghasilkan 200.

Bedakan `FAIL` (assertion tidak sesuai), `ERROR` (exception tidak tertangani dalam test), dan `OK` (seluruh test berhasil). Ketiganya memberi petunjuk berbeda saat troubleshooting.

## 5. Lab 3 — membuat test gagal dengan sengaja

Lakukan pada branch latihan dan mulai dari working tree bersih:

```bash
git status
git switch -c latihan/batas-validasi-ulang
notepad app.py
```

Pada `validate_title`, ubah hanya batas kondisi `> 120` menjadi `> 119`, simpan, lalu jalankan test. Judul tepat 120 karakter sekarang ditolak. `test_boundary` harus gagal, biasanya sebagai `ERROR` karena `ValueError` tidak diharapkan.

Kembalikan angka menjadi 120 dan jalankan ulang. Targetnya kembali `OK`. Tidak perlu me-restart server manual karena setiap proses test mengimpor ulang kode yang tersimpan.

**Catat bukti:** aturan bisnis, perubahan satu baris, nama test yang mendeteksi, dan hasil setelah pemulihan. Jangan melemahkan test agar perubahan yang salah terlihat hijau. Untuk latihan CI merah–hijau, lakukan commit perubahan salah pada branch khusus, buka PR, amati CI, kemudian commit perbaikannya pada branch yang sama. Jangan merge kondisi yang masih gagal.

## 6. Lab 4 — menambah test yang berguna

Tiga tambahan Unicode dan judul panjang sudah ada pada sumber yang diperiksa; jangan menyalin fungsi tersebut dua kali. Nama fungsi test yang sama dalam satu class dapat menimpa definisi sebelumnya.

Mulai dengan working tree bersih dan branch baru. Pilih nama lain jika branch contoh sudah ada:

```bash
git status
git switch main
git pull --ff-only origin main
git switch -c latihan/test-batas-dengan-spasi
notepad tests/test_api.py
```

Latihan baru: apakah judul berisi 120 karakter dengan spasi di tepi tetap diterima setelah spasinya dibuang? Tambahkan metode ini **di dalam `ValidationTests`**, sejajar dengan metode lain:

```python
    def test_max_title_with_surrounding_spaces(self):
        title = "x" * 120
        self.assertEqual(validate_title("  " + title + "  "), title)
```

Strukturnya mengikuti **Arrange–Act–Assert**: siapkan input, panggil fungsi, periksa hasil. Bila belum ada test setara, jumlah yang diharapkan menjadi 18. Test dapat langsung hijau karena perilakunya sudah didukung; nilainya adalah menjaga perilaku tersebut dari regresi.

Lalu rancang sendiri integration test untuk judul 120 karakter melalui POST dan GET. Sebelum menulisnya, tulis tiga assertion: status 201, judul hasil POST sama, dan task ditemukan setelah GET. Bandingkan dengan test 121 karakter: batas diterima dan batas ditolak perlu diperiksa terpisah.

**Bukti selesai:** diff hanya perubahan test yang dimaksud, test baru benar-benar terdaftar, dan seluruh suite berhasil. Jika terjadi `IndentationError`, jalankan `py -m py_compile tests/test_api.py`, lalu sejajarkan metode dengan empat spasi dan isinya dengan delapan spasi.

## 7. Lab 5 — mengirim perubahan melalui PR

Lanjutkan pada branch dari Lab 4. Jangan berpindah branch ketika test baru belum disimpan dalam commit. Periksa bahwa branch dan perubahan sesuai tujuan:

```bash
git status
git branch --show-current
```

Setelah mengedit dan menguji:

```bash
git diff -- tests/test_api.py
git add tests/test_api.py
git diff --cached
git commit -m "Uji judul batas maksimum dengan spasi tepi"
git push -u origin latihan/test-batas-dengan-spasi
```

`diff` memeriksa perubahan; `add` memilih isi commit; `commit` menyimpan versi lokal; `push` mengirim commit. `Everything up-to-date` hanya berarti tidak ada commit tambahan untuk dikirim, bukan berarti PR sudah di-merge.

Buat PR menuju `main`. Jelaskan masalah atau perilaku, perubahan, dan hasil pengujian yang benar-benar diperoleh. Periksa Files changed, tunggu CI terbaru, lalu review sebelum merge. Setelah merge, `git switch main` dan `git pull --ff-only origin main` menyamakan lokal dengan remote. Detail perintah dan pemulihan tersedia di [referensi Git](git-reference.md).

## 8. Lab 6 — memahami workflow CI

**Baca lokal; tidak menjalankan Docker:**

```bash
cat .github/workflows/ci.yml
```

Workflow saat ini dipicu PR menuju `main` dan push ke `main`. Job `test` berjalan pada Python 3.12 dan 3.13. Job `container` memakai `needs: test`, sehingga berjalan setelah test berhasil. `runs-on` memilih runner; `steps` berisi pekerjaan; `if: always()` memungkinkan pengambilan log dan cleanup walau langkah sebelumnya gagal. Ini adalah bagian dari sintaks workflow GitHub Actions. [Referensi workflow](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)

```text
PR → test Python 3.12 ─┐
                      ├→ build image → start container → smoke → cleanup
     test Python 3.13 ─┘
```

Perintah `compileall` pada workflow memeriksa sintaks; ia bukan pemeriksaan gaya kode lengkap. Test yang hijau membuktikan kasus yang diuji, tidak menjamin bebas semua bug. Matrix membantu mendeteksi perbedaan versi Python, tetapi tidak otomatis menguji seluruh kombinasi sistem operasi.

**Latihan membaca log:** buka Actions → run terbaru → job yang gagal → langkah pertama yang gagal. Catat commit, nama job, perintah, pesan error pertama yang relevan, serta exit code. Bandingkan dengan run terakhir yang berhasil. Pada PR, konteks commit workflow dapat berupa commit gabungan sementara; jangan selalu menyamakannya dengan SHA commit terakhir branch.

## 9. Troubleshooting yang sudah ditemui

| Gejala | Periksa dan pulihkan |
|---|---|
| `Empty module name` | Gunakan `./tests` di Git Bash; cek folder kerja |
| File `NUL` muncul | Gunakan `/dev/null`; periksa lalu hapus file tak sengaja itu |
| Smoke readiness gagal | Cek proses, port, `/ready`, dan log; health saja tidak cukup |
| `Connection reset by peer` saat startup | Retry readiness terbatas menangani `ConnectionError`; cek log jika berulang |
| `IndentationError` | Spasi `try` dan `except` harus sejajar; jangan campur tab |
| CI tidak berjalan setelah push branch | Workflow ini menunggu PR ke `main`; periksa trigger |
| Docker lokal tidak terhubung | Lanjutkan dengan runner GitHub; Docker lokal bukan prasyarat jalur ini |

## 10. Checkpoint sebelum level container

- [ ] Bisa menjalankan API lokal dan menjelaskan health, readiness, serta version.
- [ ] Bisa menjalankan suite test dan membedakan kegagalan test dari log HTTP yang diharapkan.
- [ ] Pernah membuktikan perubahan salah terdeteksi lalu memperbaikinya.
- [ ] Menambah satu kasus perilaku tanpa menduplikasi test yang sudah ada.
- [ ] Memiliki PR, diff, hasil test lokal, dan run CI sebagai bukti.
- [ ] Bisa menjelaskan alasan job container bergantung pada job test.

Simpan jurnal singkat: tujuan, dugaan hasil, hasil sebenarnya, penyebab kegagalan, perbaikan, serta tautan PR/run. Lanjutkan ke [container, registry, dan CD](container-dan-cd.md) setelah bisa mengulang alur tersebut tanpa menyalin seluruh instruksi.
