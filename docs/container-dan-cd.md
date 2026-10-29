# Container, registry, dan dasar delivery

[Beranda](../README.md) · [Roadmap](roadmap.md) · [Referensi Git](git-reference.md) · [Kembali: fondasi dan CI](fondasi-dan-ci.md)

Materi ini mencakup level 3–4. Seluruh pekerjaan Docker dilakukan pada **runner GitHub Actions**, karena komputer belajar tidak menjalankan Docker/WSL. Blok yang diberi label **runner** dibaca sebagai bagian workflow, bukan disalin ke Git Bash lokal.

Sumber proyek sudah memiliki `Dockerfile`, `ci.yml`, dan `publish.yml`. Keberadaan workflow publish tidak sama dengan bukti bahwa image berhasil diterbitkan: periksa run dan digest. Target staging/production belum ditentukan, sehingga bagian deployment di sini adalah rancangan dan latihan terukur, bukan klaim adanya server aktif.

## 1. Dari kode menjadi artifact

Image adalah paket aplikasi dan runtime; container adalah proses yang menjalankan image. Registry menyimpan image. Artifact adalah hasil build yang dapat disimpan dan digunakan kembali, misalnya image atau paket aplikasi.

```text
Kode pada commit tertentu
  → test
  → build image sekali
  → uji image tersebut
  → push ke registry
  → catat digest
  → gunakan digest yang sama untuk staging dan production
```

Membangun ulang dari commit sama belum tentu menghasilkan isi identik jika image dasar atau dependency berubah. Karena itu, latihan delivery berfokus pada memindahkan artifact yang telah diuji, bukan membuat build baru tanpa verifikasi pada setiap lingkungan.

| Identitas | Contoh | Kegunaan |
|---|---|---|
| Commit | `45d6e355...` | Menemukan versi kode |
| Tag image | `ghcr.io/fachmir4/cicd-practice:<commit>` | Nama yang mudah ditelusuri |
| Digest | `ghcr.io/fachmir4/cicd-practice@sha256:...` | Memilih konten image secara tepat |
| Versi aplikasi | Respons `/version` | Membuktikan versi yang merespons request |

Tag dapat diarahkan ulang; gunakan digest ketika membutuhkan pilihan artifact yang pasti. Digest bukan bukti image aman: Anda tetap memerlukan asal build, test, dan pengendalian akses.

## 2. Lab 7 — membaca Dockerfile

**Lokal, Git Bash:**

```bash
cd ~/Videos/cicd/cicd-practice
cat Dockerfile
```

File proyek saat materi disusun:

```dockerfile
FROM python:3.12-slim
ARG APP_VERSION=dev
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 PORT=8080 DB_PATH=/data/tasks.db APP_VERSION=${APP_VERSION}
WORKDIR /app
RUN mkdir /data && chown 10001:10001 /data
COPY app.py /app/app.py
USER 10001:10001
EXPOSE 8080
CMD ["python", "app.py"]
```

