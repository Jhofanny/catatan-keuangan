"""FinanceTrack: aplikasi manajemen keuangan pribadi dengan Flask dan SQLite."""

import csv
import hmac
import io
import os
import re
import secrets
import sqlite3
from datetime import date

import click
from flask import (
    Flask, abort, current_app, flash, g, redirect, render_template,
    request, Response, session, url_for,
)
from flask.cli import with_appcontext

JENIS = ("pemasukan", "pengeluaran")
KATEGORI = (
    "Gaji", "Freelance", "Bonus", "Makanan", "Transportasi",
    "Belanja", "Tagihan", "Pendidikan", "Hiburan", "Lainnya",
)
BATAS_JUMLAH = 999_999_999_999  # Simpan rupiah sebagai INTEGER, bukan float.


def get_db():
    """Ambil satu koneksi SQLite untuk setiap request/konteks aplikasi."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(error=None):
    """Tutup koneksi setelah request selesai."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Buat tabel dari schema.sql jika belum ada."""
    with current_app.open_resource("schema.sql") as file:
        get_db().executescript(file.read().decode("utf-8"))
    get_db().commit()


@click.command("init-db")
@with_appcontext
def init_db_command():
    init_db()
    click.echo("Database FinanceTrack siap digunakan.")


def token_csrf():
    """Token acak untuk memvalidasi form POST."""
    if "_csrf_token" not in session:
        session["_csrf_token"] = secrets.token_urlsafe(32)
    return session["_csrf_token"]


def rupiah(angka):
    """Ubah 150000 menjadi 'Rp 150.000'."""
    return "Rp " + format(angka, ",").replace(",", ".")


def baca_form(form):
    """Validasi input dan kembalikan (data, pesan_error)."""
    data = {
        "tanggal": form.get("tanggal", "").strip(),
        "jenis": form.get("jenis", "").strip(),
        "kategori": form.get("kategori", "").strip(),
        "jumlah": form.get("jumlah", "").strip(),
        "keterangan": form.get("keterangan", "").strip(),
    }

    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", data["tanggal"]):
        return data, "Tanggal tidak valid."
    try:
        date.fromisoformat(data["tanggal"])
    except ValueError:
        return data, "Tanggal tidak valid."

    if data["jenis"] not in JENIS:
        return data, "Pilih jenis transaksi yang valid."
    if data["kategori"] not in KATEGORI:
        return data, "Pilih kategori yang tersedia."
    if not re.fullmatch(r"[0-9]{1,12}", data["jumlah"]):
        return data, "Jumlah harus berupa angka rupiah tanpa titik/koma (maks. 12 digit)."

    jumlah = int(data["jumlah"])
    if not 1 <= jumlah <= BATAS_JUMLAH:
        return data, "Jumlah harus lebih dari Rp 0 dan maksimal Rp 999.999.999.999."
    if len(data["keterangan"]) > 150:
        return data, "Keterangan maksimal 150 karakter."

    data["jumlah"] = jumlah
    return data, None


def ambil_transaksi(transaksi_id):
    hasil = get_db().execute(
        "SELECT * FROM transaksi WHERE id = ?", (transaksi_id,)
    ).fetchone()
    if hasil is None:
        abort(404)
    return hasil


def buat_filter(args):
    """Bangun WHERE SQL dan parameternya secara aman (tanpa gabung input mentah)."""
    jenis = args.get("jenis", "")
    bulan = args.get("bulan", "")
    if jenis not in JENIS:
        jenis = ""
    if not re.fullmatch(r"[0-9]{4}-(0[1-9]|1[0-2])", bulan):
        bulan = ""

    kondisi, parameter = [], []
    if jenis:
        kondisi.append("jenis = ?")
        parameter.append(jenis)
    if bulan:
        kondisi.append("substr(tanggal, 1, 7) = ?")
        parameter.append(bulan)
    where = " WHERE " + " AND ".join(kondisi) if kondisi else ""
    return jenis, bulan, where, parameter


