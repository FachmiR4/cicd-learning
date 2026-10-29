# Roadmap CI/CD: beginner sampai praktik senior

[README](../README.md) · [Fondasi dan CI](fondasi-dan-ci.md) · [Container dan CD](container-dan-cd.md) · [Advanced dan senior](advanced-dan-senior.md) · [Tracker](progress.md)

## Cara membaca roadmap

Roadmap ini berangkat dari satu Task API, lalu memperluas tanggung jawab: membuat perubahan benar, mendistribusikan artifact, merilis dengan aman, sampai membantu tim mengoperasikan sistem. Tidak perlu mengganti bahasa atau alat setiap naik level.

**Prinsip belajar:** pahami konsep → praktikkan → sengaja buat satu kegagalan pada lab → diagnosis → pulihkan → simpan bukti. Jangan melompat hanya karena contoh dapat disalin.

Perkiraan **36 minggu × 6–8 jam** adalah rancangan sesi sampai capstone awal bagi pembelajar yang membutuhkan fondasi, bukan jaminan jabatan senior. Waktu tambahan diperlukan untuk pengalaman tim, sistem yang lebih besar, review, dan operasi nyata. Pengalaman yang sudah terbukti boleh diperhitungkan; jangan mengulang dari nol tanpa kebutuhan.

### Pembagian lingkungan

| Tempat | Kegiatan |
|---|---|
| Komputer Windows + Git Bash | Edit, Python, unit/integration test, Git, membaca hasil |
| GitHub-hosted runner | Docker build/run, smoke container, registry, pemeriksaan otomatis |
| Lingkungan staging remote yang nanti dipilih | Deployment, konfigurasi, data, pemulihan, observasi |
| Repository/cluster lab terpisah | Eksperimen destruktif terbatas, IaC, GitOps opsional |

Tidak ada kewajiban Docker Desktop atau WSL lokal. Jangan menjalankan tugas hosting permanen di runner CI.

## Peta delapan level

| Level | Perkiraan sesi | Pertanyaan yang mampu dijawab | Bukti utama |
|---|---|---|---|
| 0 Fondasi | Minggu 1–2 | Bagaimana aplikasi menerima request? | API lokal, port, log, smoke |
| 1 Beginner | Minggu 3–5 | Bagaimana menjaga perubahan dan mendeteksi bug? | Git, PR, test positif/negatif |
| 2 Intermediate CI | Minggu 6–8 | Bagaimana pemeriksaan berjalan otomatis? | Workflow, matrix, quality gate |
| 3 Artifact | Minggu 9–11 | Artifact mana yang dibangun dan diuji? | Image, registry, commit, digest |
| 4 Applied CD | Minggu 12–16 | Bagaimana versi tersebut dipasang dan dipulihkan? | Staging, promosi, rollback |
| 5 Advanced | Minggu 17–22 | Siapa yang boleh mengubah atau merilis apa? | Threat model, security gate, IaC |
| 6 Senior practice | Minggu 23–30 | Bagaimana layanan dan proses tim tetap andal? | SLO, data, runbook, platform |
| 7 Mastery | Minggu 31–36 dan berkelanjutan | Mengapa desain ini tepat dan bisa dioperasikan tim? | ADR, capstone, mentoring, tradeoff |

## Level 0 — Fondasi perangkat dan aplikasi

**Prasyarat:** dapat mengelola file. Mulai dengan Git Bash, Python launcher `py`, dan editor; belum perlu memahami Docker.

**Materi:** path absolut/relatif, working directory, exit code, stdout/stderr, environment variable, process/port, HTTP method/status, JSON, database sederhana. Bedakan `health` dengan readiness dan transaksi bisnis.

**Praktik:**

