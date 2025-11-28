
import psycopg2
import os
from tabulate import tabulate

DB_CONFIG = {
    "host": "localhost",
    "user": "postgres",
    "password": "saripane*28",
    "port": "2809",
    "database": "Cocoa"
}

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def connectDB():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception:
      
        print("Gagal terhubung ke database")
        return None

# ini helper validasi 
def input_nonempty(prompt, maxlen=None):
    while True:
        v = input(prompt).strip()
        if v == "":
            print("Input tidak boleh kosong.")
            continue
        if maxlen and len(v) > maxlen:
            print(f"Input terlalu panjang (maks {maxlen} karakter).")
            continue
        return v

def input_digits(prompt, maxlen=None):
    while True:
        v = input(prompt).strip()
        if not v.isdigit():
            print("Masukkan hanya angka.")
            continue
        if maxlen and len(v) > maxlen:
            print(f"Input terlalu panjang (maks {maxlen} digit).")
            continue
        return v

def input_choice(prompt, choices, default=None):
    choices_str = "/".join(choices)
    while True:
        v = input(f"{prompt} ({choices_str}){' [default:'+str(default)+']' if default else ''}: ").strip().lower()
        if v == "" and default is not None:
            return default
        if v in choices:
            return v
        print("Pilihan tidak valid.")

def format_rp(amount):
    try:
        a = int(amount)
        return "Rp {:,}".format(a).replace(",", ".")
    except Exception:
        return str(amount)





# ----------------- registrasi -----------------
def registrasi():
    while True:
        clear()
        print('==============================')
        print('        REGISTRASI AKUN       ')
        print('==============================')
        print("Catatan: Ketik 0 kapan saja untuk kembali.\n")

        # ========== INPUT DASAR USER ==========
        username = input_nonempty("Username: ", maxlen=100)
        if username == "0":
            return

        password = input_nonempty("Password: ", maxlen=150)
        if password == "0":
            return

        nama = input_nonempty("Nama Lengkap: ", maxlen=150)
        if nama == "0":
            return

        # ========== PILIH ROLE ==========
        while True:
            print("\nPilih Role:")
            print("1. Petani")
            print("2. Pembeli")
            print("0. Kembali")

            role_input = input_choice("Masukkan Pilihan Role", ['1', '2', '0'])
            if role_input == "0":
                return
            if role_input in ["1", "2"]:
                break

        role = 'petani' if role_input == '1' else 'pembeli'

        # ========== TELEPON & ALAMAT ==========
        no_telp = input_digits("No. Telepon: ", maxlen=15)
        if no_telp == "0":
            return

        detail_alamat = input_nonempty("Detail Alamat: ", maxlen=150)
        if detail_alamat == "0":
            return

        # ========== KONEKSI DATABASE ==========
        conn = connectDB()
        if conn is None:
            input("Tekan Enter untuk kembali...")
            return

        cur = conn.cursor()

        try:
            # TAMPILKAN DESA
            cur.execute("""
                SELECT d.id_desa, d.nama_desa, k.nama_kecamatan, kb.nama_kabupaten
                FROM desa d
                JOIN kecamatan k ON d.id_kecamatan = k.id_kecamatan
                JOIN kabupaten kb ON k.id_kabupaten = kb.id_kabupaten
                ORDER BY d.id_desa
            """)
            desa_data = cur.fetchall()

            if not desa_data:
                print("Belum ada data desa di database. Hubungi admin.")
                conn.close()
                input("Tekan Enter...")
                return

            print("\nDaftar Desa Tersedia:")
            print(tabulate(desa_data,
                           headers=["ID Desa", "Desa", "Kecamatan", "Kabupaten"],
                           tablefmt="psql"))

            # ========== VALIDASI ID DESA (HANYA LOOP BAGIAN INI) ==========
            while True:
                id_desa = input_digits("\nMasukkan ID Desa Anda: ")

                if id_desa == "0":
                    return

                cur.execute("SELECT 1 FROM desa WHERE id_desa=%s", (id_desa,))
                if cur.fetchone() is not None:
                    break
                else:
                    print("ID Desa tidak ditemukan. Coba lagi.")
                    input("Tekan Enter...")

            # ========== INSERT USER ==========
            try:
                cur.execute("""
                    INSERT INTO users (users, passwords, nama_lengkap, role_user,
                                       no_telp, detail_alamat, id_desa)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (username, password, nama, role, no_telp, detail_alamat, id_desa))

                conn.commit()
                print("\nAkun berhasil dibuat!")
                input("Tekan Enter untuk kembali ke menu...")
                break

            except Exception:
                conn.rollback()
                print("Gagal membuat akun! (Username mungkin sudah digunakan.)")
                input("Tekan Enter...")

        except Exception:
            print("Terjadi masalah saat proses registrasi.")
            try:
                conn.rollback()
            except:
                pass
            input("Tekan Enter...")

        finally:
            cur.close()
            conn.close()



      

# ----------------- login -----------------
def login():
    while True:
        clear()
        print('========================')
        print('         LOGIN          ')
        print('========================')
        print("Ketik 'x' untuk kembali ke menu utama.\n")

        username = input("Username : ").strip()
        if username.lower() == 'x':
            return None  # kembali ke menu utama

        if username == "":
            print("Username tidak boleh kosong.")
            input("Tekan Enter...")
            continue

        password = input("Password : ").strip()
        if password.lower() == 'x':
            return None  # kembali ke menu utama

        if password == "":
            print("Password tidak boleh kosong.")
            input("Tekan Enter...")
            continue

        conn = connectDB()
        if conn is None:
            input("Tekan Enter...")
            return None

        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT id_user, nama_lengkap, role_user 
                FROM users 
                WHERE users=%s AND passwords=%s
            """, (username, password))
            user = cur.fetchone()

            if not user:
                print("Username atau password salah! Silakan coba lagi.")
                input("Tekan Enter...")
                continue  # kembali ke awal loop login

            data_user = {"id": user[0], "nama": user[1], "role": user[2]}
            print(f"\nLogin berhasil! Selamat datang {data_user['nama']}")
            input("Tekan Enter untuk melanjutkan...")
            return data_user

        except Exception:
            print("Gagal proses login. Coba lagi.")
            input("Tekan Enter...")
        finally:
            cur.close()
            conn.close()