def buat_aplikasi(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", secrets.token_hex(32)),
        DATABASE=os.path.join(app.instance_path, "keuangan.sqlite3"),
    )
    if test_config:
        app.config.update(test_config)
    os.makedirs(app.instance_path, exist_ok=True)

    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.jinja_env.globals.update(rupiah=rupiah, token_csrf=token_csrf)

    @app.before_request
    def periksa_csrf():
        if request.method == "POST":
            dikirim = request.form.get("_csrf_token", "")
            tersimpan = session.get("_csrf_token", "")
            if not tersimpan or not hmac.compare_digest(dikirim, tersimpan):
                abort(400, description="Form tidak valid. Muat ulang halaman dan coba lagi.")

    @app.get("/")
    def index():
        jenis, bulan, where, parameter = buat_filter(request.args)
        transaksi = get_db().execute(
            "SELECT * FROM transaksi" + where + " ORDER BY tanggal DESC, id DESC",
            parameter,
        ).fetchall()

        # Kartu ringkasan mengikuti filter BULAN, tetapi tidak filter JENIS.
        # Dengan begitu saldo selalu = semua pemasukan - semua pengeluaran.
        where_ringkasan = " WHERE substr(tanggal, 1, 7) = ?" if bulan else ""
        parameter_ringkasan = (bulan,) if bulan else ()
        ringkasan = get_db().execute(
            "SELECT "
            "COALESCE(SUM(CASE WHEN jenis = 'pemasukan' THEN jumlah ELSE 0 END), 0) AS pemasukan, "
            "COALESCE(SUM(CASE WHEN jenis = 'pengeluaran' THEN jumlah ELSE 0 END), 0) AS pengeluaran "
            "FROM transaksi" + where_ringkasan,
            parameter_ringkasan,
        ).fetchone()
        saldo = ringkasan["pemasukan"] - ringkasan["pengeluaran"]
        return render_template(
            "index.html", transaksi=transaksi, jenis=jenis, bulan=bulan,
            ringkasan=ringkasan, saldo=saldo,
        )

    @app.route("/tambah", methods=["GET", "POST"])
    def tambah():
        data = {"tanggal": date.today().isoformat(), "jenis": "pengeluaran",
                "kategori": "Makanan", "jumlah": "", "keterangan": ""}
        error = None
        if request.method == "POST":
            data, error = baca_form(request.form)
            if error is None:
                db = get_db()
                db.execute(
                    "INSERT INTO transaksi (tanggal, jenis, kategori, jumlah, keterangan) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (data["tanggal"], data["jenis"], data["kategori"],
                     data["jumlah"], data["keterangan"]),
                )
                db.commit()
                flash("Transaksi berhasil ditambahkan.", "success")
                return redirect(url_for("index"))
        return render_template("form.html", judul="Tambah Transaksi", data=data,
                               error=error, kategori=KATEGORI)

    @app.route("/transaksi/<int:transaksi_id>/edit", methods=["GET", "POST"])
    def edit(transaksi_id):
        transaksi = ambil_transaksi(transaksi_id)
        data = dict(transaksi)
        error = None
        if request.method == "POST":
            data, error = baca_form(request.form)
            if error is None:
                db = get_db()
                db.execute(
                    "UPDATE transaksi SET tanggal = ?, jenis = ?, kategori = ?, "
                    "jumlah = ?, keterangan = ? WHERE id = ?",
                    (data["tanggal"], data["jenis"], data["kategori"],
                     data["jumlah"], data["keterangan"], transaksi_id),
                )
                db.commit()
                flash("Transaksi berhasil diperbarui.", "success")
                return redirect(url_for("index"))
        return render_template("form.html", judul="Edit Transaksi", data=data,
                               error=error, kategori=KATEGORI)

    @app.post("/transaksi/<int:transaksi_id>/hapus")
    def hapus(transaksi_id):
        ambil_transaksi(transaksi_id)
        db = get_db()
        db.execute("DELETE FROM transaksi WHERE id = ?", (transaksi_id,))
        db.commit()
        flash("Transaksi berhasil dihapus.", "success")
        return redirect(url_for("index"))

    @app.get("/ekspor")
    def ekspor():
        _, _, where, parameter = buat_filter(request.args)
        transaksi = get_db().execute(
            "SELECT * FROM transaksi" + where + " ORDER BY tanggal DESC, id DESC",
            parameter,
        ).fetchall()
        keluaran = io.StringIO()
        keluaran.write("\ufeff")  # BOM agar Excel lebih mudah membaca UTF-8.
        penulis = csv.writer(keluaran)
        penulis.writerow(["ID", "Tanggal", "Jenis", "Kategori", "Jumlah (Rp)", "Keterangan"])
        for t in transaksi:
            # Cegah teks bebas dievaluasi sebagai rumus saat CSV dibuka di spreadsheet.
            keterangan = t["keterangan"]
            if keterangan.lstrip().startswith(("=", "+", "-", "@")):
                keterangan = "'" + keterangan
            penulis.writerow([
                t["id"], t["tanggal"], t["jenis"], t["kategori"],
                t["jumlah"], keterangan,
            ])
        return Response(
            keluaran.getvalue(), mimetype="text/csv; charset=utf-8",
            headers={"Content-Disposition": 'attachment; filename="financetrack.csv"'},
        )

    return app


# Nama `app` dipakai oleh perintah: flask --app app run
app = buat_aplikasi()