1. Masuk ke root proyek; temukan `app.py`, `tests`, dan `scripts`.
2. Jalankan API pada 8081 dengan `APP_VERSION=dev`.
3. Kirim smoke dari terminal lain dan jelaskan proses yang melayani request.
4. Akses port yang salah dan endpoint yang tidak ada; bedakan kegagalan koneksi dengan HTTP 404.

**Exit criteria:** dapat menjalankan/menghentikan server, mengenali file yang benar, dan menjelaskan alasan satu request gagal. Bukti: log smoke dan catatan diagnosis. Baca [modul fondasi](fondasi-dan-ci.md).

## Level 1 — Git dan testing untuk beginner

**Prasyarat:** Level 0 atau bukti setara.

**Materi:** working tree/index/commit/remote, branch pendek, review, assertion, unit/integration test, isolasi database. Perhatikan bahwa HTTP error dapat menjadi ekspektasi test negatif.

**Praktik:**

1. Ubah batas 120 menjadi 119 di branch eksperimen, amati test gagal, lalu pulihkan.
2. Tambahkan test Unicode, round trip API, dan penolakan judul panjang.
3. Stage file tertentu, review diff, commit, push, buat PR, review, merge.
4. Coba `restore --staged` untuk memahami bahwa unstage tidak menghapus edit.

**Exit criteria:** dapat mengulang alur PR, menjelaskan assertion penting, dan memulihkan eksperimen tanpa force push atau reset hard. Bukti: PR, test log, penjelasan failure. Lihat [referensi Git](git-reference.md).

## Level 2 — CI yang dapat dipercaya

**Materi:** trigger, runner, job, step, matrix, dependency `needs`, timeout, permission, status check, lint versus syntax check. Bedakan masalah aplikasi, runner, konfigurasi, dan jaringan.

**Praktik:**

1. Baca workflow CI yang sudah ada dan cocokkan setiap job dengan log.
2. Uji salah sintaks, salah perilaku, dan salah versi pada PR yang berbeda/commit terpisah.
3. Periksa bahwa container job tidak dilanjutkan ketika test wajib gagal.
4. Tambahkan lint sederhana dengan versi tool yang ditinjau; evaluasi rule yang benar-benar berguna.
5. Atur required checks bila didukung akun/repository; buktikan jalur merge biasa mengikuti aturan.

**Exit criteria:** kegagalan wajib benar-benar menghentikan integrasi pada jalur yang ditetapkan. `continue-on-error`, retry, dan skip tidak menyembunyikan bug. Bukti: run gagal, run perbaikan, rule yang diterapkan.

**Checkpoint konsep:** `CI hijau` hanya berarti pemeriksaan yang dijalankan berhasil, bukan seluruh perilaku aplikasi dijamin benar.

## Level 3 — Artifact, container, dan registry

**Materi:** image versus container, Dockerfile/build context, user non-root, tag versus digest, dependency pinning, artifact versus cache, identitas commit. Docker hanya berjalan di runner.

**Praktik:**

1. Jelaskan `FROM`, `RUN`, `COPY`, `USER`, `CMD` dari file proyek.
2. Amati build→run→smoke pada GitHub dan cari versi commit yang diuji.
3. Aktifkan/review workflow publish yang sudah tersedia; tunggu run main.
4. Catat digest asli dari `Capture digest`, bukan placeholder.
5. Latih pull berdasarkan digest di runner terpisah dengan autentikasi sesuai akses package, kemudian smoke terhadap image yang ditarik.

**Exit criteria:** reviewer dapat melacak commit→run→image digest. Jangan build ulang lalu menyebutnya image registry yang sama. Bukti: catatan rilis dan hasil pull verification.

**Posisi pengguna saat penyusunan:** build dan smoke pernah terbukti; publish GHCR perlu konfirmasi. Baca [modul container dan CD](container-dan-cd.md).

## Level 4 — Continuous Delivery dan pemulihan

**Prasyarat:** artifact registry teridentifikasi, ada target staging lab yang disepakati dengan akses/anggaran jelas. Memilih target bukan alasan memasang banyak tool sekaligus.

