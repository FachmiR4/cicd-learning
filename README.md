# CI/CD Learning Path — Task API

Panduan belajar **pemula → menengah → advanced → praktik senior**, dengan proyek Python yang dikembangkan bertahap. Diperbarui **29 Oktober 2026**.

[Roadmap](docs/roadmap.md) · [Mulai belajar](docs/fondasi-dan-ci.md) · [Referensi Git](docs/git-reference.md) · [Troubleshooting](docs/troubleshooting.md) · [Catatan kemajuan](docs/progress.md)

> **Jalur perangkat ringan:** tulis kode, jalankan Python, dan gunakan Git di komputer sendiri. Build image serta pengujian Docker berjalan di GitHub Actions. Docker Desktop, WSL, dan Kubernetes lokal tidak menjadi prasyarat.

Repository: [FachmiR4/cicd-practice](https://github.com/FachmiR4/cicd-practice) · [GitHub Actions](https://github.com/FachmiR4/cicd-practice/actions)

## Mulai dari sini

| Kebutuhan Anda | Buka |
|---|---|
| Ingin tahu urutan dari nol sampai praktik senior | [Roadmap delapan level](docs/roadmap.md) |
| Belum lancar terminal, Git, test, atau membaca CI | [Fondasi dan CI](docs/fondasi-dan-ci.md) |
| CI sudah berhasil; ingin memahami image, registry, dan CD | [Container dan CD](docs/container-dan-cd.md) |
| Ingin memperdalam security, reliability, dan desain tim | [Advanced dan senior](docs/advanced-dan-senior.md) |
| Lupa fungsi suatu perintah Git | [Referensi perintah Git](docs/git-reference.md) |
| Menemukan error terminal, test, atau Docker | [Troubleshooting berdasarkan pengalaman proyek](docs/troubleshooting.md) |
| Ingin membuktikan progres, bukan hanya selesai membaca | [Tracker kompetensi dan bukti](docs/progress.md) |

## Roadmap singkat

| Level | Fokus | Hasil yang dibuktikan |
|---|---|---|
| 0 — Fondasi | Terminal, Python, HTTP, lingkungan | API lokal dan smoke test berhasil |
| 1 — Beginner | Git, test, branch, PR | Perubahan salah terdeteksi lalu diperbaiki |
| 2 — Intermediate CI | Workflow, runner, matrix, quality gate | CI membantu keputusan merge |
| 3 — Artifact | Dockerfile, registry, tag, digest | Image teruji tersimpan dan terlacak |
| 4 — Applied CD | Staging, konfigurasi, promosi, rollback | Artifact yang dipilih terpasang dan dapat dipulihkan |
| 5 — Advanced | Security, supply chain, IaC | Akses dan perubahan infrastruktur terkendali |
| 6 — Senior practice | Reliability, data, observability, platform | Rilis dan insiden ditangani dengan bukti |
| 7 — Mastery berkelanjutan | Arsitektur, tradeoff, standar tim, mentoring | Keputusan dapat dipertanggungjawabkan dan diajarkan |

“Senior” dan “mastery” adalah kemampuan serta tanggung jawab, bukan sertifikat otomatis setelah beberapa minggu. Lanjut level setelah exit criteria terpenuhi. Kubernetes adalah pilihan pendalaman, bukan syarat setiap layanan.

## Mulai cepat di Git Bash

Jalankan dari root proyek. Untuk instalasi yang telah digunakan pada komputer latihan:

```bash
cd ~/Videos/cicd/cicd-practice
py --version
git --version
py -m unittest discover -s ./tests -p test_api.py -v
```

Saat dokumentasi diperbarui, file test berisi **17 metode test**. Jumlah ini inventaris kode, bukan klaim pengujian baru pada setiap pembaruan dokumentasi. Jika semua lulus, ringkasan menjadi `Ran 17 tests` dan `OK`.

Untuk menyembunyikan log request JSON sambil mempertahankan laporan unittest:

```bash
py -m unittest discover -s ./tests -p test_api.py -v 1>/dev/null
```

**Terminal pertama — jalankan aplikasi:**

```bash
export PORT=8081
export APP_VERSION=dev
export FAIL_READY=0
py app.py
```

**Terminal kedua — periksa aplikasi yang sudah berjalan:**

```bash
cd ~/Videos/cicd/cicd-practice
py scripts/smoke.py http://127.0.0.1:8081 --expect-version dev
```

Target hasil: `SMOKE OK {'version': 'dev'}`. Hentikan server dengan Ctrl+C pada terminal pertama. Unit/integration test membuat server serta database sementara sendiri, sehingga tidak memerlukan server manual ini.

Lokal menggunakan launcher `py` (Python 3.14 tersedia pada perangkat latihan); CI menguji Python 3.12/3.13 dan image memakai Python 3.12. Gunakan `./tests` dan `/dev/null` untuk Git Bash; sintaks CMD `1>NUL` pernah membuat file sampah bernama `NUL`.

## Cara kerja proyek

```text
Komputer: edit → test lokal → branch → commit → push
GitHub:   PR → CI → review → merge
          main → test → build image → smoke → publish GHCR
Lanjutan: pilih digest → staging → verifikasi → promosi → observasi/pemulihan
```

| Workflow | Pemicu | Yang dilakukan |
|---|---|---|
| [CI Practice](.github/workflows/ci.yml) | PR menuju main dan push main | Syntax check, test matrix, build dan smoke container |
| [Publish verified image](.github/workflows/publish.yml) | Push main | Test, build sekali, smoke, push image, catat digest |

Kedua workflow dapat berjalan bersamaan. Publish melakukan verifikasinya sendiri, bukan otomatis menunggu hasil workflow CI lainnya. Menambahkan gate wajib harus menjamin gate itu juga berada pada jalur sebelum publikasi/promosi.

Runner GitHub bersifat sementara. Build hijau bukan bukti aplikasi tersedia sebagai layanan permanen, dan publish image bukan deployment. `$GITHUB_SHA` serta perintah Docker dalam YAML dijalankan pada runner; tidak perlu menyalinnya ke terminal lokal.

## Endpoint latihan

| Method | Path | Fungsi |
|---|---|---|
| GET | `/health` | Proses merespons |
| GET | `/ready` | Akses tabel database dapat diperiksa |
| GET | `/version` | Identitas versi aplikasi |
| GET | `/tasks` | Daftar task |
| POST | `/tasks` | Buat task dengan JSON `{"title":"Belajar CI/CD"}` |
| DELETE | `/tasks/ID` | Hapus task berdasarkan ID |

Variable: `HOST`, `PORT`, `DB_PATH`, `APP_VERSION`, `FAIL_READY`. Default data lokal: `data/tasks.db`. Fault `FAIL_READY=1` hanya digunakan dalam latihan kegagalan yang terkontrol.

## Posisi pembelajaran sekarang

- API lokal, smoke, Git/PR, dan CI pernah ditunjukkan berhasil.
- Tiga test tambahan mencakup Unicode, round trip HTTP/database, dan penolakan judul panjang tanpa menyimpan data.
- Build image dan smoke container di runner sudah ditunjukkan lewat log.
- Workflow publish GHCR tersedia. **Keberhasilan run publish dan digest belum dikonfirmasi dalam catatan percakapan ini.**
- Deployment staging/production, security gate lanjutan, dan operasional menjadi tahap berikutnya.

**Langkah berikutnya:** buka run `Publish verified image`, periksa keberhasilan push dan digest, lalu isi [catatan rilis](docs/release-record.md). Jika gagal, lanjutkan diagnosis pada tahap tersebut sebelum memilih target staging.

## Struktur materi dan proyek

```text
README.md                     Pintu masuk dan quick start
docs/
  roadmap.md                  Delapan level, praktik, exit criteria, capstone
  fondasi-dan-ci.md            Terminal, HTTP, Git, testing, CI
  container-dan-cd.md          Artifact, GHCR, staging, promosi, rollback
  advanced-dan-senior.md       Security, IaC, reliability, arsitektur tim
  git-reference.md            Fungsi dan contoh perintah Git
  troubleshooting.md          Kendala yang pernah ditemukan dan diagnosis
  progress.md                 Tracker bukti dan rencana belajar
  release-record.md           Template rilis yang sudah tersedia
  incident-report.md          Template insiden yang sudah tersedia
  archive/                    Salinan utuh catatan pembelajaran sebelumnya
app.py                        API Python dan SQLite
tests/test_api.py             Unit dan integration test
scripts/smoke.py              Readiness, versi, dan transaksi sintetis
.github/workflows/            CI dan publikasi image
Dockerfile                    Resep image
compose.yaml, k8s/, examples/  Bahan latihan opsional, bukan layanan aktif
```

## Batas latihan

Starter memakai `http.server`, SQLite, dan API tanpa autentikasi. Gunakan data sintetis dan lingkungan lab; pengembangan untuk production dibahas terpisah. Manifest Kubernetes memakai `emptyDir`, sehingga pergantian Pod dapat menghilangkan data. Workflow dan YAML tersedia tidak berarti target tersebut sudah dipasang atau aman untuk production.

Target staging remote belum dipilih/provision. Akun, akses, biaya, penyimpanan, dan pemulihan harus ditentukan sebelum deploy. Penggunaan runner/registry mengikuti ketentuan dan kuota akun; komputer lokal yang ringan tetap dapat dipakai untuk belajar.

Catatan lengkap sebelumnya dipertahankan di [arsip pembelajaran](docs/archive/learning-notes-2026-10-23.md). Modul aktif di atas menjadi urutan belajar utama; arsip berguna untuk menelusuri materi lama.
"# cicd-learning" 
