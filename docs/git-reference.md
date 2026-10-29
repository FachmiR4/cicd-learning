# Referensi perintah Git dari dasar sampai lanjutan

[README](../README.md) · [Roadmap](roadmap.md)

Bagian ini melengkapi praktik CI/CD dengan fungsi, kegunaan, dan contoh perintah Git yang sering digunakan. Materi mengadaptasi cakupan PDF **Panduan Git dari Dasar sampai Senior** yang diberikan sebagai referensi; contoh Laravel disesuaikan ke proyek Python ini. Perintah di bawah adalah referensi dan latihan, bukan daftar untuk dijalankan sekaligus.

## 1. Cara Git menyimpan pekerjaan

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

## 2. Perintah inti yang paling sering dipakai

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

## 3. Persiapan repository dan konfigurasi

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

## 4. Memeriksa dan memilih perubahan

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

## 5. Commit yang jelas dan riwayat yang mudah dibaca

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

## 6. Branch, remote, fetch, pull, dan push

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

## 7. Merge dan penyelesaian konflik

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

## 8. Stash untuk menyimpan pekerjaan sementara

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

## 9. Restore, reset, dan revert: pilih sesuai masalah

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

## 10. Rebase dan interactive rebase

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

## 11. Cherry-pick, reflog, dan bisect

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

## 12. Tag, worktree, dan kemampuan lanjutan

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

## 13. Perintah yang perlu perhatian sebelum dijalankan

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

## 14. Tiga latihan praktik yang sesuai proyek

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

## 15. Alur kerja Git yang digunakan dalam pembelajaran CI/CD

```text
Periksa status → Update main → Buat branch → Edit
→ Test lokal → Review diff → Stage → Commit → Push
→ PR → Review + CI → Merge → Update main lokal
```

Jika PR merah: buka log → perbaiki pada branch PR yang sama → test → commit → push → tunggu run commit terbaru. Jika commit sudah terlanjur dibagikan dan perlu dibatalkan: utamakan revert melalui branch/PR. Jika commit terlihat hilang: periksa reflog dan buat rescue branch sebelum mengubah riwayat lagi.

**Urutan penguasaan:** status/diff/add/commit → branch/remote/push/pull → PR dan konflik → stash/restore/revert → log/blame/reflog → rebase/cherry-pick → bisect/worktree → praktik tim, signing, dan pengelolaan repository besar.

Referensi pendamping: PDF **Panduan Git dari Dasar sampai Senior** yang dilampirkan pengguna, serta [manual Git](https://git-scm.com/docs) dan [Pro Git](https://git-scm.com/book/en/v2). Materi PDF dipakai sebagai cakupan pembelajaran; contoh di sini disesuaikan dengan Git Bash, Python, dan alur PR proyek ini.
