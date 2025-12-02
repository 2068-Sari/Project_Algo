
import psycopg2 
import os #dipakai untuk menjalankan perintah clear screen
from tabulate import tabulate #untuk menampilkan data dalam bentuk tabel rapi

DB_CONFIG = {  #Dictionary ini menyimpan konfigurasi database yang diperlukan
    "host": "localhost",
    "user": "postgres",
    "password": "saripane*28",
    "port": "2809",
    "database": "Cocoa"
}
def clear():
    os.system('cls' if os.name == 'nt' else 'clear') #cls untuk Windows
def connectDB():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print("Gagal terhubung ke database:", e)
        return None
# Helper input
def input_nonempty(prompt, maxlen=None): #Meminta input dari user yang tidak boleh kosong.
                                            #Ada validasi maksimal panjang karakter.
    while True:
        v = input(prompt).strip()
        if v == "":
            print("Input tidak boleh kosong.")
            continue
        if maxlen and len(v) > maxlen:
            print(f"Input terlalu panjang (maks {maxlen} karakter).")
            continue
        return v

def input_digits(prompt, maxlen=None): #Meminta input hanya angka.
    while True:
        v = input(prompt).strip()
        if not v.isdigit():
            print("Masukkan hanya angka.")
            continue
        if maxlen and len(v) > maxlen:
            print(f"Input terlalu panjang (maks {maxlen} digit).")
            continue
        return v

def input_choice(prompt, choices, default=None): #Menampilkan pilihan yang tersedia
    choices_str = "/".join(choices)
    while True:
        v = input(f"{prompt} ({choices_str}){' [default:'+str(default)+']' if default else ''}: ").strip().lower()
        if v == "" and default is not None:
            return default
        if v in choices:
            return v
        print("Pilihan tidak valid.")

