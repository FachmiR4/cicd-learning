# Materi Lanjutan: Security, Reliability, dan Praktik Senior

[Kembali ke README](../README.md) · [Roadmap](roadmap.md) · [Catatan rilis](release-record.md) · [Laporan insiden](incident-report.md)

Materi ini melanjutkan level 1–4. Prasyaratnya: Anda mampu membuat PR, membaca kegagalan CI, menjelaskan Dockerfile, dan membedakan build, publish, serta deployment. Sepuluh lab berikut melatih pengambilan keputusan, pembuktian kontrol, dan pemulihan layanan. Selesainya buku tidak otomatis membuat seseorang senior; kompetensi tersebut perlu dibuktikan berulang kali pada sistem dan tim dengan tanggung jawab nyata.

**Lingkungan belajar Anda tetap ringan.** Python, Git Bash, dan editor berjalan lokal. Container, pemindaian image, serta eksperimen Linux dilakukan pada runner GitHub atau remote lab yang sudah disediakan. Cloud, registry, environment, dan cluster yang belum dibuat tetap berstatus rencana. Jangan mencatat latihan desain sebagai deployment yang sudah berhasil. Untuk lab remote, tentukan pemilik, batas biaya, durasi, data sintetis, dan cara menghentikan resource terlebih dahulu.

| Level | Fokus | Lab | Bukti kemampuan |
|---|---|---|---|
| 5 — Advanced | Keamanan pipeline dan infrastructure as code | A1–A4 | Batas kepercayaan, identitas, artifact, dan perubahan infra dapat diaudit |
| 6 — Professional/Senior practice | Data, reliability, dan delivery | A5–A8 | Kegagalan terdeteksi dan pemulihan terbukti |
| 7 — Mastery berkelanjutan | Arsitektur, platform, dan kepemimpinan | A9–A10 | Keputusan dapat dijelaskan dan dioperasikan oleh orang lain |

## Batas aplikasi starter