`FROM` memilih dasar, `WORKDIR` memilih folder, `RUN` melakukan pekerjaan saat build, dan `COPY` memasukkan file. `CMD` menentukan perintah saat container dijalankan. `USER` memilih identitas proses. `EXPOSE` mendokumentasikan port; publikasi port tetap membutuhkan konfigurasi runtime. `ARG` menerima parameter build, sedangkan `ENV` menyimpan nilai lingkungan pada image. [Referensi Dockerfile](https://docs.docker.com/reference/dockerfile/)

Pada proyek ini, `/data` dapat ditulis UID 10001. `HOST=0.0.0.0` membuat aplikasi mendengarkan antarmuka container; binding host di workflow tetap dibatasi ke loopback runner. `APP_VERSION` dari build disediakan kepada aplikasi saat run. Jangan memakai mekanisme ini untuk membakar password ke image.

**Latihan:** tandai mana yang terjadi saat build dan mana yang memengaruhi run. Jelaskan mengapa mengedit `app.py` lokal tidak mengubah container yang sudah dibuat. Periksa pula `.dockerignore`: file credential, database lokal, dan `.git` tidak semestinya menjadi bagian build context yang tidak diperlukan.

## 3. Lab 8 — mencocokkan log runner

**Hanya pada runner, sudah menjadi bagian `ci.yml`:**

```bash
docker build --build-arg APP_VERSION="$GITHUB_SHA" -t cicd-practice:ci .
docker run -d --name cicd-smoke -p 127.0.0.1:8080:8080 cicd-practice:ci
python scripts/smoke.py http://127.0.0.1:8080 --expect-version "$GITHUB_SHA"
```

`$GITHUB_SHA` berasal dari konteks workflow. Ia tidak otomatis tersedia di Git Bash lokal. Port 8080 dalam contoh berada pada runner dan tidak berbenturan dengan aplikasi komputer Anda di 8081.

Buka Actions → CI Practice → run → container. Pada Build container, cari `WORKDIR`, `RUN`, `COPY`, dan `exporting to image`. `CACHED` berarti hasil langkah dapat digunakan ulang. Nama `docker.io/library/cicd-practice:ci` pada log build tidak membuktikan upload; upload membutuhkan langkah push.

Pada Smoke test, cari `SMOKE OK` dan versi yang diharapkan. Pada Container log, cari readiness atau exception jika gagal. Retry readiness membantu startup yang lambat, tetapi batas retry harus tetap ada agar kegagalan nyata tidak ditutupi.

**Bukti selesai:** simpan tautan run, nama image, versi aplikasi, dan hasil smoke. Jelaskan perbedaan “build berhasil” dengan “aplikasi benar-benar berhasil dijalankan”.

## 4. Lab 9 — menerbitkan image ke GHCR

**Baca lokal:**

```bash
cat .github/workflows/publish.yml
```

Pada proyek ini file tersebut sudah ada; jangan menyalin ulang contoh hingga menimpa perubahan. Alurnya: test → tentukan nama image → build → start → smoke → login → push → catat digest → cleanup. Workflow dipicu push ke `main`, sehingga PR biasanya hanya menjalankan CI Practice, lalu publish berjalan setelah merge.

`GITHUB_TOKEN` dapat digunakan workflow untuk menerbitkan package terkait repository, dengan izin package yang sesuai. Job publish memakai `packages: write`; job yang hanya menarik image memerlukan akses baca package. Hindari mencetak token ke log. [Autentikasi GHCR](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)

**Potongan runner yang sudah ada untuk dipahami:**

```bash
echo "IMAGE=ghcr.io/${GITHUB_REPOSITORY,,}" >> "$GITHUB_ENV"
docker build --build-arg APP_VERSION="$GITHUB_SHA" -t "$IMAGE:$GITHUB_SHA" .
docker push "$IMAGE:$GITHUB_SHA"
```

Baris pertama membuat nama repository huruf kecil. Langkah build, test container, dan push harus memakai referensi image yang sama. Jangan menambahkan build kedua antara smoke dan push.

Setelah run berhasil, periksa ringkasan Capture digest dan package terkait repository. Catat **commit, run, tag, dan digest** sebagai satu pasangan bukti rilis. Package tersedia tidak berarti aplikasi sudah berjalan sebagai layanan.

**Jika publish gagal:** lihat langkah pertama yang gagal. Test gagal berarti perbaiki kode/test; login atau push ditolak berarti periksa izin token, kepemilikan package, dan akses repository; nama image tidak valid berarti periksa huruf kecil. Jangan menyelesaikan semua masalah akses dengan token berizin luas.

## 5. Lab 10 — rancangan verifikasi artifact setelah publish

Latihan lanjutan memisahkan build dari konsumen artifact: job baru mengambil image **berdasarkan digest**, menjalankannya pada runner baru, lalu menguji versi. Ini membuktikan artifact registry dapat dipakai di luar proses build awal.

Potongan berikut **bukan workflow lengkap dan belum siap dijalankan**. Ia mengasumsikan checkout script smoke, Python, login GHCR, izin baca package, serta input `IMAGE_DIGEST` dan `EXPECTED_VERSION` yang telah divalidasi. `IMAGE_DIGEST` harus berisi referensi lengkap dengan `@sha256:`, bukan tag.

```yaml
# Contoh steps pada job verifikasi artifact di runner GitHub.
# Prasyarat konfigurasi di atas harus dipenuhi sebelum digunakan.
- name: Pull artifact berdasarkan digest
  run: docker pull "$IMAGE_DIGEST"
- name: Jalankan artifact untuk verifikasi
  run: docker run -d --name verify-artifact -p 127.0.0.1:8080:8080 "$IMAGE_DIGEST"
- name: Verifikasi versi dan fungsi
  run: python scripts/smoke.py http://127.0.0.1:8080 --expect-version "$EXPECTED_VERSION"
- name: Ambil log
  if: always()
  run: docker logs verify-artifact || true
- name: Bersihkan container percobaan
  if: always()
  run: docker rm -f verify-artifact || true
```

**Uji gagal lalu pulih:** pada job percobaan, pertahankan digest benar tetapi isi versi yang diharapkan dengan nilai sengaja salah. Smoke harus gagal dengan “Versi salah”. Kembalikan versi sesuai artifact dan ulangi. Latihan ini mendeteksi salah artifact, bukan hanya server yang hidup.

**Bukti selesai nanti:** log pull berdasarkan digest, versi yang benar, kegagalan yang disengaja, dan hasil pemulihan. Jangan menandai checkpoint ini selesai hanya karena membaca potongan YAML.

## 6. Bedakan runner sementara dan staging

Runner CI digunakan untuk pekerjaan terbatas. Container yang dijalankan di sana berhenti ketika job dibersihkan; alamat `127.0.0.1` milik runner tidak dapat dipakai sebagai URL aplikasi publik Anda. GitHub-hosted runner menyediakan mesin untuk mengeksekusi job, bukan target hosting aplikasi Anda. [Dokumentasi runner](https://docs.github.com/en/actions/concepts/runners/github-hosted-runners) Staging adalah lingkungan target yang disiapkan untuk validasi rilis, dengan konfigurasi, data, akses, dan masa hidup yang jelas.

Sebelum memilih hosting, tulis kebutuhan: harus selalu hidup atau hanya saat demo, perkiraan pengguna, data yang boleh hilang, kebutuhan HTTPS, lokasi, biaya yang dapat diterima, serta siapa yang mengoperasikan. Jangan menganggap ada VM, cluster, akun cloud, domain, atau budget yang belum disediakan.

| Keputusan sebelum deployment | Bukti yang perlu disiapkan |
|---|---|
| Target dan biaya | Pilihan layanan serta batas pemakaian yang disetujui |
| Artifact | Digest teruji dan identitas versi |
| Akses | Identitas deploy berizin minimum |
| Runtime | Port, command, resource, dan probe |
| Data | Lokasi persisten, migrasi, backup, dan restore |
| Pemulihan | Digest versi sebelumnya dan langkah rollback |

Task API menggunakan `http.server` untuk belajar. Sebelum layanan nyata melayani pengguna, desain runtime produksi, autentikasi, HTTPS, pengendalian akses data, dan operasi harus disiapkan. Keberhasilan CI latihan belum membuktikan kesiapan produksi.

## 7. Konfigurasi, secret, dan environment

Konfigurasi nonrahasia meliputi port, versi, dan alamat layanan. Secret meliputi password serta token akses. Image yang sama dapat memakai konfigurasi runtime berbeda untuk staging dan production, sehingga tidak perlu rebuild untuk sekadar mengganti konfigurasi lingkungan.

Dalam proyek, `DB_PATH` menentukan file SQLite. Menetapkan `/data/tasks.db` tidak otomatis membuat data persisten: storage harus dipasang oleh target deployment. Database yang hanya berada dalam writable layer container dapat hilang saat container diganti. Untuk banyak replika, evaluasi database bersama dan kebutuhan konkurensi sebelum sekadar menambah jumlah container.

GitHub Environment dapat menjadi bagian kontrol deployment, misalnya memisahkan konfigurasi dan perlindungan lingkungan. Aturan persetujuan dan ketersediaan fitur bergantung paket akun serta visibilitas repository; verifikasi sebelum menyatakan approval gate aktif. Nama environment saja tidak membuat server staging. [Environment dan perlindungan deployment](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments)

**Latihan desain:** buat tabel staging dan production berisi nama variabel, nilai nonrahasia, lokasi penyimpanan secret, dan pemilik akses. Simpan nama secret dan petunjuk penyediaannya dalam dokumentasi; jangan simpan nilainya.

## 8. Lab 11 — readiness dan pemulihan ringan tanpa Docker lokal

Latihan berikut sepenuhnya lokal dan hanya mengubah konfigurasi satu proses.

Jika server dari latihan sebelumnya masih memakai port 8081, hentikan dulu dengan Ctrl+C pada terminal server tersebut sebelum menjalankan proses baru.

**Git Bash pertama:**

```bash
HOST=127.0.0.1 PORT=8081 APP_VERSION=dev FAIL_READY=1 py app.py
```

**Git Bash kedua:**

```bash
curl -i http://127.0.0.1:8081/health
curl -i http://127.0.0.1:8081/ready
py scripts/smoke.py http://127.0.0.1:8081 --expect-version dev
```

Hasil harapan: health 200, readiness 503, dan smoke gagal. Proses hidup tetapi tidak layak menerima traffic. Hentikan server dengan Ctrl+C, lalu jalankan lagi dengan `FAIL_READY=0`. Smoke harus kembali berhasil. Ini simulasi kesiapan layanan, bukan deployment produksi.

Pelajaran: deployment perlu menunggu kesiapan sebelum mengalihkan pengguna. Tidur tetap seperti `sleep 30` hanya menunggu waktu; probe memeriksa kondisi nyata. Retry harus terbatas dan menyimpan log kegagalan.

## 9. Dasar rollback dan data

Rollback aplikasi berarti menjalankan artifact sebelumnya yang sudah diketahui, lalu memverifikasi readiness, versi, dan fungsi. Rancangan rilis sederhana: catat digest lama → pasang digest baru → tunggu ready → smoke → jika gagal, pulihkan digest lama → verifikasi kembali.

Rollback image tidak otomatis mengembalikan database. Migrasi yang menghapus kolom dapat membuat versi lama tidak kompatibel. Rencanakan perubahan bertahap: tambah struktur yang kompatibel, ubah aplikasi, migrasikan data, lalu hapus struktur lama setelah aman. Backup tanpa latihan restore belum membuktikan pemulihan bisa dilakukan.

**Latihan meja:** buat skenario v2 gagal ready sementara v1 masih sehat. Tuliskan siapa memutuskan rollback, batas waktu, digest tujuan, indikator berhasil, serta kondisi yang mengharuskan pemulihan database terpisah. Gunakan data latihan untuk simulasi; jangan menjadikan penghapusan data sebagai jalan pintas.

## 10. Checkpoint menuju materi profesional

- [ ] Dapat menjelaskan image, container, registry, tag, digest, dan commit.
- [ ] Memiliki bukti build dan smoke pada runner GitHub.
- [ ] Memverifikasi publish GHCR dan mencatat digest; belum terverifikasi berarti belum selesai.
- [ ] Memahami rancangan pull berdasarkan digest dan test versi.
- [ ] Berhasil membuat readiness gagal lalu pulih secara lokal.
- [ ] Memiliki rancangan staging, konfigurasi, data persisten, serta rollback.
- [ ] Memahami bahwa target deployment nyata masih harus dipilih dan disiapkan.

Lanjutkan melalui [roadmap](roadmap.md) ke keamanan supply chain, observability, reliability, dan praktik senior. Ukur kemajuan dari bukti perubahan yang dapat dirilis dan dipulihkan, bukan jumlah tool yang pernah dipasang.
