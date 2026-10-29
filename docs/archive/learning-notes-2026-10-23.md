> Arsip materi sebelum restrukturisasi 29 Oktober 2026. Gunakan [README aktif](../../README.md) dan [roadmap](../roadmap.md) untuk urutan belajar terbaru. Isi catatan lama dipertahankan; tautan file disesuaikan dengan lokasi arsip.

# Belajar CI/CD — Task API

Panduan belajar dan catatan praktik Fachmi, dari menjalankan aplikasi lokal sampai merancang proses rilis. Diperbarui: **23 Oktober 2026**.

Repository: [FachmiR4/cicd-practice](https://github.com/FachmiR4/cicd-practice) · [Hasil GitHub Actions](https://github.com/FachmiR4/cicd-practice/actions)

Proyek ini menggunakan Python dan SQLite untuk API pencatat tugas. Fokus pembelajaran adalah testing, Git, GitHub Actions, image container, registry, dan deployment yang dapat diverifikasi.

**Jalur yang dipakai: Python lokal + Docker di GitHub Actions.** Komputer lokal tidak perlu menjalankan Docker Desktop, WSL, atau Kubernetes untuk menyelesaikan tahapan awal sampai publikasi image.

## Daftar isi

1. [Status pembelajaran](#status-pembelajaran)
2. [Konsep dasar](#konsep-dasar)
3. [Persiapan dan menjalankan aplikasi](#persiapan-dan-menjalankan-aplikasi)
4. [Testing dan membaca hasilnya](#testing-dan-membaca-hasilnya)
5. [Git, branch, dan pull request](#git-branch-dan-pull-request)
6. [CI dengan GitHub Actions](#ci-dengan-github-actions)
7. [Docker melalui runner GitHub](#docker-melalui-runner-github)
8. [Publikasi image ke GHCR](#publikasi-image-ke-ghcr)
9. [Kendala yang pernah ditemukan](#kendala-yang-pernah-ditemukan)
10. [Roadmap awal sampai akhir](#roadmap-awal-sampai-akhir)
11. [Cara belajar dan bukti kelulusan](#cara-belajar-dan-bukti-kelulusan)
12. [Struktur proyek dan referensi](#struktur-proyek-dan-referensi)
13. [Referensi perintah Git](#referensi-perintah-git-dari-dasar-sampai-lanjutan)

## Status pembelajaran

Status berikut membedakan bukti praktik yang telah dibagikan, file yang tersedia, dan target berikutnya. Keberadaan file workflow tidak membuktikan bahwa seluruh run-nya berhasil.

| Materi | Status / bukti |
|---|---|
| Menjalankan API lokal pada port 8081 | Berhasil; smoke test menghasilkan `SMOKE OK` |
| Unit dan integration test awal | 14 test awal pernah dijalankan dan lulus |
| Menyimpan perubahan menggunakan Git | Commit, branch, push, PR, dan merge telah dipraktikkan |
| CI otomatis pada GitHub | Run berhasil telah ditunjukkan melalui log/screenshot |
| Eksperimen batas judul 120 menjadi 119 | Dibahas dan dilanjutkan dengan perbaikan pada PR |
| Memperbaiki retry dan indentasi smoke test | Diperbaiki; smoke lokal kembali berhasil |
| Test tambahan Unicode dan judul terlalu panjang | Tiga test tambahan ada dalam file; total saat README diperbarui: 17 test |
| Build image dan smoke container di GitHub | Log berhasil telah ditunjukkan |
| Publikasi image ke GHCR | Workflow `publish.yml` sudah tersedia; digest/run sukses belum dikonfirmasi dalam catatan ini |
| Deployment staging/production | Materi lanjutan; belum dinyatakan selesai |
| Rollback, keamanan lanjutan, monitoring, GitOps | Roadmap lanjutan |

**Langkah terdekat:** verifikasi workflow `Publish verified image`, simpan digest, lalu pelajari staging. Jangan melompat ke Kubernetes sebelum memahami artifact, konfigurasi, dan pemulihan rilis.

## Konsep dasar

| Istilah | Penjelasan |
|---|---|
| CI — Continuous Integration | Mengintegrasikan perubahan kecil secara rutin dan memeriksanya otomatis |
| Continuous Delivery | Menyiapkan perubahan yang lolos pemeriksaan agar siap dirilis; produksi bisa menunggu keputusan manusia |
| Continuous Deployment | Otomatis merilis perubahan yang memenuhi seluruh kontrol ke produksi |
| Workflow | Definisi rangkaian pekerjaan otomatis |
| Job / step | Kelompok pekerjaan / satu langkah di dalam job |
| Runner | Mesin pelaksana workflow; pada proyek ini menggunakan mesin GitHub |
| Artifact | Hasil build yang dapat dipakai lagi, misalnya container image |
| Registry | Penyimpanan container image, seperti GHCR |
| Deployment | Memasang versi aplikasi pada lingkungan tempat aplikasi dijalankan |
| Rollback | Mengembalikan layanan ke versi atau kondisi yang diketahui sehat |

Alur lengkap yang dituju:

```text
Kode lokal → Test lokal → Commit → Push → Pull Request
→ CI → Review → Merge → Build dan verifikasi artifact
→ Registry → Staging → Keputusan promosi → Production
→ Monitoring → Pemulihan bila diperlukan
```

Build/publish yang berhasil belum berarti aplikasi tersedia terus-menerus untuk pengguna. Runner GitHub bukan server hosting aplikasi permanen.

## Persiapan dan menjalankan aplikasi

### Peralatan dan pembagian tempat kerja

- Windows, Git Bash, editor kode, akun GitHub, Python.
- Komputer latihan memiliki Python 3.14 yang dijalankan melalui `py`; 14 test awal pernah diverifikasi pada versi tersebut.
- CI menguji Python 3.12 dan 3.13. Image aplikasi menggunakan Python 3.12.
- Jangan menyimpulkan seluruh versi Python kompatibel hanya dari satu run; selalu perhatikan versi yang benar-benar diuji.
- Aplikasi inti dan test menggunakan pustaka standar Python; tidak perlu memasang `pytest` untuk latihan ini.

| Lokal — Git Bash | Remote — GitHub Actions |
|---|---|
| Edit, Git, test Python, API lokal | Test matrix, Docker build/run, smoke container, publish image |
| Port API latihan: 8081 | Port smoke container di runner: 8080 |
| Tidak memerlukan Docker Engine | Docker dijalankan oleh runner Ubuntu |

**Semua blok `bash` dalam panduan lokal ini ditujukan untuk Git Bash.** Bagian berlabel “di workflow” hanya menjelaskan perintah yang dijalankan GitHub.

### Langkah 1 — Periksa tool dan folder

```bash
cd ~/Videos/cicd/cicd-practice
pwd
ls
py --version
git --version
```

Folder yang benar memuat `app.py`, `tests`, `scripts`, dan `Dockerfile`. Menjalankan discovery dari folder induk pernah membuat Python mengambil package `tests` lain dari `site-packages`.

### Langkah 2 — Jalankan aplikasi pada terminal pertama

```bash
export PORT=8081
export APP_VERSION=dev
export FAIL_READY=0
py app.py
```

Hasil yang diharapkan:

```text
Task API listening ('127.0.0.1', 8081)
```

Biarkan terminal ini berjalan. Tekan Ctrl+C jika ingin menghentikan aplikasi. Variable `export` berlaku untuk sesi terminal ini dan proses yang dijalankan darinya.

### Langkah 3 — Smoke test dari terminal kedua

```bash
cd ~/Videos/cicd/cicd-practice
py scripts/smoke.py http://127.0.0.1:8081 --expect-version dev
```

Target:

```text
SMOKE OK {'version': 'dev'}
```

Smoke test memeriksa readiness, versi, serta membuat, membaca, dan menghapus satu task sintetis. Ia tidak menjalankan server secara otomatis.

### Endpoint dan konfigurasi

| Method | Endpoint | Fungsi |
|---|---|---|
| GET | `/health` | Memastikan proses merespons |
| GET | `/ready` | Memeriksa kesiapan dengan mengakses tabel database |
| GET | `/version` | Membaca identitas versi aplikasi |
| GET | `/tasks` | Membaca daftar task |
| POST | `/tasks` | Membuat task, body `{"title":"Belajar CI"}` |
| DELETE | `/tasks/ID` | Menghapus task berdasarkan ID |

Variable aplikasi: `HOST`, `PORT`, `DB_PATH`, `APP_VERSION`, `FAIL_READY`. Default database lokal adalah `data/tasks.db`. `FAIL_READY=1` sengaja menghasilkan readiness gagal untuk simulasi; gunakan hanya pada lab.

## Testing dan membaca hasilnya

### Menjalankan test

Jalankan dari folder proyek pada Git Bash:

```bash
py -m unittest discover -s ./tests -p test_api.py -v
```

Untuk tampilan tanpa log JSON request:

```bash
py -m unittest discover -s ./tests -p test_api.py -v 1>/dev/null
```

Pada implementasi ini, log aplikasi ditulis ke stdout, sedangkan laporan unittest ke stderr. Pengalihan stdout membuat nama test dan kegagalannya tetap terlihat. Untuk diagnosis lengkap, jalankan kembali tanpa pengalihan.

Saat README ini disusun terdapat 17 metode test. Jika semua lulus, ringkasan yang diharapkan:

```text
Ran 17 tests in ...
OK
```

Angka dapat bertambah setelah menambah test baru. Test API membuat server dengan port otomatis dan database sementara; tidak memerlukan aplikasi lokal pada 8081.

### Lapisan pemeriksaan

| Jenis | Yang dibuktikan |
|---|---|
| Unit test | Fungsi validasi bekerja sesuai kontrak |
| Integration test | HTTP, validasi, dan database bekerja bersama |
| Smoke test | Fungsi inti aplikasi yang sedang berjalan dapat digunakan |

Kode HTTP error bisa merupakan hasil yang benar dalam test negatif:

| Kode | Arti / kasus latihan |
|---|---|
| 200 | Request berhasil |
| 201 | Task berhasil dibuat |
| 400 | Input tidak valid atau JSON rusak |
| 404 | Endpoint atau ID tidak ditemukan |
| 413 | Body request terlalu besar |
| 503 | Layanan belum ready |

Patokan kelulusan adalah assertion dan ringkasan test, bukan sekadar ada/tidaknya angka 400 atau 503 di log.

### Eksperimen: test mendeteksi bug

Pada branch latihan, ubah hanya batas pada kondisi validasi:

```python
len(value.strip()) > 120
```

menjadi:

```python
len(value.strip()) > 119
```

Jalankan test. `test_boundary` seharusnya menghasilkan error karena judul 120 karakter ditolak. Kembalikan batas ke 120, simpan, lalu pastikan test kembali `OK`. Jangan mengubah assertion untuk membenarkan implementasi yang salah.

### Tiga test tambahan yang sudah dipelajari

1. **`test_unicode_title`** — judul dengan Unicode/emoji diterima tanpa perubahan oleh validasi.
2. **`test_unicode_title_round_trip`** — judul dikirim melalui POST, disimpan, dan ditemukan kembali melalui GET.
3. **`test_long_title_rejected_without_saving`** — judul 121 karakter ditolak dan isi database tidak berubah.

Pelajaran penting: respons 400 saja belum cukup; periksa juga bahwa data yang ditolak tidak terlanjur tersimpan. File [tests/test_api.py](../../tests/test_api.py) adalah sumber kode test aktual.

## Git, branch, dan pull request

### Setup awal — hanya untuk repository yang belum diinisialisasi

Repository ini sudah memiliki riwayat. Perintah berikut adalah catatan pembelajaran, tidak perlu diulang pada repository aktif:

```bash
git init -b main
git config user.name "Nama Anda"
git config user.email "email-yang-ingin-dipakai@example.com"
git add .
git diff --cached --stat
git commit -m "Simpan aplikasi latihan CI/CD dan automated test"
```

Periksa file sebelum commit; `.env`, credential, dan database lokal tidak perlu masuk Git. Identitas commit dapat memakai email noreply GitHub.

Repository remote kosong dibuat tanpa README tambahan agar tidak menimbulkan riwayat berbeda. Remote dihubungkan sekali:

```bash
git remote -v
```

Hanya jika belum ada `origin`:

```bash
git remote add origin https://github.com/FachmiR4/cicd-practice.git
git push -u origin main
```

Pengguna lain harus mengganti URL dengan repository miliknya.

### Siklus kerja sehari-hari

Pastikan `git status` bersih sebelum berpindah branch. Gunakan nama branch baru untuk setiap latihan:

```bash
git status
git switch main
git pull --ff-only origin main
git switch -c latihan/perubahan-baru
```

Edit file, jalankan test, lalu:

```bash
git diff
git add NAMA_FILE_YANG_DIUBAH
git diff --cached
git commit -m "Jelaskan perubahan yang dilakukan"
git push -u origin latihan/perubahan-baru
```

`NAMA_FILE_YANG_DIUBAH` adalah placeholder; ganti dengan file sebenarnya, misalnya `tests/test_api.py` atau `README.md`.

Di GitHub: buat PR dengan base `main` dan compare branch latihan → baca diff → tunggu CI terbaru → merge jika sesuai. Perbaikan pada PR yang sama cukup di-commit dan di-push ke branch tersebut; tidak perlu membuat PR baru.

Setelah merge:

```bash
git switch main
git pull --ff-only origin main
git status
```

Jika `--ff-only` menolak, periksa perbedaan riwayat; jangan memakai force push sebagai jalan pintas. CI merah tidak otomatis melarang semua jalur merge: aturan repository perlu dikonfigurasi jika ingin check menjadi wajib.

## Referensi perintah Git dari dasar sampai lanjutan

Bagian ini melengkapi praktik CI/CD dengan fungsi, kegunaan, dan contoh perintah Git yang sering digunakan. Materi mengadaptasi cakupan PDF **Panduan Git dari Dasar sampai Senior** yang diberikan sebagai referensi; contoh Laravel disesuaikan ke proyek Python ini. Perintah di bawah adalah referensi dan latihan, bukan daftar untuk dijalankan sekaligus.

### 1. Cara Git menyimpan pekerjaan

Git adalah alat pengelolaan versi. GitHub adalah layanan hosting repository dan kolaborasi. `commit` menyimpan riwayat lokal, sedangkan `push` mengirimnya ke remote.

```text
Working directory --git add--> Staging area --git commit--> Repository lokal
                                                               |
                                                            git push
                                                               v
                                                        Repository remote
```

| Istilah | Arti dan kegunaan |
|---|---|
| Working directory | File yang sedang diedit, misalnya `app.py` |
| Staging area / index | Snapshot perubahan yang dipilih untuk commit berikutnya |
| Commit | Snapshot proyek beserta metadata dan hubungan ke parent; dapat ditelusuri dengan hash |
| Branch | Nama referensi yang bergerak mengikuti commit terbaru pada jalurnya |
| HEAD | Biasanya menunjuk branch aktif; bisa menunjuk commit langsung saat detached HEAD |
| `main` | Branch utama lokal pada proyek ini |
| `origin` | Nama singkat remote, bukan nama branch |
| `origin/main` | Catatan lokal mengenai branch `main` di remote, diperbarui saat fetch; bukan pembacaan langsung server |
| Upstream | Branch yang dilacak branch lokal, membantu status ahead/behind dan perintah pull/push |
| Pull Request | Usulan review dan integrasi pada platform seperti GitHub; bukan perintah Git dan berbeda dari `git pull` |

**Cara membaca contoh:** `COMMIT_HASH`, `GOOD_COMMIT`, `BRANCH_NAME`, dan `URL_REPO` adalah placeholder. Ganti dengan nilai sebenarnya. Jangan menulis placeholder berbentuk `<...>` di Git Bash karena tanda tersebut dapat dibaca sebagai pengalihan input/output. Tekan `q` untuk keluar dari tampilan log/diff yang memakai pager.

### 2. Perintah inti yang paling sering dipakai

Pelajari tabel ini terlebih dahulu sebelum rebase atau recovery.

| Perintah | Fungsi | Kapan dipakai |
|---|---|---|
| `git status` | Menampilkan branch, perubahan, staging, dan status konflik | Sebelum edit, pindah branch, commit, atau pull |
| `git status -sb` | Ringkasan branch dan status file | Pemeriksaan cepat |
| `git diff` | Membandingkan working directory dengan staging untuk file tracked | Memeriksa edit yang belum di-stage |
| `git diff --staged` | Membandingkan staging dengan HEAD | Memeriksa isi commit berikutnya; sama dengan `--cached` |
| `git add README.md` | Memasukkan snapshot file ke staging | Memilih file yang akan di-commit |
| `git add -p app.py` | Memilih potongan perubahan secara interaktif | Memisahkan beberapa tujuan edit dalam satu file |
| `git commit -m "docs: jelaskan alur CI"` | Membuat commit dari staging | Menyimpan perubahan yang sudah ditinjau |
| `git log --oneline -5` | Menampilkan lima commit terakhir secara ringkas | Memeriksa riwayat dan hash |
| `git switch -c latihan/nama-baru` | Membuat branch baru lalu berpindah | Memulai tugas baru dari posisi saat ini |
| `git switch main` | Berpindah ke branch yang sudah ada | Kembali ke branch utama |
| `git fetch origin` | Mengambil objek/ref remote tanpa mengintegrasikannya ke branch aktif | Memeriksa perkembangan remote dahulu |
| `git pull --ff-only origin main` | Fetch lalu memajukan branch aktif bila memungkinkan fast-forward | Memperbarui `main` lokal saat Anda memang berada di `main` |
| `git push -u origin latihan/nama-baru` | Mengirim branch dan mengatur upstream setelah berhasil | Push pertama branch latihan |
| `git push` | Mengirim perubahan sesuai konfigurasi remote/push; pada setup latihan ke upstream yang sudah diatur | Push lanjutan pada branch yang sama |

`git add` bukan proses pemantauan otomatis: jika file diedit lagi setelah `add`, jalankan `add` lagi untuk memasukkan versi terbaru. `git diff` biasa tidak menampilkan isi file untracked; lihat `git status` dan buka file tersebut.

### 3. Persiapan repository dan konfigurasi

| Perintah | Kegunaan | Catatan |
|---|---|---|
| `git --version` | Memeriksa versi Git | Berguna ketika opsi tidak dikenali |
| `git init -b main` | Membuat repository pada folder aktif | Untuk proyek baru yang belum memiliki Git |
| `git clone URL_REPO cicd-salinan` | Menyalin repository ke folder baru | Untuk mengambil proyek dari remote, bukan di dalam repository aktif |
| `git config user.name "Nama Anda"` | Mengatur nama commit untuk repository ini | Tidak mengganti login GitHub |
| `git config user.email "email@example.com"` | Mengatur email commit untuk repository ini | Dapat memakai alamat noreply GitHub |
| `git config --global user.name "Nama Anda"` | Mengatur default nama di seluruh repository akun komputer | Gunakan hanya jika memang ingin berlaku global |
| `git config --show-origin --get user.name` | Menampilkan nilai dan sumber konfigurasi | Mendiagnosis konfigurasi lokal/global yang berbeda |
| `git config --get user.email` | Memeriksa email efektif | Sebelum commit pertama |
| `git rev-parse --show-toplevel` | Menampilkan root repository | Memastikan tidak bekerja pada repository induk yang salah |
| `git help status` | Membuka bantuan perintah | Memahami opsi dengan dokumentasi lokal |
| `git status -h` | Menampilkan bantuan singkat | Referensi cepat di terminal |

### 4. Memeriksa dan memilih perubahan

| Perintah | Fungsi dan contoh penggunaan |
|---|---|
| `git diff -- app.py` | Hanya melihat edit pada `app.py` |
| `git diff --stat` | Ringkasan jumlah perubahan pada file tracked yang belum di-stage |
| `git diff --staged --stat` | Ringkasan perubahan yang akan masuk commit |
| `git diff --check` | Mendeteksi masalah whitespace pada diff; bukan lint Python atau pemeriksaan semua konflik |
| `git diff --staged --check` | Memeriksa whitespace pada perubahan staged |
| `git add .` | Men-stage perubahan di folder aktif dan turunannya; periksa dahulu agar file tak terkait tidak ikut |
| `git add -u` | Men-stage modifikasi/penghapusan file tracked, tidak menambahkan file baru |
| `git restore --staged -- README.md` | Mengeluarkan perubahan dari staging, mempertahankan edit pada working directory |
| `git ls-files` | Menampilkan file yang dilacak dalam index |
| `git check-ignore -v -- data/tasks.db` | Menunjukkan aturan ignore yang cocok; biasanya untuk file belum tracked |
| `git rm -- catatan-lama.txt` | Menghapus file tracked dan men-stage penghapusannya |
| `git rm --cached -- data/tasks.db` | Menghentikan tracking file tanpa menghapus salinan kerja; gunakan hanya jika file itu memang tracked |
| `git mv catatan.txt catatan-baru.txt` | Mengganti nama file dan men-stage hasilnya |

`.gitignore` tidak mengeluarkan file yang sudah tracked. Jika menghentikan tracking database lokal, tambahkan aturan ignore yang sesuai dan review staged diff. Jika file berisi secret pernah masuk riwayat, untrack saja tidak mencabut secret atau membersihkan commit lama.

### 5. Commit yang jelas dan riwayat yang mudah dibaca

| Perintah | Fungsi / kapan digunakan |
|---|---|
| `git commit -m "test: tambah penolakan judul panjang"` | Menyimpan satu perubahan logis dengan pesan jelas |
| `git commit --amend -m "docs: perjelas langkah publish"` | Mengganti commit terakhir dengan pesan baru; staged changes juga ikut bila ada |
| `git commit --amend --no-edit` | Mengganti commit terakhir dengan memasukkan staging, mempertahankan pesan |
| `git log --oneline --graph --decorate --all` | Melihat hubungan branch dan commit |
| `git show COMMIT_HASH` | Melihat metadata dan patch commit tertentu |
| `git show --stat HEAD` | Ringkasan perubahan commit terakhir |
| `git log --follow -- README.md` | Menelusuri riwayat satu file, termasuk rename yang dapat dideteksi |
| `git log --since="2026-10-01" --oneline` | Memfilter riwayat berdasarkan waktu |
| `git log --grep="smoke" --oneline` | Mencari teks pada pesan commit |
| `git log -S"ConnectionError" --oneline -- scripts/smoke.py` | Mencari commit yang mengubah jumlah kemunculan string tersebut |
| `git log -G"except.*ConnectionError" --oneline -- scripts/smoke.py` | Mencari patch yang cocok dengan regex |
| `git blame -L 18,28 -- scripts/smoke.py` | Menemukan commit terakhir yang terkait dengan baris tersebut; gunakan untuk konteks, bukan menyalahkan orang |

`--amend` membuat commit baru dengan hash baru. Utamakan sebelum push; jangan mengubah commit yang sudah menjadi dasar kerja orang lain tanpa koordinasi. Conventional Commits seperti `feat:`, `fix:`, `test:`, dan `docs:` adalah kebiasaan penamaan, bukan syarat bawaan Git.

### 6. Branch, remote, fetch, pull, dan push

| Perintah | Fungsi dan catatan |
|---|---|
| `git branch` | Daftar branch lokal |
| `git branch --show-current` | Nama branch aktif; kosong jika detached HEAD |
| `git branch -a` | Branch lokal dan remote-tracking |
| `git branch -vv` | Branch, upstream, dan ringkasan ahead/behind berdasarkan data lokal |
| `git switch -` | Kembali ke branch/posisi sebelumnya |
| `git switch -c rescue/cek-lama COMMIT_HASH` | Membuat branch pada commit tertentu tanpa memindahkan branch utama |
| `git branch -m nama-baru` | Mengganti nama branch aktif lokal; nama branch remote tidak otomatis ikut berubah |
| `git branch -d latihan/sudah-selesai` | Menghapus branch lokal dengan pemeriksaan merged; tetap periksa perubahan sudah masuk tujuan |
| `git remote -v` | Menampilkan URL fetch/push remote |
| `git remote add origin URL_REPO` | Menambahkan remote bernama origin jika belum ada |
| `git remote set-url origin URL_REPO` | Mengubah tujuan remote yang sudah ada; pastikan pemilik dan repository benar |
| `git remote show origin` | Memeriksa informasi remote dan hubungan branch |
| `git fetch --prune origin` | Fetch dan membersihkan remote-tracking ref yang sudah hilang di remote pada konfigurasi biasa; bukan menghapus branch lokal |
| `git log HEAD..origin/main --oneline` | Commit yang tersedia di origin/main tetapi belum terjangkau dari HEAD |
| `git log origin/main..HEAD --oneline` | Commit pada jalur HEAD yang belum terjangkau dari origin/main |
| `git diff origin/main...HEAD` | Perubahan sisi branch aktif sejak merge base dengan origin/main; berguna sebelum PR |
| `git diff origin/main HEAD` | Membandingkan isi dua titik akhir secara langsung |
| `git push --dry-run origin BRANCH_NAME` | Memeriksa rencana push tanpa mengirim pembaruan ref |
| `git push origin --delete latihan/sudah-selesai` | Menghapus branch remote; lakukan setelah merge dan koordinasi bila dipakai bersama |

Lakukan fetch sebelum menyimpulkan ahead/behind. `git pull --ff-only origin main` selalu mengintegrasikan ke **branch yang sedang aktif**, sehingga jangan menjalankannya dari branch fitur dengan asumsi memperbarui branch lokal main secara terpisah.

### 7. Merge dan penyelesaian konflik

`git merge BRANCH_NAME` menggabungkan riwayat branch tersebut ke branch aktif. Untuk proyek ini, penggabungan ke main tetap melalui PR. Berikut contoh memperbarui branch fitur dengan main:

```bash
git status
git fetch origin
git switch latihan/fitur-anda
git merge origin/main
```

Ganti nama branch dengan branch yang benar-benar ada dan mulai dari working directory bersih. Bila terjadi konflik:

```bash
git status
git diff --name-only --diff-filter=U
git diff --cc
```

Penanda konflik teks dapat berbentuk:

```text
<<<<<<< HEAD
isi dari sisi branch aktif
=======
isi dari sisi yang digabung
>>>>>>> origin/main
```

Baca kedua maksud perubahan, edit hasil yang benar, dan hapus marker. Konflik rename/delete atau file biner tidak selalu memiliki marker ini. Setelah menyelesaikan file yang terlibat:

```bash
git add app.py
py -m unittest discover -s ./tests -p test_api.py -v
git diff --staged
git merge --continue
```

Untuk membatalkan merge yang masih berjalan:

```bash
git merge --abort
```

Abort mencoba kembali ke kondisi sebelum merge; perubahan lokal yang sudah ada sebelum merge dapat menyulitkan pemulihan. Itulah alasan memulai dengan kondisi bersih.

Untuk mempelajari konflik pada file yang memang unmerged:

| Perintah | Isi yang ditampilkan |
|---|---|
| `git ls-files -u` | Entry index konflik beserta stage |
| `git show :1:app.py` | Base, bila tersedia |
| `git show :2:app.py` | Sisi ours pada operasi tersebut |
| `git show :3:app.py` | Sisi theirs pada operasi tersebut |

Jangan memilih ours/theirs untuk seluruh proyek tanpa menilai perilaku akhir. Saat rebase, ours/theirs berkaitan dengan proses replay sehingga tidak dapat diartikan sederhana sebagai “kode saya” dan “kode orang lain”.

### 8. Stash untuk menyimpan pekerjaan sementara

| Perintah | Fungsi |
|---|---|
| `git stash push -u -m "WIP sebelum review"` | Menyimpan perubahan tracked dan untracked; ignored files tidak ikut dengan `-u` |
| `git stash list` | Menampilkan daftar stash lokal |
| `git stash show -p 'stash@{0}'` | Melihat patch tracked dari stash terbaru; tambahkan `--include-untracked` bila perlu melihat file untracked |
| `git stash apply 'stash@{0}'` | Menerapkan perubahan, tetap menyimpan entry stash |
| `git stash pop 'stash@{0}'` | Menerapkan lalu menghapus entry jika berhasil; konflik biasanya mempertahankan entry |
| `git stash drop 'stash@{0}'` | Menghapus satu entry stash; lakukan setelah hasilnya diverifikasi |
| `git stash branch latihan/pulihkan-wip 'stash@{0}'` | Membuat branch dari base stash lalu mencoba menerapkannya; entry dihapus jika sukses |

Untuk pemula, pilih `apply`, periksa isi dan test, lalu `drop` entry yang benar bila sudah tidak diperlukan. `apply` tidak otomatis mengembalikan semua status staging; opsi `--index` dapat mencoba memulihkannya bila memang diperlukan. Stash bersifat lokal dan bukan backup jangka panjang.

### 9. Restore, reset, dan revert: pilih sesuai masalah

| Masalah | Perintah | Dampak |
|---|---|---|
| Salah memasukkan file ke staging | `git restore --staged -- README.md` | Mengubah index, edit lokal tetap ada |
| Ingin membuang edit unstaged satu file | `git restore -- app.py` | Mengembalikan working file dari index; edit unstaged hilang |
| Ingin mengambil isi file dari commit tertentu | `git restore --source=COMMIT_HASH -- app.py` | Mengganti working file dari sumber tersebut; review lalu stage bila sesuai |
| Commit terakhir belum dipush, ingin menyusun ulang | `git reset --soft HEAD~1` | Memundurkan HEAD/branch satu parent, index dan working files dipertahankan |
| Commit terakhir belum dipush, ingin memilih staging ulang | `git reset --mixed HEAD~1` | Memundurkan HEAD dan mengatur ulang index; working files dipertahankan |
| Ingin membuang perubahan tracked dan berpindah ke commit | `git reset --hard COMMIT_HASH` | Menimpa index/working files; dapat menghapus untracked yang menghalangi penulisan |
| Commit sudah dibagikan, perlu membatalkan dampaknya | `git revert COMMIT_HASH` | Membuat commit pembalik tanpa menghapus commit lama |

**Perintah discard/reset hard bukan cara membersihkan error secara umum.** `HEAD~1` memerlukan parent; contoh ini tidak berlaku pada repository yang hanya memiliki root commit. Sumber default `git restore FILE` adalah index, bukan selalu commit terakhir. Detail: [git restore](https://git-scm.com/docs/git-restore), [git reset](https://git-scm.com/docs/git-reset).

Untuk membatalkan perubahan yang sudah masuk main, buat branch perbaikan dari main terbaru, jalankan revert pada commit yang benar, test, lalu ajukan PR. Revert merge commit membutuhkan pemilihan mainline (`-m`) dan pemahaman dampaknya pada merge berikutnya; jangan menyalin opsi itu tanpa memeriksa parents. [git revert](https://git-scm.com/docs/git-revert)

Jika revert konflik, selesaikan file dan stage sebelum `git revert --continue`. Untuk membatalkan revert yang masih berlangsung, gunakan `git revert --abort`.

### 10. Rebase dan interactive rebase

Rebase menerapkan ulang perubahan commit di atas base lain. Commit hasil replay umumnya memiliki hash baru. Gunakan untuk branch pribadi dan pahami dampaknya bila branch sudah dibagikan.

| Perintah | Fungsi |
|---|---|
| `git fetch origin` | Memperbarui informasi base remote |
| `git rebase origin/main` | Menerapkan ulang commit branch aktif di atas origin/main |
| `git rebase --continue` | Melanjutkan setelah konflik diselesaikan dan di-stage |
| `git rebase --abort` | Membatalkan rebase yang masih berjalan |
| `git rebase --skip` | Melewati commit saat ini; perubahan commit tersebut dapat hilang dari hasil replay |
| `git rebase -i HEAD~3` | Menyunting susunan tiga commit terakhir; hanya bila sejarah memiliki parent yang diperlukan |

Pada daftar interactive rebase: `pick` mempertahankan, `reword` mengubah pesan, `edit` berhenti untuk penyesuaian, `squash` menggabungkan dengan commit sebelumnya sambil mengedit pesan, `fixup` menggabungkan tanpa pesan commit tersebut, dan `drop` menghilangkannya dari riwayat hasil.

Jika branch pribadi yang telah dipush perlu diperbarui setelah rewrite, `git push --force-with-lease origin BRANCH_NAME` lebih terkontrol daripada `--force`: pembaruan ditolak bila ref remote berbeda dari perkiraan lease. Ini tetap menulis ulang riwayat remote; fetch latar belakang dapat memengaruhi perkiraan default. Jangan gunakan pada main/branch bersama tanpa koordinasi dan kebijakan yang jelas. [git push](https://git-scm.com/docs/git-push)

### 11. Cherry-pick, reflog, dan bisect

| Perintah | Fungsi dan waktu penggunaan |
|---|---|
| `git cherry-pick -x COMMIT_HASH` | Menerapkan perubahan commit tertentu ke branch aktif dengan referensi asal pada pesan, berguna untuk hotfix terisolasi |
| `git cherry-pick --continue` | Melanjutkan setelah konflik diselesaikan dan di-stage |
| `git cherry-pick --abort` | Membatalkan rangkaian cherry-pick yang sedang berlangsung |
| `git reflog` | Melihat riwayat perpindahan referensi lokal, berguna setelah amend/reset/rebase |
| `git reflog show main` | Membaca reflog branch main lokal |
| `git show COMMIT_HASH` | Memeriksa kandidat commit yang ditemukan sebelum memulihkan |
| `git switch -c rescue/pekerjaan COMMIT_HASH` | Membuat branch pada commit yang ingin diselamatkan |
| `git bisect start` | Memulai pencarian commit penyebab regresi |
| `git bisect bad` | Menandai posisi saat ini bermasalah |
| `git bisect good GOOD_COMMIT` | Menentukan batas commit yang diketahui sehat |
| `git bisect good` / `git bisect bad` | Memberikan hasil pengujian commit yang dipilih Git |
| `git bisect skip` | Menandai commit yang tidak dapat diuji; hasil akhir bisa menjadi kurang spesifik |
| `git bisect reset` | Mengakhiri sesi bisect dan kembali ke posisi awal sesi |

Reflog bukan tempat menyimpan semua edit yang belum di-commit dan memiliki retensi; ia tidak menjamin pemulihan file yang belum pernah disimpan sebagai objek Git. Setelah menemukan commit penting, buat rescue branch agar mudah ditelusuri.

Bisect otomatis dapat memakai test Python:

```bash
git bisect start HEAD GOOD_COMMIT
git bisect run py -m unittest discover -s ./tests -p test_api.py
git bisect reset
```

Gunakan hanya ketika test reproduksi tersedia dan dapat dijalankan pada rentang commit. Exit code 0 dinilai good, 1–127 selain 125 dinilai bad, 125 berarti skip. Test yang hilang atau dependency tidak cocok bisa menghasilkan diagnosis salah. Mulai dari kondisi bersih dan jalankan `bisect reset` setelah selesai.

### 12. Tag, worktree, dan kemampuan lanjutan

| Perintah | Fungsi / kapan relevan |
|---|---|
| `git tag --list` | Daftar penanda versi |
| `git tag -a v0.1.0 -m "Baseline latihan CI"` | Membuat annotated tag pada HEAD setelah verifikasi |
| `git show v0.1.0` | Memeriksa target dan keterangan tag |
| `git push origin v0.1.0` | Mengirim tag tertentu; push branch biasa tidak otomatis mengirim semua tag |
| `git worktree list` | Menampilkan checkout tambahan dari repository yang sama |
| `git worktree add -b latihan/hotfix ../cicd-hotfix main` | Membuat folder kerja dan branch baru dari main tanpa berpindah pada folder aktif |
| `git worktree remove ../cicd-hotfix` | Menghapus worktree yang sudah selesai dan bersih; bukan menghapus branch-nya |
| `git submodule update --init --recursive` | Menyiapkan submodule yang sudah didefinisikan proyek; tidak diperlukan starter ini |
| `git sparse-checkout init --cone` | Mengaktifkan checkout sebagian folder untuk repository besar |
| `git sparse-checkout set docs scripts` | Memilih folder checkout; jangan dipakai pada lab API ini karena file test lain bisa tidak tersedia |
| `git sparse-checkout disable` | Kembali ke checkout penuh |
| `git lfs track "*.psd"` | Mendefinisikan pola Git LFS jika ekstensi LFS telah dipasang; commit juga `.gitattributes` |
| `git commit -S -m "Signed change"` | Menandatangani commit jika signing key sudah dikonfigurasi |
| `git log --show-signature -1` | Memeriksa informasi signature dan hasil verifikasinya sesuai konfigurasi trust |

Tag Git berbeda dari tag container; GitHub Release juga fitur terpisah dari tag Git. Workflow publish proyek ini memicu push ke main, sehingga membuat tag saja tidak otomatis menjalankan workflow publish yang ada.

Worktree berbagi database Git tetapi memiliki working directory/index sendiri; branch yang sama umumnya tidak dapat di-checkout pada dua worktree sekaligus. Submodule menunjuk commit repository lain. Subtree memasukkan proyek eksternal ke subdirektori dengan strategi integrasi tersendiri. LFS menyimpan pointer di Git dan konten pada layanan LFS; menerapkan pola baru tidak otomatis memindahkan binary dari riwayat lama. Semua ini materi opsional, bukan syarat belajar CI dasar.

Hook lokal seperti pre-commit/pre-push dapat membantu menjalankan pemeriksaan, tetapi dapat dilewati dan tidak menggantikan CI. Signature menghubungkan commit ke key yang diverifikasi; ia tidak menjamin isi kode aman.

### 13. Perintah yang perlu perhatian sebelum dijalankan

| Perintah | Risiko / pemeriksaan dahulu |
|---|---|
| `git restore -- FILE` | Membuang edit unstaged file tracked; baca diff dahulu |
| `git reset --hard COMMIT_HASH` | Menimpa perubahan; backup branch hanya menjaga commit, bukan semua edit belum tersimpan |
| `git clean -nd` | Preview file/folder untracked yang akan dihapus; langkah ini hanya menampilkan |
| `git clean -fd` | Benar-benar menghapus file/folder untracked; Git tidak dapat memulihkannya jika belum pernah disimpan |
| `git clean -fdx` | Juga menghapus ignored files, dapat mencakup `.env`, environment lokal, dan data; bukan langkah cleanup rutin lab |
| `git branch -D BRANCH_NAME` | Menghapus branch lokal tanpa pemeriksaan merged |
| `git push --force` | Dapat mengganti riwayat remote dan menghilangkan jalur kerja kolaborator |
| `git stash clear` | Menghapus semua entry stash; gunakan pemeriksaan per-entry sebagai pilihan awal |

Tabel ini menjelaskan konsekuensi, bukan menyarankan untuk menjalankan semuanya. Saat salah edit, pilih tindakan paling sempit: unstage satu file jika masalahnya staging; jangan langsung reset seluruh repository.

### 14. Tiga latihan praktik yang sesuai proyek

**Latihan A — Bedakan edit dan staging.** Pada branch dokumentasi yang baru, edit satu kalimat README. Jalankan `git diff`, kemudian `git add README.md` dan `git diff --staged`. Jalankan `git restore --staged -- README.md`: perubahan kembali unstaged tetapi isi edit tetap ada. Stage lagi, commit, lalu buat PR. Bukti selesai: dapat menjelaskan mengapa `git diff` bisa kosong saat perubahan masih ada di staging.

**Latihan B — Cari asal perbaikan smoke test.** Jalankan perintah baca berikut tanpa mengubah file:

```bash
git log --oneline -- scripts/smoke.py
git log -S"ConnectionError" --oneline -- scripts/smoke.py
git blame -L 18,28 -- scripts/smoke.py
```

Pilih hash yang ditemukan, lalu `git show COMMIT_HASH`. Bukti selesai: temukan perubahan retry dan jelaskan kaitannya dengan kegagalan koneksi CI.

**Latihan C — Stash satu pekerjaan dokumentasi.** Dari branch pribadi, edit README, jalankan `git stash push -m "WIP dokumentasi"`, periksa working directory dengan `git status`, lalu `git stash apply 'stash@{0}'`. Pastikan edit kembali. Setelah edit tersimpan sebagai commit, hapus hanya entry stash yang telah Anda verifikasi. Jangan membuat stash baru di tengah latihan jika belum memahami perubahan nomor `stash@{0}`.

Latihan rebase, reset, clean, dan bisect sebaiknya dilakukan pada repository eksperimen terpisah setelah menguasai tiga latihan ini.

### 15. Alur kerja Git yang digunakan dalam pembelajaran CI/CD

```text
Periksa status → Update main → Buat branch → Edit
→ Test lokal → Review diff → Stage → Commit → Push
→ PR → Review + CI → Merge → Update main lokal
```

Jika PR merah: buka log → perbaiki pada branch PR yang sama → test → commit → push → tunggu run commit terbaru. Jika commit sudah terlanjur dibagikan dan perlu dibatalkan: utamakan revert melalui branch/PR. Jika commit terlihat hilang: periksa reflog dan buat rescue branch sebelum mengubah riwayat lagi.

**Urutan penguasaan:** status/diff/add/commit → branch/remote/push/pull → PR dan konflik → stash/restore/revert → log/blame/reflog → rebase/cherry-pick → bisect/worktree → praktik tim, signing, dan pengelolaan repository besar.

Referensi pendamping: PDF **Panduan Git dari Dasar sampai Senior** yang dilampirkan pengguna, serta [manual Git](https://git-scm.com/docs) dan [Pro Git](https://git-scm.com/book/en/v2). Materi PDF dipakai sebagai cakupan pembelajaran; contoh di sini disesuaikan dengan Git Bash, Python, dan alur PR proyek ini.

## CI dengan GitHub Actions

File aktif: [.github/workflows/ci.yml](../../.github/workflows/ci.yml), nama workflow **CI Practice**.

| Konfigurasi | Perilaku |
|---|---|
| `pull_request` menuju `main` | Memeriksa perubahan sebelum merge |
| `push` ke `main` | Memeriksa hasil setelah masuk branch utama |
| Job `test` | Syntax check dan test pada Python 3.12 serta 3.13 |
| Job `container`, `needs: test` | Build dan smoke container hanya setelah test berhasil |
| `contents: read` | Akses baca kode untuk workflow ini |
| `if: always()` pada log/cleanup | Tetap menampilkan log dan membersihkan container setelah kegagalan |

Push ke branch latihan yang belum memiliki PR tidak memicu workflow ini. Buka PR menuju `main` untuk menjalankan pemeriksaannya.

`compileall` memeriksa sintaks Python, bukan lint lengkap. Cleanup yang memakai `|| true` tidak boleh disalin ke test wajib karena dapat menyembunyikan kegagalan.

### Membaca hasil CI

1. Buka **Actions → CI Practice**.
2. Pilih run untuk commit terbaru yang ingin diperiksa.
3. Buka job `test` atau `container`.
4. Baca step pertama yang gagal, lalu rincian error.
5. Setelah memperbaiki dan push, periksa run commit baru. Run lama yang gagal tetap menjadi riwayat.

Alur yang telah dipraktikkan: perubahan salah → CI gagal → perbaikan → CI hijau. Kesalahan pernah berasal dari validasi judul, retry koneksi, dan indentasi; gejalanya perlu dibedakan.

## Docker melalui runner GitHub

**Perintah Docker di bagian ini hanya untuk dipahami dari workflow, bukan dijalankan pada komputer latihan yang engine-nya tidak aktif.**

| Konsep | Makna |
|---|---|
| Dockerfile | Resep membangun image |
| Image | Paket aplikasi dan runtime |
| Container | Instance proses yang menjalankan image |
| Tag | Nama versi image, dapat dipindahkan |
| Digest | Identitas konten image/manifest berdasarkan hash |

Baca resep tanpa Docker lokal:

```bash
cat Dockerfile
cat .github/workflows/ci.yml
```

### Instruksi Dockerfile proyek

| Instruksi | Tujuan |
|---|---|
| `FROM python:3.12-slim` | Menggunakan runtime Python dari image dasar |
| `ARG APP_VERSION=dev` | Menerima nilai versi ketika build |
| `ENV ...` | Konfigurasi default aplikasi dalam image |
| `WORKDIR /app` | Menentukan folder kerja |
| `RUN mkdir /data && chown 10001:10001 /data` | Menyiapkan direktori database ketika build |
| `COPY app.py /app/app.py` | Menyalin kode ke image |
| `USER 10001:10001` | Menjalankan proses dengan pengguna non-root |
| `EXPOSE 8080` | Mendokumentasikan port; tidak otomatis mempublikasikannya |
| `CMD ["python", "app.py"]` | Perintah awal saat container dijalankan |

`RUN` dilaksanakan ketika build; `CMD` menentukan perintah saat run.

### Perintah yang dijalankan di workflow

```text
docker build --build-arg APP_VERSION="$GITHUB_SHA" -t cicd-practice:ci .
docker run -d --name cicd-smoke -p 127.0.0.1:8080:8080 cicd-practice:ci
python scripts/smoke.py http://127.0.0.1:8080 --expect-version "$GITHUB_SHA"
```

`GITHUB_SHA` disediakan oleh GitHub Actions dan mengidentifikasi commit yang sedang diuji; pada event PR nilainya dapat menunjuk merge commit sementara. Workflow menggunakan nilai yang sama untuk build dan verifikasi versi.

### Membaca log build

Navigasi: **Actions → run → container → Build container**.

| Log | Arti |
|---|---|
| `extracting sha256:...` | Mengekstrak layer image dasar |
| `WORKDIR`, `RUN`, `COPY` | Instruksi build sedang dieksekusi |
| `CACHED` | Menggunakan hasil yang masih sesuai dari cache |
| `exporting to image` | Menyusun hasil menjadi image |
| `naming to docker.io/library/cicd-practice:ci` | Memberi nama image lokal di runner, belum upload ke Docker Hub |
| `SMOKE OK {'version': '...'}` | Kesiapan, versi, dan transaksi sintetis berhasil diperiksa |

Image pada runner CI belum menjadi artifact registry yang tersedia untuk deployment. Itu tujuan tahap berikutnya.

## Publikasi image ke GHCR

File aktif sudah ditemukan: [.github/workflows/publish.yml](../../.github/workflows/publish.yml). Nama workflow: **Publish verified image**. Template asalnya: [examples/publish.yml.example](../../examples/publish.yml.example).

Jangan menyalin ulang template jika file aktif sudah ada dan sudah dimodifikasi. Untuk repository baru yang belum mengaktifkannya, latihan awal menggunakan:

```bash
cp -i examples/publish.yml.example .github/workflows/publish.yml
```

Review, commit, buat PR, lalu merge setelah pemeriksaan yang relevan berhasil. Workflow publish dipicu oleh **push ke `main`**, bukan ketika PR baru dibuka.

### Urutan workflow publish

1. Checkout dan siapkan Python.
2. Jalankan unit/integration test.
3. Tentukan nama image: `ghcr.io/fachmir4/cicd-practice`.
4. Build image dengan tag commit dan versi aplikasi dari commit tersebut.
5. Jalankan image dan lakukan smoke test.
6. Login GHCR menggunakan `GITHUB_TOKEN` dengan `packages: write`.
7. Push **image yang sama yang telah diuji**.
8. Ambil digest dan tulis ke ringkasan workflow.
9. Tampilkan log, bersihkan container, dan logout.

Workflow publish melakukan verifikasinya sendiri; ia tidak menunggu workflow `CI Practice` secara lintas-workflow. Kedua workflow dapat berjalan bersamaan pada push `main`. Jika menambah gate wajib seperti scan, letakkan gate itu sebelum push pada alur publish juga.

### Bukti berhasil

Buka **Actions → Publish verified image → run terbaru**. Periksa step `Push the tested image` dan `Capture digest`. Ringkasan seharusnya memuat referensi nyata berbentuk:

```text
ghcr.io/fachmir4/cicd-practice@sha256:DIGEST_SEBENARNYA
```

Simpan commit, digest, dan tautan run ke [docs/release-record.md](../../docs/release-record.md). Package dapat ditinjau melalui bagian Packages pada akun/repository terkait. Publikasi pertama default-nya private; tidak perlu mengubahnya menjadi public untuk latihan.

Token workflow tersedia otomatis; jangan menempelkan credential ke Git. Jika mendapat 403, periksa izin package, repository, dan kebijakan organisasi. Jangan langsung memperluas izin seluruh akun.

**Checkpoint:** file publish sudah ada, tetapi keberhasilan publikasi perlu dibuktikan dari run dan digest. Image terbit bukan berarti aplikasi telah di-deploy.

## Kendala yang pernah ditemukan

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

### Retry readiness yang sudah diperbaiki

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

### Git Bash versus CMD

| Kebutuhan | Git Bash — digunakan sekarang | CMD — latihan sebelumnya |
|---|---|---|
| Folder test | `./tests` | `.\tests` |
| Sembunyikan stdout | `1>/dev/null` | `1>NUL` |
| Set variable | `export PORT=8081` | `set PORT=8081` |
| Baca file | `cat README.md` | `type README.md` |

Jangan mengetik simbol prompt `$` atau potongan `C:\...>` sebagai bagian command. Jika file `NUL` muncul kembali, periksa folder dengan `pwd`/`git status` sebelum menjalankan `rm -- NUL` pada file tersebut.

## Roadmap awal sampai akhir

Tahap 1–9 merangkum pembelajaran yang sudah dijalani. Tahap 10 adalah checkpoint publikasi yang perlu dikonfirmasi. Tahap 11–20 merupakan rencana lanjutan; jangan menganggapnya sudah diimplementasikan dalam starter.

| Tahap | Materi dan praktik | Bukti untuk melanjutkan |
|---|---|---|
| 1 | Terminal, path, Python, Git; bedakan Git Bash dan CMD | Tool dikenali dan folder proyek benar |
| 2 | HTTP, health, readiness, versi, operasi task | API lokal dan smoke berhasil |
| 3 | Unit/integration test, assertion, input negatif | Seluruh test yang tersedia lulus |
| 4 | Eksperimen perubahan 120→119→120 | Dapat menjelaskan test gagal lalu pulih |
| 5 | Commit, branch, remote, push | Riwayat lokal dan remote dapat ditelusuri |
| 6 | Pull request, review, merge, sinkronisasi | PR ditinjau, CI hijau, main lokal terbarui |
| 7 | Trigger, runner, job, step, dependency, log CI | Dapat menemukan step gagal dan penyebabnya |
| 8 | Tambah test Unicode, HTTP round trip, penolakan input | Tiga test tambahan dan bukti run |
| 9 | Dockerfile, image/container, build/run melalui GitHub | Build serta smoke container berhasil |
| 10 | Registry GHCR, tag commit, digest, token | Image tersimpan dan digest tercatat |
| 11 | Kualitas/security gate: lint, dependency/image scan, SBOM | Temuan ditinjau dan gate penting memblokir publish |
| 12 | Menyiapkan target staging dan konfigurasi | Lingkungan terpisah dengan akses serta data lab |
| 13 | CD staging dari artifact registry | Digest tepat terpasang, smoke dan versi benar |
| 14 | Rollback dan latihan rilis gagal | Versi sehat pulih dan data diverifikasi |
| 15 | Database bersama, migrasi expand–migrate–contract | Versi lama/baru kompatibel selama transisi |
| 16 | Promosi production, kontrol akses, keputusan rilis | Artifact sama dipromosikan dengan bukti dan persetujuan yang diperlukan |
| 17 | Logs, metrics, SLI/SLO, runbook, insiden | Gangguan terdeteksi dan latihan pemulihan terdokumentasi |
| 18 | Efisiensi, cache, concurrency, reusable workflow | Durasi membaik tanpa mengurangi pemeriksaan wajib |
| 19 | Opsional: IaC, Kubernetes, Helm/Kustomize, GitOps | Desired state dapat dibuat ulang dan rollout diverifikasi |
| 20 | Proyek akhir dan presentasi portfolio | Demo dari perubahan sampai pemulihan, dengan catatan keterbatasan |

### Tahap 11 — Kualitas dan keamanan

Tambahkan linter dan aturan yang dipahami. Scan image/dependency, hasilkan SBOM, dan dokumentasikan keputusan untuk temuan. Pin action ke full commit SHA yang ditinjau serta kelola pembaruannya. Pisahkan kode PR tidak tepercaya dari credential deployment. Gunakan OIDC ketika target mendukungnya dengan trust yang dibatasi secara tepat.

**Latihan:** buat temuan atau pelanggaran aturan di branch lab; buktikan gate menolak kandidat sebelum artifact dipublikasikan. Jangan memakai secret asli untuk simulasi.

### Tahap 12–14 — Staging, CD, dan rollback

Pilih target remote yang dapat menjalankan image, sesuai akses dan anggaran; komputer lokal tetap hanya menjadi editor/client. Akun, biaya, autentikasi, storage, dan endpoint harus ditentukan sebelum provisioning. Jangan mencoba menjadikan GitHub runner server permanen.

Urutan praktik: siapkan staging → simpan konfigurasi/secret sesuai lingkungan → tarik artifact dengan digest → jalankan layanan → verifikasi versi dan transaksi → catat rilis. Setelah baseline sehat, pasang kandidat lab yang gagal readiness dan uji pemulihan ke artifact sebelumnya.

**Bukti:** commit dan digest, URL staging, hasil smoke, waktu pemulihan, serta pemeriksaan data. Deployment sukses tidak cukup jika fungsi pengguna rusak. Rollback image tidak otomatis membalikkan schema, secret, atau isi database.

### Tahap 15–16 — Data dan production

Starter SQLite dan HTTP server ini perlu dikembangkan sebelum dijadikan layanan production. Tambahkan autentikasi/otorisasi, server aplikasi yang sesuai, database bersama jika memakai banyak instance, pengelolaan koneksi, dan pengujian kegagalan.

Latih migrasi bertahap: tambah struktur kompatibel → migrasi data → alihkan penggunaan → hapus struktur lama setelah jendela rollback selesai. Verifikasi backup dengan latihan restore ke lingkungan terpisah.

Promosikan **artifact staging yang sama** ke production, bukan build ulang. Tetapkan kontrol lingkungan, serialisasi deployment, dan kriteria batal sebelum rilis. Production pada capstone boleh disimulasikan, asalkan diberi label jelas.

### Tahap 17–19 — Operasi dan pendalaman

Pasang penanda versi pada log, ukur error/latency, tentukan SLI dan target SLO yang relevan. Simulasikan insiden, ikuti runbook, catat timeline, dan perbaiki proses.

Optimalkan pipeline berdasarkan pengukuran. Cache harus boleh hilang tanpa merusak kebenaran build. Jangan membatalkan deployment aktif secara sembarang. Reusable workflow membutuhkan kontrak input/output dan pengelolaan versi.

IaC dan Kubernetes/GitOps adalah jalur opsional setelah alur sederhana dikuasai. Gunakan lingkungan remote/lab yang sesuai kemampuan perangkat. Manifest starter Kubernetes memakai `emptyDir`: data hilang saat Pod diganti dan tidak dibagi antar-Pod. Jangan meningkatkan replica dengan menganggap SQLite lokal otomatis menjadi database bersama.

### Tahap 20 — Capstone

Siapkan proyek dengan fitur sendiri, test positif/negatif, PR, CI, image bertag commit, digest, scan/SBOM, staging, promosi, dan latihan pemulihan. Sertakan diagram, keputusan teknis, [catatan rilis](../../docs/release-record.md), dan [laporan insiden](../../docs/incident-report.md).

Demo: perubahan benar → test salah menolak perubahan → perbaikan → build/publish → staging → fault → rollback → verifikasi data. Jelaskan bagian yang benar-benar dijalankan dan yang hanya disimulasikan. Kemampuan profesional dinilai dari keputusan dan bukti yang konsisten, bukan jumlah alat.

## Cara belajar dan bukti kelulusan

Gunakan sesi 45–90 menit: baca satu konsep → praktik → ubah satu variabel → amati hasil → catat penyebab dan perbaikan. Prediksi hasil sebelum menjalankan command. Jangan langsung melanjutkan jika belum memahami error tahap sebelumnya.

Template catatan sesi:

```text
Tanggal dan tahap:
Tujuan:
Perintah / perubahan:
Prediksi:
Hasil sebenarnya:
Error dan penyebab:
Perbaikan:
Bukti (commit, run, digest, log):
Langkah berikutnya:
```

Checklist setiap tahap:

- [ ] Dapat menjelaskan tujuan dengan kalimat sendiri.
- [ ] Dapat mengulang langkah dari folder dan terminal yang benar.
- [ ] Memiliki bukti hasil yang diharapkan.
- [ ] Dapat menjelaskan satu kegagalan dan perbaikannya.
- [ ] Data serta credential lab ditangani sesuai kebutuhan.
- [ ] Commit dan dokumentasi menjelaskan perubahan.

## Struktur proyek dan referensi

```text
app.py                         API latihan
tests/test_api.py              Unit dan integration tests
scripts/smoke.py               Pemeriksaan API yang sudah berjalan
scripts/deploy-local.ps1       Contoh deployment Docker lokal (bukan jalur aktif)
Dockerfile                     Resep image
.dockerignore                  Pengecualian build context
.gitignore                     Pengecualian file lokal dari Git
.github/workflows/ci.yml       CI test dan container
.github/workflows/publish.yml  Build, verifikasi, dan upload GHCR
examples/                      Template pembelajaran tambahan
compose.yaml                   Lab Compose opsional
k8s/lab.yaml                   Manifest Kubernetes lab, data sementara
docs/                          Template catatan rilis dan insiden
```

### Batas starter dan lingkungan

API belum memiliki autentikasi dan memakai `http.server` pustaka standar; jangan mengeksposnya sebagai layanan production. Bind lokal default adalah `127.0.0.1`; container memakai `0.0.0.0` di dalam jaringan container. Named volume Compose berbeda dari `emptyDir` Kubernetes. Jangan menganggap data tetap ada setelah semua jenis penggantian runtime.

Repository private memakai kuota Actions sesuai paket akun. Periksa pemakaian sebelum menjalankan banyak workflow atau menyimpan banyak artifact. Tidak ada deployment remote permanen yang dibuat hanya dengan mengaktifkan CI/publish.

### Dokumentasi resmi

- [Git: buku Pro Git](https://git-scm.com/book/en/v2)
- [Sintaks workflow GitHub Actions](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)
- [GitHub-hosted runners](https://docs.github.com/en/actions/concepts/runners/github-hosted-runners)
- [Publikasi image dari GitHub Actions](https://docs.github.com/en/actions/tutorials/publish-packages/publish-docker-images)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Kuota GitHub Actions](https://docs.github.com/en/billing/concepts/product-billing/github-actions)
- [Docker dengan GitHub Actions](https://docs.docker.com/build/ci/github-actions/)
- [Batas HTTP server Python](https://docs.python.org/3.12/library/http.server.html)
- [Kubernetes probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [Argo CD](https://argo-cd.readthedocs.io/en/stable/)

Materi di README ini melengkapi modul utama dan Buku Praktik 24 Lab. Untuk kondisi perangkat saat ini, ikuti jalur **lokal untuk Python/Git, remote untuk container**, kemudian pilih target deployment saat tahap staging dimulai.
