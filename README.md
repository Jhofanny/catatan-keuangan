# FinanceTrack — Aplikasi Manajemen Keuangan Pribadi

Aplikasi web pencatatan pemasukan dan pengeluaran menggunakan **Python, Flask, SQLite, HTML, dan CSS**. Dibuat sebagai proyek latihan backend dan portofolio Junior Python Developer.

> **Catatan:** Versi ini dirancang untuk penggunaan lokal satu pengguna. Belum memiliki login dan tidak boleh dipublikasikan ke internet dengan data keuangan sungguhan tanpa autentikasi dan perlindungan tambahan.

## Fitur

- Dashboard: total pemasukan, pengeluaran, dan saldo bersih.
- Tambah, lihat, edit, dan hapus transaksi (CRUD).
- Filter menurut jenis transaksi dan bulan.
- Ekspor hasil filter ke CSV.
- Validasi jumlah dan tanggal, query SQL berparameter, token CSRF pada form.
- Pengujian otomatis dengan `unittest`.

## Teknologi

- Python 3.11+
- Flask 3.1+
- SQLite (`sqlite3` bawaan Python)
- Jinja2, HTML, CSS

## Struktur proyek

```text
finance-track/
├── app.py                  # Route Flask, logika bisnis, validasi
├── schema.sql              # Struktur tabel SQLite
├── requirements.txt        # Dependensi Python
├── templates/
│   ├── base.html           # Layout utama
│   ├── index.html          # Dashboard + riwayat transaksi
│   └── form.html           # Form tambah dan edit
├── static/
│   └── style.css           # Tampilan responsif
├── tests/
│   └── test_app.py         # Pengujian otomatis
├── .gitignore              # File yang tidak boleh di-commit
├── .env.example            # Contoh konfigurasi lingkungan
└── README.md               # Dokumentasi proyek
```

## Cara menjalankan (Windows)

1. Pastikan Python 3.11+ dan Git tersedia.
2. Buka terminal di direktori proyek.
3. Buat dan aktifkan virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Jika PowerShell memblokir aktivasi, gunakan Command Prompt dan `.venv\Scripts\activate.bat`.

4. Instal paket:

```powershell
python -m pip install -r requirements.txt
```

5. Buat database (cukup sekali untuk database baru):

```powershell
python -m flask --app app init-db
```

6. Jalankan aplikasi untuk belajar di komputer sendiri:

```powershell
python -m flask --app app run --debug
```

7. Buka `http://127.0.0.1:5000` di browser.

Jangan gunakan `--debug` jika aplikasi diakses publik.

## Cara menguji

```powershell
python -m unittest discover -s tests -v
```

Tes menggunakan database SQLite sementara, bukan data keuangan asli.

## Penjelasan konsep penting

- `@app.get('/')`: fungsi Python dijalankan ketika browser mengakses alamat tertentu (routing).
- `request.form`: membaca data yang dimasukkan pengguna pada formulir.
- `sqlite3.connect()`: membuka koneksi ke database lokal.
- `?` pada SQL: tempat nilai yang diikat aman ke query agar tidak menyisipkan SQL mentah.
- `db.commit()`: menyimpan hasil `INSERT`, `UPDATE`, atau `DELETE` secara permanen.
- `render_template()`: menggabungkan HTML dan nilai data dari Python.
- `redirect()`: memindahkan browser ke halaman lain setelah menyimpan perubahan.
- `url_for()`: menghasilkan URL berdasarkan nama fungsi view Flask.
- `unittest`: membuktikan fitur penting berjalan sesuai harapan.

Jumlah uang disimpan sebagai INTEGER rupiah, bukan float, untuk menghindari masalah pembulatan pecahan.

## Contoh uji manual

1. Tambahkan **pemasukan** Rp 1.500.000 kategori Gaji.
2. Tambahkan **pengeluaran** Rp 50.000 kategori Makanan.
3. Pastikan saldo dashboard = **Rp 1.450.000**.
4. Edit pengeluaran menjadi Rp 60.000, lalu cek saldo = Rp 1.440.000.
5. Filter bulan berjalan dan ekspor CSV.
6. Hapus pengeluaran, lalu cek saldo kembali ke Rp 1.500.000.

## Unggah ke GitHub

1. Buat repository GitHub baru bernama `finance-track`, tanpa README atau `.gitignore` awal (karena file ini sudah ada).
2. Di dalam folder proyek, jalankan:

```bash
git init -b main
git add .
git commit -m "Initial commit: aplikasi FinanceTrack Flask SQLite"
git remote add origin https://github.com/USERNAME/finance-track.git
git push -u origin main
```

Ganti `USERNAME` dengan username GitHub kamu. Pastikan `.gitignore` tidak mengikutsertakan `instance/` dan `.venv/`. GitHub mungkin meminta autentikasi via browser atau kredensial yang didukung, bukan password akun biasa.

## Ide pengembangan berikutnya

- Sistem login dan akun pengguna.
- Rekap atau grafik pengeluaran per kategori.
- Anggaran bulanan dan notifikasi jika mendekati batas.
- REST API JSON dan dokumentasi endpoint.
- Deployment aman ke server (setelah autentikasi dan hardening keamanan).

## Lisensi

Dapat digunakan sebagai bahan belajar dan dikembangkan sendiri.