Task API ini cocok sebagai alat belajar. API belum memiliki autentikasi/otorisasi pengguna; endpoint mutasi tidak boleh diperlakukan sebagai layanan publik siap produksi. Python `http.server` sendiri tidak direkomendasikan sebagai server produksi. Sebelum penggunaan nyata, pilih runtime/server yang sesuai, definisikan akses, TLS, batas request, audit, serta retensi data. [Dokumentasi Python](https://docs.python.org/3/library/http.server.html)

SQLite dapat berguna untuk aplikasi sederhana, tetapi banyak replika tidak otomatis memberi database bersama. Rencanakan siapa yang menulis, bagaimana locking bekerja, dan kapan database client-server diperlukan. Pada contoh Kubernetes yang memakai `emptyDir`, data mengikuti umur Pod dan hilang ketika Pod dihapus dari node; restart container dalam Pod yang sama berbeda dengan penggantian Pod. PVC pun bukan pengganti backup. [Dokumentasi volume Kubernetes](https://kubernetes.io/docs/concepts/storage/volumes/#emptydir)

## Level 5 — Melindungi jalur perubahan

### Lab A1 — Buat threat model untuk pipeline

**Tujuan:** mengetahui siapa dapat mengubah kode, artifact, dan deployment. Threat model adalah daftar aset, pihak yang berinteraksi, batas kepercayaan, ancaman, dan kontrol yang dapat diuji.

**Praktik:** gambarkan `kontributor → PR → runner → registry → environment`. Untuk setiap panah, tulis identitas, izin, data yang diterima, dan bukti pemeriksaannya. Mulai dari kasus konkret: PR mengubah workflow; judul PR mengandung karakter shell; dependency memperbarui kode; artifact dari run lain dipilih tanpa verifikasi.

Perlakukan kode PR sebagai input yang belum dipercaya. Hindari checkout dan eksekusi kode PR dalam job berprivilege `pull_request_target`. Judul dan isi PR juga data, sehingga jangan menyisipkannya langsung ke skrip shell. Pisahkan pengujian PR dari penerbitan/deployment berizin tulis. Pin action ke commit SHA lengkap yang sudah diverifikasi dari repository penerbit; siapkan pembaruan melalui PR yang meninjau upstream, perubahan, dan hasil pengujian. Pinning tanpa proses pembaruan meninggalkan versi lama selamanya. [Secure use GitHub Actions](https://docs.github.com/en/actions/reference/security/secure-use)

**Failure drill:** review sebuah rancangan workflow yang memberikan izin deploy pada semua PR. Tandai jalur penyalahgunaannya di diagram; jangan mengeksekusi serangan atau menggunakan credential asli.

**Bukti lulus:** lima ancaman memiliki kontrol, pemilik, dan metode pengujian; reviewer dapat menunjukkan mengapa PR tidak dapat menerbitkan image produksi.

### Lab A2 — Susun matriks izin dan desain OIDC

**Tujuan:** mengurangi dampak ketika satu job bermasalah.

| Job | Kebutuhan minimum dalam rancangan lab |
|---|---|
| Test PR | Membaca source, tanpa credential deployment |
| Publish tepercaya | Membaca source dan menulis package tujuan |
| Deploy staging | Mengubah layanan staging tertentu |
| Deploy produksi | Identitas produksi terpisah dan aturan persetujuan yang disepakati |

**Praktik:** buat tabel identitas untuk tiap job di workflow Anda. Batasi `permissions` pada job yang memerlukan kemampuan tambahan. Gunakan `GITHUB_TOKEN` untuk kasus GHCR yang memang didukung; tidak perlu membuat cloud credential hanya untuk meniru contoh.

OIDC memungkinkan provider menukar identitas workflow dengan credential berumur pendek. Izin `id-token: write` hanya memungkinkan job meminta token OIDC, bukan otomatis memberi akses cloud. Provider masih harus memvalidasi issuer, audience, subject/claim yang relevan, repository, serta branch atau environment yang diizinkan. Kebijakan yang menerima semua repository tetap berbahaya walaupun memakai OIDC. [GitHub OIDC](https://docs.github.com/en/actions/concepts/security/openid-connect)

**Failure drill:** buat dua skenario di tabel: repository benar tetapi branch salah; repository dan environment benar tetapi role meminta resource di luar staging. Nyatakan keputusan yang diharapkan: ditolak. Verifikasi nyata dilakukan hanya setelah remote lab disediakan.

**Bukti lulus:** setiap izin mempunyai alasan; hasil desain dipisahkan dari log pengujian autentikasi nyata; tidak ada token dalam README, screenshot, atau artifact.

### Lab A3 — Bedakan scan, SBOM, signature, dan provenance

Keempatnya menjawab pertanyaan berbeda:

| Kontrol | Pertanyaan yang dijawab | Keterbatasan |
|---|---|---|
| Vulnerability scan | Kerentanan dikenal apa yang ditemukan? | Bergantung pada database scanner dan cakupan |
| SBOM | Komponen apa yang terkandung dalam artifact? | Daftar komponen bukan bukti bebas kerentanan |
| Signature | Apakah konten terkait identitas penandatangan yang diterima? | Penandatangan tepercaya masih dapat membangun kode cacat |
| Provenance | Dari input dan proses mana artifact dihasilkan? | Perlu verifikasi terhadap kebijakan build yang dipercaya |

SLSA menjelaskan tingkat jaminan provenance dan perlindungan proses build. Jangan mengklaim tingkat SLSA hanya karena satu file provenance tersedia. [SLSA build track](https://slsa.dev/spec/v1.2/build-track-basics)

**Praktik:** di branch lab, rancang job runner untuk memindai image hasil build, menghasilkan SBOM, lalu menyimpan digest dan laporan. Pilih versi tool dari penerbit resmi dan tinjau pembaruannya. Evaluasi temuan berdasarkan severity, kemungkinan eksploitasi, exposure, perbaikan yang tersedia, serta pengecualian dengan pemilik dan tanggal kedaluwarsa. Tetapkan aturan tim; tidak ada ambang universal untuk semua aplikasi.

Untuk signing, verifikasi digest sekaligus issuer dan identitas signer yang diharapkan; keberhasilan pemeriksaan kriptografi saja belum cukup. [Verifikasi Sigstore](https://docs.sigstore.dev/cosign/verifying/verify/)

**Failure drill:** verifier menerima digest lain atau signer salah. Hasil yang diperlukan adalah penolakan. **Bukti lulus:** [catatan rilis](release-record.md) menghubungkan commit, run, digest, laporan, pengecualian, dan hasil verifikasi; image yang diperiksa adalah image yang dipromosikan.

### Lab A4 — Review infrastructure as code sebelum apply

Infrastructure as code menjadikan konfigurasi dapat ditinjau. State menghubungkan konfigurasi dengan resource nyata; drift adalah perbedaan aktual dari keadaan yang dimaksud. Mengubah konfigurasi, memperbarui state, dan mengubah resource bukan tindakan yang sama.

**Praktik tanpa cloud:** buat rancangan tiga resource: aplikasi, penyimpanan, dan identitas. Untuk setiap perubahan, catat apakah penambahan, update, replacement, atau deletion; jelaskan dampak ke alamat layanan dan data. Bandingkan dua contoh plan tertulis, salah satunya mengganti database. Pilih mana yang perlu revisi.

Dalam lab remote, jalur kerja menjadi `format → validate → plan → review → apply plan yang disetujui → verifikasi`. `terraform plan` memprediksi perubahan; menjalankannya sendiri belum menerapkan resource. Jika konfigurasi atau keadaan berubah setelah review, buat plan baru. [Terraform plan](https://developer.hashicorp.com/terraform/cli/commands/plan)

State dan saved plan dapat memuat data sensitif. Menandai nilai sebagai `sensitive` tidak berarti nilai itu otomatis hilang dari state; gunakan backend dengan kontrol akses, enkripsi, versioning, dan mekanisme locking yang sesuai. [Terraform sensitive data](https://developer.hashicorp.com/terraform/language/manage-sensitive-data)

**Failure drill:** terdapat drift akibat perubahan manual, lalu dua operator ingin apply bersamaan. Jelaskan cara mendeteksi, menyelesaikan kepemilikan perubahan, dan mencegah penimpaan. **Bukti lulus:** reviewer memahami biaya, deletion/replacement, recovery state, dan pemilik persetujuan; tidak ada apply otomatis dari PR tidak tepercaya.

## Level 6 — Membuktikan layanan dapat dipulihkan

### Lab A5 — Migrasi database dan uji restore

Rollback image tidak membatalkan perubahan database. Migrasi destruktif dapat membuat aplikasi lama tidak lagi bisa membaca data.

Gunakan pola **expand → migrate → contract**. Contoh: ingin mengganti `title` menjadi `name`. Tambahkan kolom baru tanpa menghapus yang lama; jalankan kode kompatibel selama transisi; isi data lama dalam batch yang dapat diulang; verifikasi kesesuaian; pindahkan pembacaan; hapus kolom lama hanya setelah semua pembaca lama berhenti dan jendela rollback ditutup. Uji kombinasi versi aplikasi lama/baru dengan schema yang didukung. Penulisan ganda perlu konsistensi dan pemulihan parsial.

**Praktik lokal:** gunakan database fixture tersendiri, bukan file data belajar aktif. Buat tiga task, backup, tambahkan satu task setelah backup, lalu pulihkan backup ke file baru. Bandingkan row dan jalankan `PRAGMA integrity_check`. Gunakan SQLite backup API melalui Python `sqlite3.Connection.backup()`; menyalin sembarang file database aktif dapat menghasilkan salinan tidak konsisten. [SQLite Backup API](https://www.sqlite.org/backup.html)

**RPO** adalah target kehilangan data maksimum yang dapat diterima; **RTO** adalah target lama pemulihan layanan. Untuk latihan, contoh target RPO 15 menit dan RTO 30 menit boleh digunakan jika jelas berlabel contoh. Ukur waktu nyata serta transaksi yang tidak terpulihkan, bukan hanya menulis target.

**Failure drill:** migrasi berhenti di tengah dan diulang. **Bukti lulus:** tidak terjadi duplikasi, restore tervalidasi melalui API, kehilangan data terukur, dan keterbatasan rollback tercatat.

### Lab A6 — Rancang SLI, SLO, dan error budget

**SLI** adalah ukuran perilaku layanan yang dialami pengguna; **SLO** adalah targetnya pada jendela tertentu. CPU merupakan sinyal diagnosis, tetapi belum langsung menjawab apakah pengguna bisa menyimpan task.

**Praktik:** definisikan request yang masuk denominator, request yang dinilai baik, titik pengukuran, dan jendela evaluasi. Misalnya, request valid ke endpoint task berhasil tanpa 5xx; kesalahan input yang memang ditolak jangan otomatis dihitung sebagai kegagalan layanan. Sertakan latency agar respons yang sangat lambat tidak dianggap sehat hanya karena statusnya 200.

Contoh hitungan: dari 100.000 request yang memenuhi definisi, target keberhasilan 99,9% memberi jatah 100 request gagal. Jika 40 gagal, 40% budget terpakai. Ini ilustrasi matematika, bukan target wajib proyek Anda. Kebijakan error budget menghubungkan hasil pengukuran dengan keputusan rilis dan pekerjaan reliability. [Contoh kebijakan Google SRE](https://sre.google/workbook/error-budget-policy/)

**Failure drill:** log menunjukkan HTTP 200, tetapi aplikasi gagal menyimpan data. Tambahkan pemeriksaan perilaku atau indikator transaksi yang mendeteksi masalah tersebut. Tentukan siapa menerima alert, kapan bertindak, dan tautan runbook; alert tanpa tindakan yang jelas hanya menambah kebisingan.

**Bukti lulus:** dashboard/laporan data sintetis, rumus yang dapat dihitung ulang, contoh pelanggaran, serta keputusan apakah rilis dilanjutkan, ditahan, atau dipulihkan.

### Lab A7 — Optimasi pipeline berdasarkan pengukuran

Pisahkan waktu antre runner, checkout, pengunduhan dependency, test, build, scan, dan deploy. Menghemat dua detik lint tidak membantu bila antrean runner berlangsung sepuluh menit. Catat beberapa run untuk membandingkan variasi dan distribusi waktu; jangan mengambil keputusan dari satu run tercepat.

**Praktik:** buat tabel baseline minimal lima run yang tersedia. Pilih satu eksperimen: matrix test paralel, cakupan path yang benar, atau cache dependency saat dependency memang ada. Aplikasi stdlib ini tidak membutuhkan cache `pip` kosong hanya agar terlihat canggih.

Cache mempercepat pekerjaan yang dapat dibuat ulang; artifact menyimpan hasil job seperti laporan atau paket. Kegagalan cache harus tetap menghasilkan build yang benar. Jangan menyimpan secret di cache, dan perlakukan konten hasil restore sesuai batas kepercayaannya. [GitHub cache versus artifact](https://docs.github.com/en/actions/concepts/workflows-and-actions/dependency-caching)

**Failure drill:** hapus penggunaan cache pada branch eksperimen lalu bandingkan hasil fungsional; simulasikan dua permintaan deployment environment yang sama. Tentukan urutan/lock deployment. Pembatalan run lama cocok untuk beberapa pemeriksaan PR, tetapi membatalkan migrasi atau deploy aktif sembarangan dapat meninggalkan keadaan parsial.

**Bukti lulus:** perbandingan sebelum/sesudah, jumlah runner-minute, serta bukti test dan artifact tetap benar. Retry dibatasi untuk kegagalan sementara; test deterministik yang gagal tidak disembunyikan dengan retry tak terbatas.

### Lab A8 — Progressive delivery dan GitOps sebagai pilihan

**Rolling update** mengganti instance bertahap; **blue-green** menyiapkan dua versi kemudian memindahkan routing; **canary** mengekspos versi baru ke sebagian traffic. Pilihan bergantung pada kapasitas, mekanisme routing, observability, dan kompatibilitas data. Menjalankan dua container saja belum berarti canary jika tidak ada traffic yang diarahkan serta dibandingkan.

**Praktik desain:** buat tabel tahap canary, misalnya 5% → 25% → 100%, lengkap dengan jumlah observasi minimum, waktu tunggu, indikator error/latency, keputusan abort, dan pemilik. Persentase ini contoh; traffic kecil mungkin membutuhkan durasi lebih panjang. Sertakan versi schema dan jalur rollback. Menyalurkan traffic kembali tidak mengembalikan data yang sudah berubah.

GitOps memakai deklarasi desired state berversi yang ditarik agen dan direkonsiliasi terus-menerus. CI menerbitkan artifact; perubahan digest masuk melalui PR konfigurasi; reconciler menyamakan lingkungan dengan deklarasi tersebut. [Prinsip OpenGitOps](https://opengitops.dev/)

**Failure drill:** state aktual berbeda dari Git, kemudian operator melakukan hotfix manual. Tentukan apakah perubahan diadopsi ke Git atau dikembalikan, termasuk catatan insidennya. Eksperimen Kubernetes hanya pada remote lab yang disediakan; Kubernetes bukan prasyarat lulus CI/CD. Untuk Task API, selesaikan desain penyimpanan sebelum menambah replika.

**Bukti lulus:** rancangan routing/data, contoh keputusan abort berbasis bukti, identitas digest, dan batas jelas antara simulasi dokumen dengan rollout yang pernah dijalankan.

## Level 7 — Arsitektur dan kepemimpinan teknis

### Lab A9 — Bangun kontrak platform yang dapat digunakan tim

Engineer senior membantu tim lain bekerja aman dengan sedikit ketergantungan pada dirinya. Platform yang baik menyediakan jalur standar, dokumentasi, pesan error berguna, dan jalur pengecualian yang terlihat.

**Praktik:** rancang reusable workflow dengan input eksplisit, output digest, permission minimum, timeout, dan kode kegagalan yang terdokumentasi. Buat contoh pemanggil untuk dua aplikasi. Bedakan perubahan kompatibel, perubahan perilaku, dan breaking change. Pin versi yang dipercaya, berikan changelog dan masa migrasi, lalu uji pembaruan pada pengguna percobaan sebelum semua repository.

Tulis **ADR (Architecture Decision Record)** tentang memilih runner GitHub dibanding Docker lokal untuk pembelajaran: konteks perangkat, kebutuhan, opsi, keputusan, konsekuensi, biaya, dan kondisi peninjauan ulang. Buat ADR kedua untuk SQLite versus database terpusat. Keputusan terbaik mengikuti kebutuhan, bukan jumlah alat yang dipakai.

**Failure drill:** versi pipeline baru merusak satu pemanggil. Pulihkan referensi workflow pemanggil, simpan bukti kegagalan, dan perbaiki tanpa memaksa seluruh tim menerima breaking change. Minta teman mengikuti dokumentasi tanpa penjelasan lisan.

**Bukti lulus:** dua pemanggil memenuhi kontrak, rollback versi pipeline jelas, satu orang lain bisa menjelaskan alur, serta terdapat pemilik dukungan dan prosedur pengecualian. Otonomi tim tidak berarti tidak ada batas keamanan.

### Lab A10 — Pimpin simulasi insiden dan evaluasi hasil delivery

**Praktik:** gunakan skenario data sintetis: deployment terakhir menyebabkan `/ready` gagal setelah migrasi. Bagikan peran incident commander, investigator, communicator, dan pencatat. Jika belajar sendiri, tulis keputusan tiap peran secara terpisah. Catat waktu deteksi, hipotesis, tindakan, pemulihan, dan verifikasi pengguna; jangan langsung menganggap commit terakhir pasti penyebab.

Utamakan pemulihan berdasarkan bukti. Bandingkan rollback aplikasi, perubahan konfigurasi, dan roll-forward schema. Tulis [laporan insiden](incident-report.md) tanpa menyalahkan orang, dengan faktor penyebab, celah deteksi, serta tindakan yang memiliki pemilik dan tenggat. Jalankan ulang drill untuk membuktikan tindak lanjut efektif.

DORA saat ini menggunakan lima ukuran: change lead time, deployment frequency, failed deployment recovery time, change fail rate, dan deployment rework rate. Ukur pada layanan/tim dengan definisi konsisten. Angka dipakai memperbaiki sistem kerja, bukan menilai individu melalui jumlah commit. [Panduan metrik DORA](https://dora.dev/guides/dora-metrics/)

**Failure drill:** rollback image berhasil tetapi pengguna tetap gagal karena schema. Tunjukkan bagaimana komunikasi insiden diperbarui tanpa menyatakan pulih terlalu dini. **Bukti lulus:** timeline, keputusan beserta alasannya, hasil restore/roll-forward, dan rekomendasi perbaikan yang lebih spesifik daripada “lebih teliti”.

## Capstone senior: satu rilis yang dapat dipertanggungjawabkan

Pilih perubahan nyata, misalnya penambahan atribut task dengan migrasi kompatibel. Hasil akhirnya mencakup threat model, ADR, PR, CI, digest image, laporan keamanan, rencana rilis, pengujian pemulihan, dan handover. Pakai [catatan rilis](release-record.md) sebagai pengikat bukti. Target remote baru dijalankan setelah tersedia; tanpa itu, labeli capstone sebagai simulasi, dengan deployment/recovery remote masih belum terbukti.

| Aspek | Bobot contoh | Bukti yang dinilai |
|---|---:|---|
| Kebenaran aplikasi dan test | 20 | Jalur normal, invalid input, kompatibilitas, dan failure test |
| Identitas dan supply chain | 20 | Batas PR, minimum permission, digest dan verifikasi asal |
| Data dan pemulihan | 20 | Migrasi kompatibel, restore nyata, hasil ukur RPO/RTO |
| Reliability dan delivery | 20 | SLI/SLO terdefinisi, rollout/abort, diagnosis dari telemetry |
| Keputusan dan kolaborasi | 20 | ADR, review, runbook, handover, pembelajaran insiden |

Gunakan 80/100 sebagai contoh target internal belajar, bukan sertifikasi profesional. Nilai tinggi tidak menggantikan **gate wajib**: tidak ada credential bocor; artifact yang dipromosikan dapat ditelusuri; pemeriksaan penting tidak diabaikan; pemulihan data telah diuji pada lingkungan yang diklaim; langkah destruktif dan biaya diketahui; orang lain dapat menjalankan prosedur; klaim keberhasilan didukung bukti.

Mastery berarti mampu memilih kompleksitas yang diperlukan, menguji asumsi, memperbaiki keputusan saat bukti berubah, dan meningkatkan kemampuan tim. Ulangi proyek dengan kebutuhan berbeda sebelum menganggap pola pertama berlaku universal. Tandai perkembangan nyata pada [roadmap](roadmap.md); level jabatan di perusahaan tetap ditentukan cakupan tanggung jawab dan penilaian organisasi.