**Materi:** pemisahan environment/config/secret, autentikasi, readiness, smoke, idempotensi proses, locking/concurrency, promosi, approval, rollback, rollout versus release.

**Praktik:**

1. Tulis deployment contract: input digest, config, target, health checks, output catatan rilis.
2. Siapkan staging remote dan pasang artifact yang dipilih tanpa build ulang.
3. Verifikasi versi dan operasi sintetis. Simpan data hanya di storage yang memang dirancang bertahan.
4. Latih fault readiness, salah versi, dan gagal mengakses dependency satu per satu.
5. Pulihkan versi/kondisi sehat dan verifikasi data. Rilis yang gagal tetap dicatat gagal meskipun rollback berhasil.

**Exit criteria:** dapat mendemonstrasikan sukses, gagal tetapi pulih, dan gagal yang perlu tindakan manual; tidak menganggap ketiganya sama. Bukti: digest sebelum/sesudah, smoke, waktu pulih, batas kompatibilitas data.

## Level 5 — Security, supply chain, dan IaC

**Materi:** trust boundary PR, minimum privilege, OIDC trust, supply chain, SBOM, scan, signature/provenance, pinning dan update, state IaC, plan/apply, drift, separation of duties.

**Praktik:**

1. Gambar siapa yang dapat menjalankan kode dengan credential apa.
2. Pastikan PR tidak tepercaya tidak memperoleh akses publish/deploy.
3. Tambahkan scan sebelum push; catat pengecualian beserta pemilik dan tanggal kedaluwarsa.
4. Buat SBOM, lalu bedakan bukti identitas signer, asal artifact, dan kerentanan.
5. Jika target mendukung OIDC, uji trust positif dan negatif pada lab; token issuance bukan izin resource otomatis.
6. Buat infrastruktur lab kecil dengan IaC, review plan, lindungi state, dan uji drift serta teardown terbatas.

**Exit criteria:** kandidat tidak sah ditolak, perubahan infra dapat dinilai sebelum apply, dan bukti dapat diaudit. Tidak perlu mengklaim level compliance/SLSA tanpa memenuhi semua syaratnya. Baca [modul advanced](advanced-dan-senior.md).

## Level 6 — Praktik senior: reliability, data, dan tim

**Materi:** SLI/SLO/error budget, indikator delivery, latency/error per versi, rollout aman, schema compatibility, RPO/RTO, recovery data, runbook, incident learning, reusable workflow, developer experience, costs.

**Praktik:**

1. Ukur transaksi pengguna dan tetapkan target dalam jendela waktu yang bermakna.
2. Latih rilis yang menghasilkan error walaupun prosesnya hidup; deteksi dari data layanan.
3. Jalankan expand–migrate–contract, test writer lama/baru dan jendela rollback.
4. Uji restore backup ke lingkungan terpisah; ukur kehilangan data dan lama pemulihan.
5. Buat template pipeline berversi yang digunakan dua repo contoh; uji migrasi konsumen.
6. Ukur bottleneck CI dan optimalkan satu variabel tanpa menghapus test wajib.
7. Jika kebutuhan membenarkan, latih GitOps atau progressive delivery dengan routing dan pengukuran yang sesuai.

**Exit criteria:** orang lain dapat mengikuti runbook, tradeoff diterangkan, kesalahan ditemukan tanpa menyalahkan individu, dan perbaikan memiliki pemilik. Bukti: incident drill, metrics, compatibility matrix, review template.

## Level 7 — Mastery yang berkelanjutan

**Materi:** desain berdasarkan kebutuhan, system boundaries, reliability versus cost, prioritas risiko, standar pengecualian, platform adoption, review arsitektur, komunikasi, mentoring, rencana migrasi dan dekomisioning.

**Praktik:**