def format_rp(amount): #Mengubah angka menjadi format rupiah
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
        print('        REGISTRASI        ')
        print('==============================')
        print("Catatan: Ketik 0 kapan saja untuk kembali.\n")

        username = input_nonempty("Username: ", maxlen=50)
        if username == "0":
            return

        password = input_nonempty("Password: ", maxlen=100)
        if password == "0":
            return

        nama = input_nonempty("Nama Lengkap: ", maxlen=150)
        if nama == "0":
            return

        while True:
            print("\nPilih Role:") #User memilih jenis role akun.
            print("1. Petani")
            print("2. Pembeli")
            print("0. Kembali")

            role_input = input_choice("Masukkan Pilihan Role", ['1', '2', '0'])
            if role_input == "0":
                return
            if role_input in ["1", "2"]:
                break

        role = 'petani' if role_input == '1' else 'pembeli'

        no_telp = input_digits("No. Telepon: ", maxlen=15) #no tepl maksimal 15 digit
        if no_telp == "0":
            return

        detail_alamat = input_nonempty("Detail Alamat: ", maxlen=150)
        if detail_alamat == "0":
            return

        conn = connectDB()
        if conn is None:
            input("Tekan Enter untuk kembali...")
            return

        cur = conn.cursor()
        try:                #Mengambil daftar desa lengkap beserta kecamatan & kabupaten
                            #Jika tidak ada data desa maka tidak bisa registrasi.
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
            print(tabulate(desa_data, headers=["ID Desa", "Desa", "Kecamatan", "Kabupaten"], tablefmt="psql"))

            while True:
                id_desa = input_digits("\nMasukkan ID Desa Anda: ") #User wajib memilih ID desa.
                if id_desa == "0":
                    return
                cur.execute("SELECT 1 FROM desa WHERE id_desa=%s", (id_desa,))
                if cur.fetchone() is not None:
                    break
                else:
                    print("ID Desa tidak ditemukan. Coba lagi.")
                    input("Tekan Enter...")

            try:
                cur.execute("""
                    INSERT INTO users (users, passwords, nama_lengkap, role_user,
                                       no_telp, detail_alamat, id_desa)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (username, password, nama, role, no_telp, detail_alamat, id_desa))
                conn.commit() #Data lengkap user dimasukkan ke tabel users
                print("\nAkun berhasil dibuat!")
                input("Tekan Enter untuk kembali ke menu...")
                break
            except Exception as e:
                conn.rollback()
                print("Gagal membuat akun! (Username mungkin sudah digunakan.)", e)
                input("Tekan Enter...")
        except Exception as e:
            print("Terjadi masalah saat proses registrasi.", e)
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
            return None

        if username == "":
            print("Username tidak boleh kosong.")
            input("Tekan Enter...")
            continue

        password = input("Password : ").strip()
        if password.lower() == 'x':
            return None

        if password == "":
            print("Password tidak boleh kosong.")
            input("Tekan Enter...")
            continue

        conn = connectDB()
        if conn is None:
            input("Tekan Enter...")
            return None

        cur = conn.cursor()
        try:            #Cek apakah username & password cocok.

                        #Jika tidak ditemukan → tampilkan pesan salah & ulangi.
            cur.execute("""
                SELECT id_user, nama_lengkap, role_user 
                FROM users 
                WHERE users=%s AND passwords=%s
            """, (username, password))
            user = cur.fetchone()

            if not user:
                print("Username atau password salah! Silakan coba lagi.")
                input("Tekan Enter...")
                continue

            data_user = {"id": user[0], "nama": user[1], "role": user[2]}
            print(f"\nLogin berhasil! Selamat datang {data_user['nama']}")
            input("Tekan Enter untuk melanjutkan...")
            return data_user
        except Exception as e:
            print("Gagal proses login. Coba lagi.", e)
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
        if show_deleted:
            cur.execute("""
                SELECT id_produk, COALESCE(nama_produk, 'Kakao') AS nama_produk,
                       COALESCE(nama_grade, '') AS nama_grade, stok, deskripsi, is_delete
                FROM produk 
                ORDER BY id_produk
            """) #Tampilkan semua produk.
        else:
            cur.execute("""
                SELECT id_produk, COALESCE(nama_produk, 'Kakao') AS nama_produk,
                       COALESCE(nama_grade, '') AS nama_grade, stok, deskripsi
                FROM produk
                WHERE is_delete = FALSE
                ORDER BY id_produk
            """) #Tampilkan hanya produk aktif.
        data = cur.fetchall()
        if not data:
            print("Belum ada produk.")
            input("Tekan Enter...")
            return []

        # Menentukan harga berdasarkan grade
        harga_grade = {'A': 62500, 'B': 56000, 'C': 49000}

        table_data = []
        for row in data:
            id_produk, nama_produk, nama_grade, stok, deskripsi = row[:5]
            harga = harga_grade.get((nama_grade or '').upper(), 0)  #Jika grade kosong → harga = 0.
            table_data.append([id_produk, nama_produk, nama_grade, stok, format_rp(harga)])

        print(tabulate(table_data, headers=["ID", "Nama Produk", "Grade", "Stok (Kg)", "Harga/Kg (Rp)"], tablefmt="psql"))
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

        nama_produk = input("Nama Produk (kosong = 'Kakao'): ").strip()
        if nama_produk.lower() == "x":
            return

        nama_grade = input_choice("Grade", ['a','b','c','x']).upper()
        if nama_grade.lower() == "x":
            return

        stok = input_digits("Stok Produk  : ")
        if stok.lower() == "x":
            return

        deskripsi = input("Deskripsi (opsional): ").strip()

        conn = connectDB()
        if conn is None:
            input("Tekan Enter...")
            return

        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO produk (nama_produk, nama_grade, stok, deskripsi, is_delete)
                VALUES (%s, %s, %s, %s, FALSE) 
            """, (nama_produk or None, nama_grade, float(stok), deskripsi or None))
            conn.commit() #is_delete selalu FALSE saat produk baru dibuat.
            print("\nProduk berhasil ditambahkan!")
        except Exception as e:
            conn.rollback()
            print("Gagal menambah produk.", e)
        finally:
            cur.close()
            conn.close()
        input("Tekan Enter untuk kembali...")
        return