# ----------------- produk -----------------
def lihat_produk(show_deleted=False):
    conn = connectDB()
    if conn is None:
        input("Tekan Enter...")
        return []

    clear()
    print("====================================")
    print("            DATA PRODUK             ")
    print("====================================")

    cur = conn.cursor()
    try:
        # Query produk berdasarkan parameter
        if show_deleted:
            cur.execute("""
                SELECT id_produk, nama_produk, grade, stok, is_delete
                FROM produk_kakao ORDER BY id_produk
            """)
        else:
            cur.execute("""
                SELECT id_produk, nama_produk, grade, stok
                FROM produk_kakao 
                WHERE is_delete = FALSE 
                ORDER BY id_produk
            """)

        data = cur.fetchall()
        if not data:
            print("Belum ada produk.")
            input("Tekan Enter...")
            return []

        # Harga tetap berdasarkan grade
        harga_grade = {
            'A': 62500,
            'B': 56000,
            'C': 49000
        }

        # Format tabel tampilan
        table_data = []
        for row in data:
            id_produk, nama, grade, stok = row[:4]
            harga = harga_grade.get(grade.upper(), 0)

            table_data.append([
                id_produk,
                nama,
                grade,
                stok,
                f"Rp {harga:,}".replace(",", ".")  # Format ribuan: Rp 62.500
            ])

        print(tabulate(
            table_data,
            headers=["ID", "Nama Produk", "Grade", "Stok (Kg)", "Harga/Kg (Rp)"],
            tablefmt="psql"
        ))

        input("Tekan Enter untuk kembali...")
        return data

    except Exception as e:
        print("Gagal menampilkan produk:", e)
        input("Tekan Enter...")
        return []

    finally:
        cur.close()
        conn.close()




