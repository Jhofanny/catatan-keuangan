CREATE TABLE IF NOT EXISTS transaksi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tanggal TEXT NOT NULL,
    jenis TEXT NOT NULL CHECK (jenis IN ('pemasukan', 'pengeluaran')),
    kategori TEXT NOT NULL,
    jumlah INTEGER NOT NULL CHECK (jumlah > 0),
    keterangan TEXT NOT NULL DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_transaksi_tanggal ON transaksi (tanggal);