1. Tulis ADR membandingkan dua desain: misalnya VM/container sederhana dengan cluster, atau deployment langsung dengan GitOps.
2. Uraikan kebutuhan, beban operasional, kegagalan, biaya relatif, serta alasan menunda kompleksitas tertentu.
3. Minta reviewer lain menguji keputusan dan mereproduksi proyek tanpa pendampingan langkah demi langkah.
4. Ajarkan satu materi pada rekan, gunakan umpan balik untuk memperbaiki dokumen.
5. Evaluasi dampak perubahan proses setelah beberapa rilis/insiden, bukan hanya dari demo tunggal.

**Exit criteria:** keputusan masuk akal dalam konteks, hasil dapat diverifikasi, dan tim mampu mengoperasikan sistem tanpa satu orang menjadi titik kegagalan. Level ini terus berkembang; bukan klaim “master” setelah menyelesaikan buku.

## Jadwal belajar yang dapat disesuaikan

| Sesi mingguan | Aktivitas |
|---|---|
| 1: 60–90 menit | Baca satu konsep, gambar alurnya, prediksi hasil |
| 2: 90–120 menit | Praktik satu perubahan dengan bukti |
| 3: 90–120 menit | Failure drill, diagnosis, pemulihan |
| 4: 60–90 menit | Review, dokumentasi, PR, refleksi |

Gunakan [progress.md](progress.md) untuk mencatat bukti. Selesaikan satu masalah sebelum menambah tool baru. Jika perangkat terbatas, pertahankan latihan Python lokal dan pindahkan tugas container/infra ke runner atau target lab yang telah disiapkan.

## Capstone: dari perubahan sampai operasi

Bangun fitur baru pada Task API (misalnya status task dan perubahan kontrak API) dengan test, PR, CI, artifact registry, staging, strategi promosi, serta pemulihan. Database dan server aplikasi perlu disesuaikan sebelum skenario production nyata; environment simulasi boleh dipakai dan harus diberi label.

### Hasil yang diserahkan

1. README/diagram dan cara reproduksi yang benar untuk lingkungan pembelajar.
2. Test perilaku penting dan bukti CI menolak perubahan salah.
3. Artifact teridentifikasi commit/digest serta hasil verifikasi registry.
4. Kontrak deployment, catatan rilis staging, dan promosi artifact yang sama.
5. Threat model, hak akses, scan/SBOM, dan kebijakan pengecualian.
6. Compatibility matrix schema/aplikasi dan bukti backup restore.
7. Sinyal layanan, runbook, timeline incident drill dan perbaikannya.
8. ADR berisi alternatif, batas, biaya operasional, dan keputusan.

### Rubrik

| Aspek | Bobot |
|---|---:|
| Kebenaran aplikasi dan kekuatan test | 20 |
| Keterlacakan artifact dan CI | 15 |
| Deployment, promosi, dan rollback | 20 |
| Security dan kontrol perubahan | 15 |
| Operasi, data, dan pemulihan | 20 |
| Dokumentasi, keputusan, dan transfer pengetahuan | 10 |

Target pembelajaran: **80/100**, dengan syarat wajib tidak ada secret bocor, gate wajib tidak dilewati, dan pemulihan dibuktikan. Skor tidak menggantikan penilaian profesional di tempat kerja. Jika target remote belum tersedia, tandai bagian CD belum teruji; jangan mengklaim lulus penuh dari simulasi YAML saja.

## Bacaan dan batas informasi

Mulai dari modul dalam repository; sumber resmi terkait ditautkan di masing-masing bab. Gunakan [GitHub Actions](https://docs.github.com/en/actions), [Docker CI](https://docs.docker.com/build/ci/github-actions/), [SLSA](https://slsa.dev/), [DORA](https://dora.dev/guides/dora-metrics/), dan [Google SRE](https://sre.google/books/) untuk pendalaman. Periksa versi, dukungan akun, dan kondisi target ketika benar-benar menjalankan integrasi baru.
