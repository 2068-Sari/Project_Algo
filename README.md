AgroCocoa: Aplikasi Pengelolaan Transaksi Kakao Berbasis CLI 🌱💻

AgroCocoa adalah aplikasi transaksi kakao berbasis konsol (CLI) yang dibangun dengan Python dan terhubung langsung ke PostgreSQL sebagai database. Aplikasi ini mengelola produk kakao, pengguna (Admin, Petani, Pembeli), transaksi, dan pembayaran.
Aplikasi ini dirancang untuk membantu pengelolaan jual–beli  di koperasi cokelat Nusantara secara sederhana namun terstruktur.

Fitur Utama

Aplikasi memiliki tiga peran pengguna (role), dan setiap role memiliki fitur yang berbeda.

👑 Fitur Admin
Admin memiliki akses penuh untuk mengelola seluruh data dalam sistem.

🔑 Login
Admin memiliki menu khusus setelah login.

📦 Manajemen Produk Kakao
📋 Daftar Produk

Admin melihat seluruh produk yang statusnya belum dihapus (soft delete).

➕ Tambah Produk

Admin dapat menambah produk baru:
- Nama produk
- Grade
- Stok
Fungsi: tambah_produk().

✏️ Edit Produk
Admin dapat mengubah:
- Nama produk
- Grade
- Stok
Fungsi: update_produk().

❌ Hapus Produk

Penghapusan dilakukan soft delete, yaitu:
is_delete = TRUE
Produk tidak hilang, hanya disembunyikan.

Fungsi: hapus_produk().

💰 Manajemen Transaksi & Pembayaran
💵 Input Transaksi (Pembelian & Penjualan)

Admin dapat mencatat:
- Pembelian kakao → stok bertambah
- Penjualan kakao → stok berkurang
- Admin bebas memilih jenis transaksi.

Fitur:
- input id produk
- Input berat produk
- Hitung subtotal
- Tentukan status pembayaran
- Metode pembayaran (tunai / transfer)

🧾 Kelola Pembayaran

Admin dapat:
- Melihat seluruh data pembayaran
- Mengubah status pembayaran (Lunas / Belum)
- Mengubah metode pembayaran
Fungsi: kelola_pembayaran().

📊 Laporan Rekap

Admin dapat melihat:
- Total pembelian
- Total penjualan
- Total stok seluruh produk
- Total transaksi yang tercatat
Fungsi: laporan_rekap().


🛒 Fitur Pembeli (Buyer)
📝 Registrasi
Pembeli dapat membuat akun baru melalui menu registrasi. Data akan disimpan ke tabel users.

🔑 Login
Pembeli yang sudah memiliki akun dapat masuk menggunakan username dan password.

🛍️ Lihat Produk
Pembeli dapat melihat seluruh produk kakao yang tersedia, lengkap dengan:
- Nama produk
- Grade
- Harga per kg
- Stok tersedia
Fungsi ini menggunakan lihat_produk().

🛒 Melakukan Pembelian

Pembeli dapat membeli produk kakao melalui fungsi input_transaksi()
Fitur pembelian meliputi:
- Pilih produk
- Input berat (kg)
- Sistem menghitung subtotal
- Pembeli memasukkan uang pembayaran

Sistem menentukan:
Lunas → bila uang cukup
Hutang → bila uang kurang

Metode pembayaran: tunai atau transfer bank
Stok produk otomatis berkurang
Data pembelian masuk ke tabel:
transaksi
detail_transaksi
pembayaran

🧾 Lihat Riwayat Transaksi

Pembeli dapat melihat seluruh transaksi yang pernah dilakukan, meliputi:
- Produk
- Jumlah
- Harga/kg
- Subtotal
- Status pembayaran
- Tanggal transaksi
Fungsi: lihat_riwayat(id_user).


💻 Teknologi yang Digunakan
🔹 Python : Bahasa pemorograman utama untuk membangun aplikasi CLI.

🔹 PostgreSQL : Database utama untuk menyimpan data pengguna, produk, transaksi, dan pembayaran.

🔹 psycopg2: Digunakan untuk melakukan koneksi Python ↔ PostgreSQL.

🔹 tabulate : Menampilkan tabel dengan format rapi di konsol.

🔹 OS : Digunakan untuk membersihkan tampilan console (cls).

▶️ Cara Menjalankan Aplikasi
1. Pastikan Python dan pip terinstal.
   pip install psycopg2 tabulate

2. Buat database PostgreSQL kemudian sesuaikan konfigurasi di dalam kode
   DB_CONFIG = {
    "host": "localhost",
    "database": "...",
    "user": "...",
    "password": "..."
}

3. Pastikan tabel-tabel berikut sudah dibuat:
- users
- produk_kakao
- transaksi
- detail_transaksi
- pembayaran
- desa
- laporan
4. Jalankan aplikasi melalui Terminal:
  python agrococoa_app.py


👤 Akun 

Admin 👑
- username: admin1
- password: admin123

Petani 🌾
- username: petani1
- password: petani123
- username: petani2
- password: petani1234
  
Pembeli 🛒
- username: pembeli1
- password: pembeli123

