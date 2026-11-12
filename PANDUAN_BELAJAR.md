# Panduan Belajar FinanceTrack — Dari Nol Sampai GitHub

Panduan ini dirancang untuk fresh graduate dengan dasar Python. **Jangan hanya menyalin kode**: jalankan satu tahap, pahami alurnya, lalu coba latihan kecil yang tersedia.

## 0. Siapkan alat

- Instal Python versi 3.11 atau lebih baru (saat instalasi di Windows, aktifkan opsi menambahkan Python ke PATH bila tersedia).
- Instal VS Code, ekstensi **Python** dari Microsoft, dan Git.
- Buka folder `finance-track` di VS Code menggunakan **File → Open Folder**.
- Buka **Terminal → New Terminal**.

Jalankan pada PowerShell:

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m flask --app app init-db
python -m flask --app app run --debug
```

Jika terminal PowerShell tidak bisa mengaktifkan `.venv`, buka **Command Prompt** di VS Code dan jalankan `.venv\Scripts\activate.bat`. Buka `http://127.0.0.1:5000` di browser. Terminal Flask harus tetap berjalan selama aplikasi digunakan. Untuk menghentikan server tekan `Ctrl+C`.

### Pahami apa yang dilakukan perintah tadi

- `python -m venv .venv`: membuat lingkungan library Python terpisah.
- `python -m pip install -r requirements.txt`: membaca daftar dependensi dan memasang Flask.
- `python -m flask --app app init-db`: memanggil perintah `init-db` yang kita daftarkan di `app.py`, kemudian membuat tabel di SQLite.
- `python -m flask --app app run --debug`: menjalankan server web lokal dengan auto-reload untuk belajar. **Jangan** gunakan `--debug` di server publik.

## 1. Kenali alur aplikasi web

```text
Browser                 Flask (app.py)              SQLite (instance/keuangan.sqlite3)
  |                         |                              |
  |-- GET / -------------->|                              |
  |                         |--- SELECT transaksi -------->|
  |                         |<-- data transaksi ------------|
  |<-- HTML dashboard ------|                              |
  |                         |                              |
  |-- POST /tambah -------->|                              |
  |                         |--- INSERT transaksi -------->|
  |<-- redirect ke / -------|                              |
```

Browser mengirim **request** (permintaan). Flask mencari **route** yang cocok, menjalankan fungsi Python, membaca/menulis database bila dibutuhkan, dan mengirim **response** (balasan HTML atau file CSV).

## 2. Pelajaran Python dalam `app.py`

Buka `app.py`. Mulai dari baris-baris ini:

```python
JENIS = ("pemasukan", "pengeluaran")
BATAS_JUMLAH = 999_999_999_999
```

- `JENIS` adalah **tuple**, kumpulan nilai yang tidak perlu berubah.
- `BATAS_JUMLAH` adalah **konstanta** (nama dengan huruf besar mengisyaratkan nilai tetap).

Lihat `def rupiah(angka):`. Itu adalah **fungsi**, blok logika yang dapat dipanggil berulang kali.

```python
def rupiah(angka):
    return "Rp " + format(angka, ",").replace(",", ".")
```

Input `rupiah(150000)` akan menghasilkan teks `Rp 150.000`. Ini bukan angka baru; hanya format untuk ditampilkan.

**Latihan:** cari fungsi `baca_form()` dan jawab: mengapa kita harus memeriksa jumlah lebih besar dari nol sebelum menyimpan?

## 3. Pelajaran Flask: routing dan request

Perhatikan di dalam fungsi `buat_aplikasi()`:

```python
@app.get("/")
def index():
    ...
```

- `@app.get("/")` adalah **decorator**. Flask menghubungkan permintaan GET ke alamat `/` dengan fungsi `index()`.
- `@app.route("/tambah", methods=["GET", "POST"])`: `GET` menampilkan formulir, sedangkan `POST` memproses data yang dikirim.
- `request.form` berisi nilai input formulir yang dikirim lewat POST.
- `render_template("index.html", ...)` membuat HTML dari template dan data.
- `redirect(url_for("index"))` mengarahkan browser kembali ke halaman dashboard setelah data berhasil disimpan.