# ------------------- tambah produk --------------------
def tambah_produk():
    while True:
        clear()
        print("===================================")
        print("          TAMBAH PRODUK            ")
        print("===================================")
        print("Tekan X untuk kembali ke menu admin\n")

        nama_produk = input("Nama Produk : ").strip()
        if nama_produk.lower() == "x":
            return  # kembali ke menu admin
        if not nama_produk:
            print("Nama produk tidak boleh kosong!")
            input("Tekan Enter...")
            continue

        grade = input_choice("Grade", ['a', 'b', 'c', 'x'] ).upper()
        if grade.lower() == "x":
            return
        
        stok = input_digits("Stok Produk  : ")
        if stok.lower() == "x":
            return

        conn = connectDB()
        if conn is None:
            input("Tekan Enter...")
            return

        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO produk_kakao (nama_produk, grade, stok, is_delete)
                VALUES (%s, %s, %s, FALSE)
            """, (nama_produk, grade, int(stok)))

            conn.commit()
            print("\nProduk berhasil ditambahkan!")

        except Exception:
            conn.rollback()
            print("Gagal menambah produk.")

        finally:
            cur.close()
            conn.close()

        input("Tekan Enter untuk kembali...")
        return  # kembali ke menu admin setelah selesai





# -------------------- update produk ---------------------
def update_produk():
    while True:
        clear()
        print("===================================")
        print("          UPDATE PRODUK            ")
        print("===================================")
        print("Tekan X untuk kembali ke menu admin\n")

        conn = connectDB()
        if conn is None:
            input("Tekan Enter...")
            return

        cur = conn.cursor()
        try:
            # tampilkan list produk
            cur.execute("""
                SELECT id_produk, nama_produk, grade, stok 
                FROM produk_kakao 
                WHERE is_delete = FALSE 
                ORDER BY id_produk
            """)
            rows = cur.fetchall()

            if not rows:
                print("Belum ada produk.")
                input("Tekan Enter...")
                return

            print(tabulate(rows, headers=["ID", "Nama", "Grade", "Stok"], tablefmt="psql"))

            # pilih ID produk
            idp = input("\nMasukkan ID produk yang ingin diupdate (X untuk kembali): ").strip()
            if idp.lower() == "x":
                return  # kembali ke menu admin

            if not idp.isdigit():
                print("ID harus berupa angka!")
                input("Tekan Enter...")
                continue

            idp = int(idp)

            # cek produk ada
            cur.execute("SELECT 1 FROM produk_kakao WHERE id_produk=%s AND is_delete=FALSE", (idp,))
            if cur.fetchone() is None:
                print("Produk tidak ditemukan.")
                input("Tekan Enter...")
                continue

            # input data baru
            nama_baru = input_nonempty("Nama Produk Baru : ", maxlen=150)
            if nama_baru.lower() == "x":
                return
            
            grade_baru = input_choice("Grade Baru", ['a', 'b', 'c', 'x']).upper()
            if grade_baru.lower() == "x":
                return
            
            stok_baru = input_digits("Stok Baru        : ")
            if stok_baru.lower() == 'x':
                return

            # update database
            cur.execute("""
                UPDATE produk_kakao 
                SET nama_produk=%s, grade=%s, stok=%s 
                WHERE id_produk=%s
            """, (nama_baru, grade_baru, int(stok_baru), idp))

            conn.commit()
            print("\nProduk berhasil diupdate!")

        except Exception as e:
            conn.rollback()
            print("Gagal update produk.")

        finally:
            cur.close()
            conn.close()

        input("Tekan Enter untuk kembali...")
        return





# ---------------------- hapus produk ------------------------
def hapus_produk():
    while True:
        clear()
        print("===================================")
        print("          HAPUS PRODUK             ")
        print("===================================")
        print("Tekan X untuk kembali ke menu admin\n")

        conn = connectDB()
        if conn is None:
            input("Tekan Enter...")
            return

        cur = conn.cursor()
        try:
            # tampilkan produk
            cur.execute("""
                SELECT id_produk, nama_produk 
                FROM produk_kakao 
                WHERE is_delete = FALSE 
                ORDER BY id_produk
            """)
            rows = cur.fetchall()

            if not rows:
                print("Belum ada produk.")
                input("Tekan Enter...")
                return

            print(tabulate(rows, headers=["ID", "Nama"], tablefmt="psql"))

            # pilih ID produk
            idp = input("\nMasukkan ID produk yang ingin dihapus (X untuk kembali): ").strip()
            if idp.lower() == "x":
                return   # kembali ke menu admin

            if not idp.isdigit():
                print("ID harus angka!")
                input("Tekan Enter...")
                continue

            idp = int(idp)

            # cek produk ada
            cur.execute("SELECT 1 FROM produk_kakao WHERE id_produk=%s AND is_delete=FALSE", (idp,))
            if cur.fetchone() is None:
                print("Produk tidak ditemukan atau sudah dihapus.")
                input("Tekan Enter...")
                continue

            # konfirmasi
            confirm = input_choice("Yakin ingin menghapus produk? (y/n)", ['y', 'n'], default='n')
            if confirm == 'y':
                cur.execute("UPDATE produk_kakao SET is_delete = TRUE WHERE id_produk=%s", (idp,))
                conn.commit()
                print("Produk berhasil dihapus")
            else:
                print("Penghapusan dibatalkan.")

        except Exception:
            conn.rollback()
            print("Gagal menghapus produk.")

        finally:
            cur.close()
            conn.close()

        input("Tekan Enter untuk kembali...")
        return





# ----------------- transaksi (generik) -----------------
def input_transaksi(admin_mode=False, current_user_id=None, role=None):
    clear()
    print("====================================")
    print("          INPUT TRANSAKSI           ")
    print("====================================")
    print("Ketik 'exit' untuk kembali\n")

    conn = connectDB()
    if conn is None:
        input("Tekan Enter...")
        return

    cur = conn.cursor()
    try:
        # ====================== TAMPILKAN PRODUK ======================
        cur.execute("""
            SELECT id_produk, nama_produk, grade, stok
            FROM produk_kakao
            WHERE is_delete = FALSE ORDER BY id_produk
        """)
        produk_data = cur.fetchall()

        if not produk_data:
            print("Belum ada produk untuk transaksi.")
            input("Tekan Enter...")
            return

        harga_grade = {'A': 62500, 'B': 56000, 'C': 49000}
        table_display = []

        for item in produk_data:
            pid, nama, grade, stok = item
            harga_display = f"Rp {harga_grade[grade.upper()]:,}".replace(",", ".")
            table_display.append([pid, nama, grade, stok, harga_display])

        print(tabulate(
            table_display,
            headers=["ID", "Nama Produk", "Grade", "Stok", "Harga/kg (Rp)"],
            tablefmt="psql"
        ))

        # ====================== PILIH PRODUK ======================
        while True:
            id_produk = input("\nMasukkan ID Produk: ").strip()
            if id_produk.lower() == "exit":
                return
            if id_produk.isdigit():
                id_produk = int(id_produk)
                break
            print("Masukkan angka ID yang valid!")

        cur.execute("SELECT grade, stok FROM produk_kakao WHERE id_produk=%s", (id_produk,))
        row = cur.fetchone()
        if not row:
            print("Produk tidak ditemukan!")
            input("Tekan Enter...")
            return
        
        grade_produk = row[0].upper()
        stok_produk = row[1]
        harga_satuan = harga_grade[grade_produk]

        # ====================== BERAT ======================
        while True:
            berat_str = input("Berat Biji (kg): ").strip()
            if berat_str.lower() == "exit":
                return
            try:
                berat = float(berat_str)
                if berat > 0:
                    break
                print("Berat harus > 0!")
            except:
                print("Masukkan angka yang valid!")

        jumlah = int(berat)
        subtotal = jumlah * harga_satuan

        # ====================== JENIS TRANSAKSI ======================
        if admin_mode:
            jenis = input_choice("Jenis Transaksi", ['pembelian', 'penjualan'])
        else:
            jenis = "penjualan" if role == "petani" else "pembelian"

        id_user = current_user_id

        status_bayar = "Pending"
        metode_bayar = "Belum Ditentukan"

        # ====================== CEK STOK UNTUK PEMBELIAN ======================
        if jenis == "pembelian":
            if jumlah > stok_produk:
                print(f"\n❌ Stok tidak cukup! Stok tersedia hanya {stok_produk} kg.")
                input("Tekan Enter...")
                return

        # ====================== PEMBAYARAN UNTUK PEMBELI ======================
        if jenis == "pembelian":
            print(f"\nTotal harus dibayar: Rp {subtotal:,}".replace(",", "."))
            while True:
                uang_str = input("Masukkan jumlah uang: ").replace(".", "").strip()
                if uang_str.lower() == "exit":
                    return
                if uang_str.isdigit():
                    uang_pembeli = int(uang_str)
                    break
                print("Masukkan angka yang valid!")

            if uang_pembeli >= subtotal:
                status_bayar = "Lunas"
                metode_bayar = input_choice("Metode Pembayaran", ["tunai", "transfer bank"])
                print("\nPembayaran LUNAS ✔")
            else:
                status_bayar = "Hutang"
                metode_bayar = "Belum Ditentukan"
                print("\nPembayaran tidak cukup → status: HUTANG ")

        # ====================== INSERT TRANSAKSI ======================
        cur.execute("""
            INSERT INTO transaksi (tanggal_transaksi, berat_biji, grade_mutu, 
                                   harga_satuan, id_user, jenis_transaksi)
            VALUES (CURRENT_DATE, %s, %s, %s, %s, %s)
            RETURNING id_transaksi
        """, (berat, grade_produk, harga_satuan, id_user, jenis))
        
        id_transaksi = cur.fetchone()[0]

        cur.execute("""
            INSERT INTO detail_transaksi (jumlah, harga_satuan_kg, subtotal, id_produk, id_transaksi)
            VALUES (%s, %s, %s, %s, %s)
        """, (jumlah, harga_satuan, subtotal, id_produk, id_transaksi))

        # ====================== INSERT PEMBAYARAN ======================
        cur.execute("""
            INSERT INTO pembayaran (metode_pembayaran, status, id_transaksi)
            VALUES (%s, %s, %s)
        """, (metode_bayar.title(), status_bayar.title(), id_transaksi))

        # ====================== UPDATE STOK ======================
        if jenis == "penjualan":
            cur.execute("UPDATE produk_kakao SET stok = stok + %s WHERE id_produk=%s", (jumlah, id_produk))
            print(f"\nPetani menerima uang: Rp {subtotal:,}".replace(",", "."))

        elif jenis == "pembelian":
            # stok sudah dipastikan cukup
            cur.execute("UPDATE produk_kakao SET stok = stok - %s WHERE id_produk=%s", (jumlah, id_produk))

        conn.commit()
        print("\nTransaksi berhasil disimpan!")

    except Exception as e:
        conn.rollback()
        print("ERROR:", e)

    finally:
        cur.close()
        conn.close()
        input("\nTekan Enter untuk kembali...")

# ----------------- laporan -----------------
def laporan_rekap():
    clear()
    print("====================================")
    print("            LAPORAN REKAP           ")
    print("====================================")

    conn = connectDB()
    if conn is None:
        input("Tekan Enter...")
        return
    cur = conn.cursor()
    try:
        # Total Pembelian
        cur.execute("""
            SELECT COALESCE(SUM(dt.subtotal), 0)
            FROM transaksi t
            JOIN detail_transaksi dt ON t.id_transaksi = dt.id_transaksi
            WHERE t.jenis_transaksi = 'pembelian'
        """)
        total_pembelian = cur.fetchone()[0] or 0

        # Total Penjualan
        cur.execute("""
            SELECT COALESCE(SUM(dt.subtotal), 0)
            FROM transaksi t
            JOIN detail_transaksi dt ON t.id_transaksi = dt.id_transaksi
            WHERE t.jenis_transaksi = 'penjualan'
        """)
        total_penjualan = cur.fetchone()[0] or 0

        # Total Stok Produk
        cur.execute("SELECT COALESCE(SUM(stok), 0) FROM produk_kakao WHERE is_delete = FALSE")
        total_stok = cur.fetchone()[0] or 0

        data = [(format_rp(total_pembelian), format_rp(total_penjualan), f"{total_stok} Kg")]

        print("\nRingkasan Keuangan dan Stok:")
        print(tabulate(data, headers=["Total Pembelian", "Total Penjualan", "Total Stok"], tablefmt="psql"))
    except Exception:
        print("Gagal menampilkan laporan.")
    finally:
        cur.close()
        conn.close()
        input("Tekan Enter untuk kembali...")



# ----------------- pembayaran -----------------
def kelola_pembayaran():
    clear()
    print("======================================")
    print("            KELOLA PEMBAYARAN         ")
    print("======================================")

    conn = connectDB()
    if conn is None:
        input("Tekan Enter...")
        return
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT p.id_pembayaran, p.metode_pembayaran, p.status, p.id_transaksi, t.jenis_transaksi
            FROM pembayaran p
            LEFT JOIN transaksi t ON p.id_transaksi = t.id_transaksi
            ORDER BY p.id_pembayaran DESC
        """)
        data = cur.fetchall()
        if not data:
            print("Belum ada data pembayaran.")
            input("Tekan Enter...")
            return
        print("\nData Pembayaran:")
        print(tabulate(data, headers=["ID Pembayaran", "Metode", "Status", "ID Transaksi", "Jenis Transaksi"], tablefmt="psql"))

        pilih = input("Masukkan ID Pembayaran yang akan diupdate (kosong = batal): ").strip()
        if pilih == "":
            return

        if not pilih.isdigit():
            print("ID pembayaran harus angka.")
            input("Tekan Enter...")
            return

        metode_baru = input_choice("Metode Baru", ['transfer bank', 'tunai'], default='transfer bank')
        status_baru = input_choice("Status Baru", ['hutang','lunas'], default='hutang')

        cur.execute("UPDATE pembayaran SET metode_pembayaran=%s, status=%s WHERE id_pembayaran=%s",
                    (metode_baru.title(), status_baru.title(), int(pilih)))
        conn.commit()
        print("Pembayaran berhasil diperbarui!")
    except Exception:
        conn.rollback()
        print("Gagal memperbarui pembayaran.")
    finally:
        cur.close()
        conn.close()
        input("Tekan Enter untuk kembali...")