# -------------------- update produk ---------------------
def update_produk(): #Digunakan untuk mengubah data produk yang sudah ada.
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
            cur.execute("SELECT id_produk, COALESCE(nama_produk,'Kakao'), COALESCE(nama_grade,''), stok FROM produk WHERE is_delete = FALSE ORDER BY id_produk")
            rows = cur.fetchall()
            if not rows:
                print("Belum ada produk.")
                input("Tekan Enter...")
                return

            print(tabulate(rows, headers=["ID", "Nama", "Grade", "Stok"], tablefmt="psql"))

            idp = input("\nMasukkan ID produk yang ingin diupdate (X untuk kembali): ").strip()
            if idp.lower() == "x":
                return

            if not idp.isdigit():
                print("ID harus berupa angka!")
                input("Tekan Enter...")
                continue
            idp = int(idp)

            cur.execute("SELECT 1 FROM produk WHERE id_produk=%s AND is_delete=FALSE", (idp,))
            if cur.fetchone() is None:
                print("Produk tidak ditemukan.")
                input("Tekan Enter...")
                continue

            nama_baru = input_nonempty("Nama Produk Baru : ", maxlen=150)
            if nama_baru.lower() == "x":
                return

            grade_baru = input_choice("Grade Baru", ['a','b','c','x']).upper()
            if grade_baru.lower() == "x":
                return

            stok_baru = input_digits("Stok Baru        : ")
            if stok_baru.lower() == 'x':
                return

            deskripsi_baru = input("Deskripsi Baru (opsional): ").strip()

            cur.execute("""
                UPDATE produk
                SET nama_produk=%s, nama_grade=%s, stok=%s, deskripsi=%s
                WHERE id_produk=%s
            """, (nama_baru, grade_baru, float(stok_baru), deskripsi_baru or None, idp)) #Update ke database
            conn.commit()
            print("\nProduk berhasil diupdate!")
        except Exception as e:
            conn.rollback()
            print("Gagal update produk.", e)
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
            cur.execute("SELECT id_produk, COALESCE(nama_produk,'Kakao') FROM produk WHERE is_delete = FALSE ORDER BY id_produk")
            rows = cur.fetchall() #Tampilkan daftar produk yang belum dihapus
            if not rows:
                print("Belum ada produk.")
                input("Tekan Enter...")
                return

            print(tabulate(rows, headers=["ID", "Nama"], tablefmt="psql"))

            idp = input("\nMasukkan ID produk yang ingin dihapus (X untuk kembali): ").strip()
            if idp.lower() == "x":
                return

            if not idp.isdigit():
                print("ID harus angka!")
                input("Tekan Enter...")
                continue
            idp = int(idp)

            cur.execute("SELECT 1 FROM produk WHERE id_produk=%s AND is_delete=FALSE", (idp,))
            if cur.fetchone() is None:
                print("Produk tidak ditemukan atau sudah dihapus.")
                input("Tekan Enter...")
                continue

            confirm = input_choice("Yakin ingin menghapus produk? (y/n)", ['y','n'], default='n')
            if confirm == 'y': #Konfirmasi penghapusan y= yakin menghapus
                cur.execute("UPDATE produk SET is_delete = TRUE WHERE id_produk=%s", (idp,))
                conn.commit()
                print("Produk berhasil dihapus")
            else: # n = batal menghapus produk
                print("Penghapusan dibatalkan.")
        except Exception as e:
            conn.rollback()
            print("Gagal menghapus produk.", e)
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
        # Ambil data produk untuk ditampilkan
        cur.execute("""
            SELECT id_produk, COALESCE(nama_produk,'Kakao') AS nama_produk, COALESCE(nama_grade,'') AS nama_grade, stok
            FROM produk
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
            harga_display = f"Rp {harga_grade.get((grade or '').upper(), 0):,}".replace(",", ".")
            table_display.append([pid, nama, grade, stok, harga_display])

        print(tabulate(table_display, headers=["ID", "Nama Produk", "Grade", "Stok", "Harga/kg (Rp)"], tablefmt="psql"))

        if role == "pembeli" and not admin_mode: #mode pembeli
            keranjang = []
            while True:
                # Pembeli memilih produk, harus angka dan ada didatbase
                id_produk = input("\nMasukkan ID Produk (atau ketik 'done' jika selesai menambah): ").strip()
                if id_produk.lower() == "exit":
                    return
                if id_produk.lower() == "done":
                    break
                if not id_produk.isdigit():
                    print("Masukkan angka ID yang valid!")
                    continue
                id_produk = int(id_produk)

                cur.execute("SELECT nama_produk, nama_grade, stok FROM produk WHERE id_produk=%s", (id_produk,))
                row = cur.fetchone()
                if not row:
                    print("Produk tidak ditemukan!")
                    continue

                nama_produk, grade_produk, stok_produk = row
                grade_produk = (grade_produk or '').upper()
                harga_satuan = harga_grade.get(grade_produk, 0)

                # Input berat dengan validasi stok, Sistem mencegah pembeli membeli melebihi stok.
                while True:
                    berat_str = input("Berat Biji (kg): ").strip()
                    if berat_str.lower() == "exit":
                        return
                    try:
                        berat = float(berat_str)
                        if berat <= 0:
                            print("Berat harus > 0!")
                            continue
                        if berat > float(stok_produk):
                            print(f"\n❌ Stok tidak cukup! Stok yang tersedia hanya {stok_produk} kg.")
                            retry = input_choice("Coba masukkan berat lain? (y/n)", ["y", "n"])
                            if retry == "y":
                                continue
                            else:
                                berat = None
                                break
                        break
                    except:
                        print("Masukkan angka yang valid!")

                if berat is None:
                    # user memilih batal menambah item ini
                    continue

                subtotal = int(berat * harga_satuan)

                # Hitung subtotal & masukkan ke keranjang
                keranjang.append({
                    "id_produk": id_produk,
                    "nama": nama_produk,
                    "grade": grade_produk,
                    "berat": berat,
                    "harga": harga_satuan,
                    "subtotal": subtotal
                })
                print("Item ditambahkan ke keranjang.")

                # Tanyakan apakah ingin tambah item lain
                lanjut = input_choice("Tambah produk lain?", ["y", "n"])
                if lanjut == "n":
                    break

            # Jika keranjang kosong
            if len(keranjang) == 0:
                print("Keranjang kosong. Tidak ada transaksi.")
                input("Tekan Enter...")
                return

            # Tampilkan ringkasan keranjang
            print("\n========== KERANJANG ==========")
            keranjang_display = []
            total_bayar = 0
            for it in keranjang:
                keranjang_display.append([it["id_produk"], it["nama"], it["grade"], it["berat"], format_rp(it["harga"]), format_rp(it["subtotal"])])
                total_bayar += it["subtotal"]
            print(tabulate(keranjang_display, headers=["ID","Nama","Grade","Berat","Harga/kg","Subtotal"], tablefmt="psql"))
            print(f"\nTOTAL HARUS DIBAYAR: {format_rp(total_bayar)}")

            # Pembayaran 
            while True:
                uang_str = input("Masukkan jumlah uang (ketik 0 jika belum bayar): ").replace(".", "").strip()
                if uang_str.lower() == "exit":
                    return
                if uang_str.isdigit():
                    uang_pembeli = int(uang_str)
                    break
                print("Masukkan angka yang valid!")

            if uang_pembeli >= total_bayar: 
                status_pembayaran = "lunas"

                print("\nMetode Pembayaran:") 
                print("1. Tunai")
                print("2. Transfer Bank BRI")
                print("3. Transfer Bank BCA")

                while True:
                    metode_input = input("Pilih metode (1/2/3): ").strip()
                    if metode_input == "":
                        metode_bayar_choice = 1
                        break
                    if metode_input in ["1", "2", "3"]:
                        metode_bayar_choice = int(metode_input)
                        break
                    print("Masukkan pilihan yang valid!")

                print("\nPembayaran LUNAS ✔")

            elif uang_pembeli == 0:
                status_pembayaran = "hutang"
                metode_bayar_choice = None
                print("\nPembayaran belum dilakukan → status: HUTANG")

            else:
                status_pembayaran = "hutang"

                print("\nMetode Pembayaran (untuk mencatat jumlah yang dibayar):")
                print("1. Tunai")
                print("2. Transfer Bank BRI")
                print("3. Transfer Bank BCA")

                while True:
                    metode_input = input("Pilih metode (1/2/3): ").strip()
                    if metode_input == "":
                        metode_bayar_choice = 1
                        break
                    if metode_input in ["1", "2", "3"]:
                        metode_bayar_choice = int(metode_input)
                        break
                    print("Masukkan pilihan yang valid!")

                print("\nPembayaran kurang → status: HUTANG")

                sisa = total_bayar - uang_pembeli
                print(f"\n⚠ Kekurangan pembayaran Anda: {format_rp(sisa)}")
                print("Silakan melakukan pelunasan ke koperasi secara langsung atau melalui transfer.\n")
                print("Terimakasih sudah melakukan transaksi, tetapi transaksi masih dicatat sebagai Hutang")


            #Insert ke Table transaksi
            cur.execute("""
                INSERT INTO transaksi (tanggal, jenis_transaksi, status_transaksi, status_pembayaran, id_user)
                VALUES (CURRENT_DATE, %s, %s, %s, %s)
                RETURNING id_transaksi
            """, ("pembelian", "diproses", status_pembayaran, current_user_id))
            id_transaksi = cur.fetchone()[0]

            # Insert detail untuk setiap item + update stok per item
            for it in keranjang:
                cur.execute("""
                    INSERT INTO detail_transaksi (berat_kg, harga_satuan, subtotal, id_produk, id_transaksi)
                    VALUES (%s, %s, %s, %s, %s)
                """, (it["berat"], it["harga"], it["subtotal"], it["id_produk"], id_transaksi))

                # update stok (kurangi)
                cur.execute("UPDATE produk SET stok = stok - %s WHERE id_produk=%s", (it["berat"], it["id_produk"]))

            # Insert pembayaran 
            if uang_pembeli > 0:
                metode_map = {
                    'tunai': 1,
                    'transfer bank': 2,
                    'transfer bri': 2,
                    'transfer bca': 3
                }
                id_metode = metode_map.get(metode_bayar_choice, 1)
                cur.execute("""
                    INSERT INTO pembayaran (tanggal_bayar, nominal_bayar, id_transaksi, id_metode_pembayaran)
                    VALUES (CURRENT_DATE, %s, %s, %s)
                """, (uang_pembeli, id_transaksi, id_metode))

            conn.commit()
            print("\nTransaksi berhasil disimpan!")
            input("Tekan Enter untuk kembali...")
            return

        while True:
            id_produk = input("\nMasukkan ID Produk: ").strip()
            if id_produk.lower() == "exit":
                return
            if id_produk.isdigit():
                id_produk = int(id_produk)
                break
            print("Masukkan angka ID yang valid!")

        cur.execute("SELECT nama_grade, stok FROM produk WHERE id_produk=%s", (id_produk,))
        row = cur.fetchone()
        if not row:
            print("Produk tidak ditemukan!")
            input("Tekan Enter...")
            return

        grade_produk = (row[0] or '').upper()
        stok_produk = float(row[1])
        harga_satuan = harga_grade.get(grade_produk, 0)

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

        subtotal = int(berat * harga_satuan)

        if admin_mode:
            jenis = input_choice("Jenis Transaksi", ['pembelian', 'penjualan'])
        else:
            jenis = "penjualan" if role == "petani" else "pembelian"

        id_user = current_user_id

        status_pembayaran = "hutang"
        metode_bayar_choice = None
        uang_pembeli = 0

        if jenis == "pembelian":
            if berat > stok_produk:
                print(f"\n❌ Stok tidak cukup! Stok yang tersedia hanya {stok_produk} kg.")
                input("Tekan Enter...")
                return

            print(f"\nTotal harus dibayar: Rp {subtotal:,}".replace(",", "."))
            while True:
                uang_str = input("Masukkan jumlah uang (ketik 0 jika belum bayar): ").replace(".", "").strip()
                if uang_str.lower() == "exit":
                    return
                if uang_str.isdigit():
                    uang_pembeli = int(uang_str)
                    break
                print("Masukkan angka yang valid!")

            if uang_pembeli >= subtotal:
                status_pembayaran = "lunas"
                metode_bayar_choice = input_choice("Metode Pembayaran", ["tunai", "transfer bank"])
                print("\nPembayaran LUNAS ✔")
            elif uang_pembeli == 0:
                status_pembayaran = "hutang"
                metode_bayar_choice = None
                print("\nPembayaran belum dilakukan → status: HUTANG")
            else:
                status_pembayaran = "hutang"
                metode_bayar_choice = input_choice("Metode Pembayaran (untuk catatan jumlah bayar)", ["tunai", "transfer bank"])
                print("\nPembayaran kurang → status: HUTANG")


        cur.execute("""
            INSERT INTO transaksi (tanggal, jenis_transaksi, status_transaksi, status_pembayaran, id_user)
            VALUES (CURRENT_DATE, %s, %s, %s, %s)
            RETURNING id_transaksi
        """, (jenis, 'diproses', status_pembayaran, id_user))
        id_transaksi = cur.fetchone()[0]

        # Insert detail_transaksi (berat_kg, harga_satuan, subtotal, id_produk, id_transaksi)
        cur.execute("""
            INSERT INTO detail_transaksi (berat_kg, harga_satuan, subtotal, id_produk, id_transaksi)
            VALUES (%s, %s, %s, %s, %s)
        """, (berat, harga_satuan, subtotal, id_produk, id_transaksi))

        # Insert pembayaran jika ada pembayaran
        if uang_pembeli > 0:
            metode_map = {
                'tunai': 1,
                'transfer bank': 2,
                'transfer bri': 2,
                'transfer bca': 3
            }
            id_metode = metode_map.get(metode_bayar_choice, 1)
            cur.execute("""
                INSERT INTO pembayaran (tanggal_bayar, nominal_bayar, id_transaksi, id_metode_pembayaran)
                VALUES (CURRENT_DATE, %s, %s, %s)
            """, (uang_pembeli, id_transaksi, id_metode))

        # Update stok
        if jenis == "penjualan":
            # petani setor => stok bertambah
            cur.execute("UPDATE produk SET stok = stok + %s WHERE id_produk=%s", (berat, id_produk))
            print(f"\nPetani menerima uang: Rp {subtotal:,}".replace(",", "."))
        elif jenis == "pembelian":
            cur.execute("UPDATE produk SET stok = stok - %s WHERE id_produk=%s", (berat, id_produk))

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
    #minta input periode dalam format YYYY-MM
    bulan = input("Masukkan bulan dan tahun (contoh: 2025-11): ").strip()
    if not bulan:
        print("Bulan tidak boleh kosong")
        input("Tekan Enter...")
        return

    conn = connectDB()
    if conn is None:
        input("Tekan Enter...")
        return
    cur = conn.cursor()
    try:
       #Menghitung total pembelian & penjualan berdasarkan jenis transaksi.
        cur.execute("""
            SELECT 
                COALESCE(SUM(CASE WHEN t.jenis_transaksi='pembelian' THEN dt.subtotal ELSE 0 END),0) AS total_pembelian,
                COALESCE(SUM(CASE WHEN t.jenis_transaksi='penjualan' THEN dt.subtotal ELSE 0 END),0) AS total_penjualan,
                COALESCE(SUM(p.stok),0) AS total_stok
            FROM transaksi t
            JOIN detail_transaksi dt ON t.id_transaksi = dt.id_transaksi
            JOIN produk p ON dt.id_produk = p.id_produk
            WHERE TO_CHAR(t.tanggal,'YYYY-MM') = %s
        """, (bulan,)) #Menyaring berdasarkan bulan yang diinput.
        row = cur.fetchone()
        total_pembelian, total_penjualan, total_stok = row

        data = [(bulan, format_rp(total_pembelian), format_rp(total_penjualan), f"{total_stok} Kg")]
        print(tabulate(data, headers=["Periode","Total Pembelian","Total Penjualan","Total Stok"], tablefmt="psql"))

    except Exception as e:
        print("Gagal menampilkan laporan:", e)
    finally:
        cur.close()
        conn.close()
        input("Tekan Enter untuk kembali...")





# ----------------- kelola pembayaran -----------------
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
    try: #Menampilkan semua pembayaran
        cur.execute("""
            SELECT 
                p.id_pembayaran, 
                p.tanggal_bayar, 
                p.nominal_bayar,
                p.id_transaksi,
                t.status_pembayaran,
                mp.nama_metode, 
                mp.nama_bank
            FROM pembayaran p
            LEFT JOIN metode_pembayaran mp 
                ON p.id_metode_pembayaran = mp.id_metode_pembayaran
            LEFT JOIN transaksi t
                ON p.id_transaksi = t.id_transaksi
            ORDER BY p.id_pembayaran DESC
        """) #Mengambil seluruh pembayaran + join metode bayar + join transaksi.
        data = cur.fetchall()
        if not data:
            print("Belum ada data pembayaran.")
            input("Tekan Enter...")
            return

        print("\nData Pembayaran:")
        print(tabulate(data, 
            headers=["ID Pembayaran", "Tanggal", "Nominal", "ID Transaksi", "Status", "Metode", "Bank"], 
            tablefmt="psql"
        ))


        pilih = input("\nMasukkan ID Pembayaran yang akan diupdate (kosong = batal): ").strip()
        if pilih == "": #Jika kosong → batal.
            return
        
        if not pilih.isdigit():
            print("❌ ID pembayaran harus berupa angka!")
            input("Tekan Enter...")
            return
        
        pilih = int(pilih)

        # === VALIDASI ID PEMBAYARAN ADA DI DATABASE ===
        cur.execute("SELECT id_pembayaran FROM pembayaran WHERE id_pembayaran = %s", (pilih,))
        cek = cur.fetchone()
        if cek is None:
            print(f"❌ ID Pembayaran '{pilih}' tidak ditemukan!")
            print("Silakan masukkan ID yang benar.")
            input("Tekan Enter...")
            return

        # Jika valid → lanjut update
        nominal_baru = input_digits("Nominal baru: ")

        print("\nPilih metode pembayaran:")
        print("1. Tunai")
        print("2. Transfer Bank BRI")
        print("3. Transfer Bank BCA")

        metode_baru = input_choice("Pilih", ["1", "2", "3"])

        cur.execute("""
            UPDATE pembayaran
            SET nominal_bayar = %s, id_metode_pembayaran = %s
            WHERE id_pembayaran = %s
        """, (int(nominal_baru), int(metode_baru), pilih)) #Update database

        conn.commit()
        print("\n✔ Pembayaran berhasil diperbarui!")

    except Exception as e:
        conn.rollback()
        print("Gagal memperbarui pembayaran:", e)

    finally:
        cur.close()
        conn.close()
        input("Tekan Enter untuk kembali...")





# ----------------- lihat riwayat -----------------
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
            SELECT 
                t.id_transaksi,
                t.tanggal,
                t.jenis_transaksi,
                dt.berat_kg,
                dt.harga_satuan,
                dt.subtotal,
                COALESCE(pr.nama_produk, pr.nama_grade) AS produk_nama
            FROM transaksi t
            JOIN detail_transaksi dt ON t.id_transaksi = dt.id_transaksi
            JOIN produk pr ON dt.id_produk = pr.id_produk
            WHERE t.id_user = %s
            ORDER BY t.id_transaksi DESC, dt.id_detail ASC
        """, (id_user,)) #Menampilkan semua transaksi user (petani atau pembeli).
                        #diurutkan dari transaksi terbaruu

        
        rows = cur.fetchall()
        if not rows:
            print("Belum ada riwayat transaksi.")
        else:
            rows_fmt = []
            for r in rows:
                rows_fmt.append((r[0], r[1].isoformat(), r[2], r[6], r[3], format_rp(r[4]), format_rp(r[5])))
            print(tabulate(rows_fmt, headers=["ID","Tanggal","Jenis","Produk","Berat(Kg)","Harga/Kg","Subtotal"], tablefmt="psql"))
    except Exception as e:
        print("Gagal mengambil riwayat.", e)
    finally:
        cur.close()
        conn.close()
        input("Tekan Enter untuk kembali...")

# Menus
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
            input_transaksi(admin_mode=False, current_user_id=user['id'], role="petani")
        elif pilih == "3":
            lihat_riwayat(user['id'])
        elif pilih.lower() == "x":
            break
        else:
            print("Pilihan tidak valid!")
            input("Tekan Enter...")

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
        if pilihan == "1":
            lihat_produk()
        elif pilihan == "2":
            input_transaksi(admin_mode=False, current_user_id=user['id'], role='pembeli')
        elif pilihan == "3":
            lihat_riwayat(user["id"])
        elif pilihan == "x":
            break
        else:
            print("\nPilihan tidak valid!")
            input("Tekan Enter untuk melanjutkan...")

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
    conn = connectDB()
    if conn:
        conn.close()
    menu_utama()