**Latihan:** ubah judul pada `templates/index.html` menjadi kata-katamu sendiri, lalu refresh browser.

## 4. Pelajaran SQLite: database dan SQL

Buka `schema.sql`.

```sql
CREATE TABLE IF NOT EXISTS transaksi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tanggal TEXT NOT NULL,
    jenis TEXT NOT NULL CHECK (jenis IN ('pemasukan', 'pengeluaran')),
    kategori TEXT NOT NULL,
    jumlah INTEGER NOT NULL CHECK (jumlah > 0),
    keterangan TEXT NOT NULL DEFAULT ''
);
```

- **Table** = lembar penyimpanan data.
- **Row** = satu baris transaksi.
- **Column** = atribut data seperti tanggal, jumlah, kategori.
- **Primary key** = ID unik tiap transaksi.
- **CHECK** = aturan yang juga dicek oleh database.

Empat perintah utama SQL disebut **CRUD**:

| Istilah | SQL | Di aplikasi |
|---|---|---|
| Create | `INSERT` | Tambah transaksi |
| Read | `SELECT` | Dashboard |
| Update | `UPDATE` | Edit transaksi |
| Delete | `DELETE` | Hapus transaksi |

Perhatikan tanda tanya pada kode SQL:

```python
db.execute("DELETE FROM transaksi WHERE id = ?", (transaksi_id,))
```

Itu adalah **parameterized query**. Nilai `transaksi_id` dikirim terpisah dari perintah SQL. Cara ini lebih aman daripada menyisipkan teks input langsung ke query.

Fungsi `get_db()` membuka koneksi database. `db.commit()` menyimpan perubahan. `close_db()` menutup koneksi setelah request.

**Latihan:** tambah dua transaksi lewat browser dan periksa apakah data masih ada setelah kamu menghentikan lalu menjalankan server Flask lagi.

## 5. Pelajaran HTML dan Jinja

Buka `templates/base.html`, `templates/index.html`, dan `templates/form.html`.

- `base.html`: kerangka yang dipakai semua halaman.
- `{% extends 'base.html' %}`: menggunakan kerangka tersebut.
- `{{ rupiah(saldo) }}`: menampilkan nilai variabel `saldo` yang berasal dari Python.
- `{% for t in transaksi %}`: mengulang satu baris tabel untuk setiap transaksi.
- HTML `<form method="post">` mengirim data ke Flask.

`static/style.css` mengatur warna, ukuran, spacing, dan tampilan mobile. Belajar CSS bisa setelah memahami jalur request–database–response.

**Latihan:** ubah warna tombol `.btn-primary` dan lihat pengaruhnya.

## 6. Hitung saldo: latihan logika

Misalnya kamu membuat catatan:

- Pemasukan: Rp 1.500.000
- Pengeluaran: Rp 50.000

Perhitungannya:

```text
saldo = pemasukan - pengeluaran
saldo = 1.500.000 - 50.000
saldo = 1.450.000
```

Flask menghitung total melalui query `SUM(...)` dari SQLite lalu menguranginya. Filter **bulan** berlaku untuk ringkasan, sedangkan filter **jenis** hanya berlaku untuk daftar transaksi. Ini disengaja supaya saldo tidak berubah menjadi angka yang keliru ketika pengguna hanya ingin melihat pengeluaran.

**Latihan:** ubah angka pengeluaran menjadi Rp 60.000 dengan tombol Edit. Berapa saldo baru?

## 7. Pelajaran keamanan dasar

Proyek ini memakai:

- **Validasi server-side**: jumlah harus positif, tanggal harus valid, kategori harus dikenal.
- **Query parameter SQL**: mencegah injeksi SQL melalui input.
- **Token CSRF** pada form POST: menolak permintaan perubahan tanpa token sesi yang sesuai.
- **HTML escaping Jinja**: membantu menghindari penyisipan HTML berbahaya dari input teks.
- **`.gitignore`**: mencegah database dan file rahasia ikut diunggah ke GitHub.
- **Integer rupiah**: menghindari kesalahan pembulatan angka pecahan saat menyimpan uang.

**Batas keamanan yang penting:** belum ada login. Aplikasi ini untuk belajar dan menjalankan secara lokal, bukan untuk digunakan sebagai layanan keuangan publik. Untuk tahap berikutnya bisa ditambahkan akun, otorisasi per pengguna, konfigurasi server produksi, dan pengujian keamanan lebih luas.

## 8. Testing otomatis

Dari folder root proyek, jalankan:

```powershell
python -m unittest discover -s tests -v
```

Baca `tests/test_app.py`. Tes memakai database sementara agar tidak merusak data pengguna. Pengujian yang disediakan mencakup:

1. Halaman utama saat belum ada data.
2. Menambah pemasukan dan pengeluaran serta menghitung saldo.
3. Menolak angka yang tidak valid.
4. Filter jenis dan bulan.
5. Edit dan hapus transaksi.
6. Memblokir POST tanpa token CSRF.
7. Mengekspor CSV.

**Latihan:** coba sengaja mengubah nilai pada tes saldo agar salah, lalu lihat bagaimana `unittest` melaporkan kegagalan. Setelah itu kembalikan ke nilai yang benar.

## 9. Persiapan GitHub

Lakukan review sebelum upload:

- Database `instance/keuangan.sqlite3` **tidak ikut diunggah**.
- Folder `.venv` **tidak ikut diunggah**.
- Tidak ada kata sandi, API key, atau data keuangan pribadi dalam repository.
- `README.md` berisi deskripsi, fitur, cara menjalankan, dan cara tes.

Buat repository **kosong** bernama `finance-track` di GitHub. Kemudian di folder proyek:

```powershell
git init -b main
git status
git add .
git commit -m "Initial commit: FinanceTrack Flask SQLite"
git remote add origin https://github.com/USERNAME/finance-track.git
git push -u origin main
```

Ganti `USERNAME` dengan akun GitHubmu. Untuk commit pertama, Git mungkin meminta pengaturan identitas:

```powershell
git config --global user.name "Nama Kamu"
git config --global user.email "email-github@example.com"
```

**Yang perlu dipahami:**

- `git init`: memulai repository Git di laptop.
- `git status`: melihat perubahan yang belum disimpan.
- `git add .`: menandai berkas untuk masuk commit.
- `git commit`: membuat checkpoint kode.
- `git remote add origin`: menghubungkan repository lokal ke alamat GitHub.
- `git push`: mengirim commit ke GitHub.

Jika nanti mengembangkan fitur:

```powershell
git add .
git commit -m "Add monthly category report"
git push
```

## 10. Checklist proyek siap portofolio

- [ ] Saya dapat menjelaskan cara route Flask bekerja.
- [ ] Saya paham tabel transaksi dalam SQLite.
- [ ] Saya dapat menyebutkan empat operasi CRUD.
- [ ] Saya dapat menambah, mengedit, menghapus, dan memfilter transaksi.
- [ ] Saya menjalankan tes dan semuanya sukses di laptop saya.
- [ ] Saya mengambil screenshot dashboard menggunakan data contoh, bukan data pribadi.
- [ ] Saya mengunggah source code dan README ke GitHub.
- [ ] Saya bisa menjelaskan tantangan yang saya temui dan cara saya menyelesaikannya.

Contoh kalimat CV (sesuaikan dengan pekerjaan yang benar-benar kamu lakukan):

**FinanceTrack — Personal Finance Web App** | Python, Flask, SQLite, HTML/CSS  
Mengembangkan aplikasi CRUD untuk pencatatan keuangan dengan dashboard saldo, filter transaksi, ekspor CSV, validasi data, dan pengujian otomatis menggunakan `unittest`.
