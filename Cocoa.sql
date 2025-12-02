CREATE TABLE kabupaten (
    id_kabupaten SERIAL PRIMARY KEY,
    nama_kabupaten VARCHAR(150) NOT NULL
);


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

CREATE TABLE produk (
    id_produk SERIAL PRIMARY KEY,
    nama_produk VARCHAR(150) NOT NULL DEFAULT 'Kakao',
    nama_grade VARCHAR(50) NOT NULL,
    stok DECIMAL(10,3) NOT NULL,
	deskripsi TEXT,
    is_delete BOOLEAN NOT NULL
);

CREATE TYPE jenis_transaksi_enum AS ENUM ('pembelian', 'penjualan');
CREATE TYPE status_transaksi_enum AS ENUM ('menunggu','diproses','selesai');
CREATE TYPE status_pembayaran_enum AS ENUM ( 'lunas','hutang','gagal');
CREATE TABLE transaksi (
    id_transaksi SERIAL PRIMARY KEY,
	tanggal DATE NOT NULL,
	jenis_transaksi jenis_transaksi_enum NOT NULL,
	status_transaksi status_transaksi_enum NOT NULL,
    status_pembayaran status_pembayaran_enum NOT NULL,
    id_user INTEGER REFERENCES users(id_user)
);

CREATE TABLE laporan (
    id_laporan SERIAL PRIMARY KEY,
	periode VARCHAR(100) NOT NULL,
    total_pembelian DECIMAL(15,2) NOT NULL,
    total_penjualan DECIMAL(15,2) NOT NULL,
	tanggal_dibuat DATE NOT NULL,
    stok DECIMAL(10,3) NOT NULL,
    id_user INTEGER REFERENCES users(id_user)
);

CREATE TABLE detail_transaksi (
    id_detail SERIAL PRIMARY KEY,
    berat_kg DECIMAL(10,3) NOT NULL,
    harga_satuan INTEGER NOT NULL,
    subtotal INTEGER NOT NULL,
    id_transaksi INTEGER REFERENCES transaksi(id_transaksi),
    id_produk INTEGER REFERENCES produk(id_produk)
);

CREATE TABLE metode_pembayaran (
    id_metode_pembayaran SERIAL PRIMARY KEY,
    nama_metode VARCHAR(100) NOT NULL,
    nama_bank VARCHAR(100),
    no_rekening VARCHAR(50)
);

CREATE TABLE pembayaran (
    id_pembayaran SERIAL PRIMARY KEY,
  	tanggal_bayar DATE NOT NULL,
    nominal_bayar INTEGER NOT NULL,
    id_transaksi INTEGER REFERENCES transaksi(id_transaksi),
	id_metode_pembayaran INTEGER REFERENCES metode_pembayaran(id_metode_pembayaran)
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
('Rowoindah', 1),
('Ambulu', 2),
('Andongsari', 2),
('Sumberrejo', 2),
('Balung Kulon', 3),
('Balung Lor', 3),
('Karangduren', 3),
('Kaliwates', 4),
('Sempusari', 4),
('Mangli', 4),
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

INSERT INTO produk (nama_grade, stok, deskripsi, is_delete)
VALUES
('A', 150, 'Kakao kualitas premium', FALSE),
('B', 200, 'Kakao kualitas menengah', FALSE),
('C', 300, 'Kakao kualitas rendah', FALSE);

SELECT * FROM produk

INSERT INTO transaksi 
(tanggal, jenis_transaksi, status_transaksi, status_pembayaran, id_user)
VALUES
('2025-11-01', 'penjualan', 'selesai', 'lunas', 2),
('2025-11-02', 'penjualan', 'selesai', 'lunas', 2),
('2025-11-03', 'penjualan', 'selesai', 'lunas', 4),
('2025-11-04', 'penjualan', 'selesai', 'lunas', 2),
('2025-11-05', 'penjualan', 'selesai', 'lunas', 4),
('2025-11-06', 'penjualan', 'selesai', 'hutang', 2),
('2025-11-06', 'pembelian', 'selesai', 'lunas', 3);


SELECT * FROM transaksi

INSERT INTO detail_transaksi
(berat_kg, harga_satuan, subtotal, id_transaksi, id_produk)
VALUES
(550, 60000, 33000000, 1, 1),
(300, 50000, 15000000, 2, 2),
(425, 61000, 25925000, 3, 1),
(600, 45000, 27000000, 4, 3),
(700, 62000, 43400000, 5, 1),
(200, 56000, 11200000, 6, 2),
(730, 62000, 45260000, 7, 1);

SELECT * FROM detail_transaksi

INSERT INTO metode_pembayaran (nama_metode, nama_bank, no_rekening) VALUES
('Tunai', NULL, NULL),
('Transfer Bank', 'BRI', '1234567890'),
('Transfer Bank', 'BCA', '9876543210');


INSERT INTO pembayaran
(tanggal_bayar, nominal_bayar, id_transaksi, id_metode_pembayaran)
VALUES
('2025-11-02', 15000000, 1, 2),
('2025-11-03', 33000000, 2, 1),
('2025-11-04', 25925000, 3, 2),
('2025-11-05', 27000000, 4, 1),
('2025-11-06', 43400000, 5, 2),
('2025-11-07', 11200000, 6, 2),
('2025-11-07', 45260000, 7, 2);


INSERT INTO laporan(periode, total_pembelian, total_penjualan, tanggal_dibuat, stok, id_user) VALUES
('November 2025', 155525000, 45260000, '2025-11-30', 2695, 1);


