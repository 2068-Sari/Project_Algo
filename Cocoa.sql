

CREATE TABLE kabupaten (
    id_kabupaten SERIAL PRIMARY KEY,
    nama_kabupaten VARCHAR(150) NOT NULL
);

SELECT * FROM kabupaten
CREATE TABLE kecamatan (
    id_kecamatan SERIAL PRIMARY KEY,
    nama_kecamatan VARCHAR(150) NOT NULL,
    id_kabupaten INTEGER REFERENCES kabupaten(id_kabupaten)
);

CREATE TABLE desa (
    id_desa SERIAL PRIMARY KEY,
    nama_desa VARCHAR(150) NOT NULL,
    id_kecamatan INTEGER REFERENCES kecamatan(id_kecamatan)
);

CREATE TYPE user_role AS ENUM ('admin', 'petani', 'pembeli');

CREATE TABLE users(
	id_user SERIAL PRIMARY KEY,
	users VARCHAR(100) UNIQUE NOT NULL,
	passwords VARCHAR(150) NOT NULL,
	nama_lengkap VARCHAR(150) NOT NULL,
	role_user user_role NOT NULL,  -- 1 admin, 2 petani, 3 pembeli
	no_telp VARCHAR(15) NOT NULL,
	detail_alamat VARCHAR(150) NOT NULL,
	id_desa INTEGER REFERENCES desa(id_desa)
);

CREATE TABLE produk_kakao (
    id_produk SERIAL PRIMARY KEY,
    nama_produk VARCHAR(150) NOT NULL DEFAULT 'Kakao',
    grade VARCHAR(15) NOT NULL,
    stok INTEGER NOT NULL,
    is_delete BOOLEAN NOT NULL
);

CREATE TABLE transaksi (
    id_transaksi SERIAL PRIMARY KEY,
	jenis_transaksi VARCHAR(100) DEFAULT 'pembelian' NOT NULL,
    tanggal_transaksi DATE NOT NULL,
    berat_biji DECIMAL(10,3) NOT NULL,
    grade_mutu VARCHAR(5) NOT NULL,
    harga_satuan INTEGER NOT NULL,
    id_user INTEGER REFERENCES users(id_user)
);

CREATE TABLE laporan (
    id_laporan SERIAL PRIMARY KEY,
    total_pembelian DECIMAL(15,2) NOT NULL,
    total_penjualan DECIMAL(15,2) NOT NULL,
    stok DECIMAL(10,3) NOT NULL,
    id_user INTEGER REFERENCES users(id_user)
);

CREATE TABLE detail_transaksi (
    id_detail_transaksi SERIAL PRIMARY KEY,
    jumlah INTEGER NOT NULL,
    harga_satuan_kg INTEGER NOT NULL,
    subtotal INTEGER NOT NULL,
    id_transaksi INTEGER REFERENCES transaksi(id_transaksi),
    id_produk INTEGER REFERENCES produk_kakao(id_produk)
);

CREATE TABLE pembayaran (
    id_pembayaran SERIAL PRIMARY KEY,
    metode_pembayaran VARCHAR(100) NOT NULL,
    status VARCHAR(100) NOT NULL,
    id_transaksi INTEGER REFERENCES transaksi(id_transaksi)
);


INSERT INTO kabupaten (nama_kabupaten) VALUES
('Jember');

INSERT INTO kecamatan (nama_kecamatan,id_kabupaten) VALUES
('Ajung', 1),
('Ambulu', 1),
('Balung', 1),
('Kaliwates', 1),
('Sumbersari', 1);

SELECT * FROM kecamatan

INSERT INTO desa (nama_desa, id_kecamatan) VALUES
('Ajung', 1),
('Mangaran', 1),
('Rowoindah', 1);

INSERT INTO desa (nama_desa, id_kecamatan) VALUES
('Ambulu', 2),
('Andongsari', 2),
('Sumberrejo', 2);

INSERT INTO desa (nama_desa, id_kecamatan) VALUES
('Balung Kulon', 3),
('Balung Lor', 3),
('Karangduren', 3);

INSERT INTO desa (nama_desa, id_kecamatan) VALUES
('Kaliwates', 4),
('Sempusari', 4),
('Mangli', 4);

INSERT INTO desa (nama_desa,id_kecamatan) VALUES
('Sumbersari', 5),
('Kebonsari', 5),
('Antirogo', 5);

SELECT * FROM users

INSERT INTO users (users, passwords, nama_lengkap, role_user, no_telp, detail_alamat, id_desa
) VALUES
('admin1', 'admin123', 'Admin Sistem', 'admin', '08123456789', 'jl.jawa C', 1),
('petani1', 'petani123', 'sari', 'petani', '082233445566', 'jl.mastrip', 3),
('pembeli1', 'pembeli123', 'darrel', 'pembeli', '083122334455', 'jl.toba', 5),
('petani2', 'petani1234', 'rega', 'petani', '082233344445', 'jl.brawijaya', 2);

INSERT INTO produk_kakao (grade, stok, is_delete) VALUES
('A', 150, FALSE),
('B', 200, FALSE),
('C', 300, FALSE);
SELECT * FROM produk_kakao

INSERT INTO transaksi (tanggal_transaksi, berat_biji, grade_mutu, harga_satuan, id_user) VALUES
('2025-11-01', 550.000, 'A', 60000, 2),
('2025-11-02', 300.000, 'B', 50000, 2),
('2025-11-03', 425.000, 'A', 61000, 4),
('2025-11-04', 600.000, 'C', 45000, 2),
('2025-11-05', 700.000, 'A', 62000, 4),
('2025-11-06', 200.000, 'B', 56000, 2);
INSERT INTO transaksi (tanggal_transaksi, berat_biji, grade_mutu, harga_satuan, jenis_transaksi, id_user) VALUES
('2025-11-06', 730.000, 'A', 62000, 'penjualan', 3);

SELECT * FROM transaksi

INSERT INTO detail_transaksi (jumlah, harga_satuan_kg, subtotal, id_transaksi, id_produk) VALUES
(550, 60000, 33000000, 1, 1),
(300, 50000, 15000000, 2, 2),
(425, 61000, 25925000, 3, 1),
(600, 45000, 27000000, 4, 3),
(700, 62000, 43400000, 5, 1),
(200, 56000, 11200000, 6, 2),
(730, 62000, 45260000, 7, 1);
SELECT * FROM detail_transaksi

INSERT INTO pembayaran (metode_pembayaran, status, id_transaksi) VALUES
('Transfer Bank', 'Lunas', 4),
('Tunai', 'Lunas', 5),
('Transfer Bank', 'Hutang', 6),
('Transfer Bank', 'Lunas', 1),
('Tunai', 'Hutang', 2),
('Transfer Bank', 'Lunas', 3);
SELECT * FROM pembayaran

INSERT INTO laporan (total_pembelian, total_penjualan, stok, id_user) VALUES 
(155525000, 45260000, 2695, 1);
SELECT * FROM laporan

