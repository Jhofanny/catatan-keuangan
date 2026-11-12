"""Jalankan: python -m unittest discover -s tests -v"""
import csv
import io
import os
import tempfile
import unittest
from pathlib import Path

from app import buat_aplikasi, init_db


class FinanceTrackTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.app = buat_aplikasi({
            "TESTING": True,
            "SECRET_KEY": "hanya-untuk-unit-test",
            "DATABASE": str(Path(self.folder.name) / "test.sqlite3"),
        })
        self.client = self.app.test_client()
        with self.app.app_context():
            init_db()

    def tearDown(self):
        self.folder.cleanup()

    def token(self):
        self.client.get("/tambah")
        with self.client.session_transaction() as sesi:
            return sesi["_csrf_token"]

    def tambah_data(self, jenis="pemasukan", jumlah="150000", tanggal="2026-11-12", keterangan="Kerja lepas"):
        return self.client.post("/tambah", data={
            "_csrf_token": self.token(),
            "tanggal": tanggal,
            "jenis": jenis,
            "kategori": "Freelance" if jenis == "pemasukan" else "Makanan",
            "jumlah": jumlah,
            "keterangan": keterangan,
        }, follow_redirects=True)

    def test_dashboard_awal_kosong(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Belum ada transaksi", response.data)

    def test_tambah_dan_total_saldo(self):
        self.tambah_data("pemasukan", "150000")
        response = self.tambah_data("pengeluaran", "50000")
        self.assertIn(b"Rp 150.000", response.data)
        self.assertIn(b"Rp 50.000", response.data)
        self.assertIn(b"Rp 100.000", response.data)

    def test_validasi_jumlah_negatif(self):
        response = self.tambah_data("pengeluaran", "-1000")
        self.assertIn(b"Jumlah harus berupa angka", response.data)
        self.assertIn(b"Belum ada transaksi", self.client.get("/").data)

    def test_filter_jenis_dan_bulan(self):
        self.tambah_data("pemasukan", "150000", "2026-11-12")
        self.tambah_data("pengeluaran", "50000", "2026-10-12")
        response = self.client.get("/?jenis=pemasukan&bulan=2026-11")
        self.assertIn(b"Rp 150.000", response.data)
        self.assertNotIn(b"Rp 50.000", response.data)

    def test_edit_lalu_hapus(self):
        self.tambah_data("pemasukan", "150000")
        response = self.client.post("/transaksi/1/edit", data={
            "_csrf_token": self.token(),
            "tanggal": "2026-11-12", "jenis": "pemasukan",
            "kategori": "Gaji", "jumlah": "200000", "keterangan": "Kerja paruh waktu",
        }, follow_redirects=True)
        self.assertIn(b"Rp 200.000", response.data)
        response = self.client.post("/transaksi/1/hapus", data={
            "_csrf_token": self.token(),
        }, follow_redirects=True)
        self.assertIn(b"Belum ada transaksi", response.data)

    def test_tidak_bisa_post_tanpa_csrf(self):
        response = self.client.post("/tambah", data={"jumlah": "150000"})
        self.assertEqual(response.status_code, 400)

    def test_ekspor_csv(self):
        self.tambah_data("pemasukan", "150000")
        response = self.client.get("/ekspor")
        self.assertEqual(response.status_code, 200)
        isi = response.data.decode("utf-8-sig")
        baris = list(csv.reader(io.StringIO(isi)))
        self.assertEqual(baris[1][4], "150000")
        self.assertEqual(baris[1][2], "pemasukan")


if __name__ == "__main__":
    unittest.main()