# ----------------- lihat riwayat untuk petani atau pembeli -----------------
def lihat_riwayat(id_user):
    clear()
    print("====================================")
    print("           RIWAYAT TRANSAKSI        ")
    print("====================================")
    conn = connectDB()
    if conn is None:
        input("Tekan Enter...")
        return
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT t.id_transaksi, t.tanggal_transaksi, t.jenis_transaksi, dt.jumlah, dt.harga_satuan_kg, dt.subtotal, p.nama_produk
            FROM transaksi t
            JOIN detail_transaksi dt ON t.id_transaksi = dt.id_transaksi
            JOIN produk_kakao p ON dt.id_produk = p.id_produk
            WHERE t.id_user = %s
            ORDER BY t.tanggal_transaksi DESC
        """, (id_user,))
        rows = cur.fetchall()
        if not rows:
            print("Belum ada riwayat transaksi.")
        else:
            rows_fmt = []
            for r in rows:
                rows_fmt.append((r[0], r[1].isoformat(), r[2], r[6], r[3], format_rp(r[4]), format_rp(r[5])))
            print(tabulate(rows_fmt, headers=["ID","Tanggal","Jenis","Produk","Jumlah(Kg)","Harga/Kg","Subtotal"], tablefmt="psql"))
    except Exception:
        print("Gagal mengambil riwayat.")
    finally:
        cur.close()
        conn.close()
        input("Tekan Enter untuk kembali...")



# -------------------- menu admin --------------------
def menu_admin(user):
    while True:
        clear()
        print("=================================")
        print("        MENU ADMIN AGROCOCOA     ")
        print("=================================")
        print("1. Lihat Produk Kakao")
        print("2. Tambah Produk")
        print("3. Update Produk")
        print("4. Hapus Produk")
        print("5. Input Transaksi (Admin Mode)")
        print("6. Kelola Pembayaran")
        print("7. Laporan Rekap")
        print("x. Logout")

        pilihan = input("\nMasukkan pilihan: ").strip()
        if pilihan == '1':
            lihat_produk()
        elif pilihan == '2':
            tambah_produk()
        elif pilihan == '3':
            update_produk()
        elif pilihan == '4':
            hapus_produk()
        elif pilihan == '5':
            input_transaksi(admin_mode=True, current_user_id=user['id'])
        elif pilihan == '6':
            kelola_pembayaran()
        elif pilihan == '7':
            laporan_rekap()
        elif pilihan.lower() == 'x':
            break
        else:
            print("Pilihan tidak valid.")
            input("Tekan Enter...")



# ----------------------- menu petani ------------------------
def menu_petani(user):
    while True:
        clear()
        print("=================================")
        print("            MENU PETANI          ")
        print("=================================")
        print("1. Lihat Produk Kakao yang Tersedia di Koperasi")
        print("2. Setor Panen")
        print("3. Lihat Riwayat Setoran")
        print("x. Logout")

        pilih = input("\nMasukkan pilihan: ").strip()

        if pilih == "1":
            lihat_produk()

        elif pilih == "2":
            # PETANI → otomatis jenis = penjualan
            input_transaksi(
                admin_mode=False, current_user_id=user['id'], role="petani")

        elif pilih == "3":
            lihat_riwayat(user['id'])

        elif pilih.lower() == "x":
            break

        else:
            print("Pilihan tidak valid!")
            input("Tekan Enter...")



# --------------------- menu pembeli ----------------------
def menu_pembeli(user):
    while True:
        clear()
        print("=================================")
        print("           MENU PEMBELI          ")
        print("=================================")
        print("1. Lihat Daftar Produk Kakao")
        print("2. Beli Produk")
        print("3. Riwayat Pembelian")
        print("x. Logout")

        pilihan = input("\nMasukkan pilihan: ").strip().lower()

        
        #Lihat Produk
        if pilihan == "1":
            lihat_produk()
            input("\nTekan Enter untuk kembali...")

        
        #Beli Produk
        elif pilihan == "2":
            input_transaksi(admin_mode=False, current_user_id=user['id'], role='pembeli')

            input("\nTekan Enter untuk kembali...")

        #Lihat Riwayat Pembelian
        elif pilihan == "3":
            lihat_riwayat(user["id"])
            input("\nTekan Enter untuk kembali...")

        # LOGOUT
        elif pilihan == "x":
            break

        else:
            print("\nPilihan tidak valid!")
            input("Tekan Enter untuk melanjutkan...")



# --------------------- menu utama ----------------------
def menu_utama():
    while True:
        clear()
        print('==========================================')
        print('        SELAMAT DATANG DI AGROCOCOA       ')
        print('==========================================')
        print('1. Registrasi Akun')
        print('2. Login')
        print('3. Keluar')

        pilih = input('Masukkan Pilihan : ').strip()
        if pilih == '1':
            registrasi()
        elif pilih == '2':
            user = login()
            if user:
                if user['role'] == 'admin':
                    menu_admin(user)
                elif user['role'] == 'petani':
                    menu_petani(user)
                elif user['role'] == 'pembeli':
                    menu_pembeli(user)
        elif pilih.lower() == '3':
            print('Keluar dari sistem...')
            break
        else:
            print('Inputan Invalid')
            input("Tekan Enter...")

if __name__ == "__main__":
    # hanya untuk testing koneksi awal
    conn = connectDB()
    if conn:
        conn.close()
    menu_utama()

