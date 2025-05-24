import os
import sqlite3

GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

EKSTRAK_DIR = "/storage/emulated/0/Download"

def tampilkan_header():
    header = r"""
 ▄▄▄▄    ██▓ ██▓     ██▓    
▓█████▄ ▓██▒▓██▒    ▓██▒    
▒██▒ ▄██▒██▒▒██░    ▒██░    
▒██░█▀  ░██░▒██░    ▒██░    
░▓█  ▀█▓░██░░██████▒░██████▒
░▒▓███▀▒░▓  ░ ▒░▓  ░░ ▒░▓  ░
▒░▒   ░  ▒ ░░ ░ ▒  ░░ ░ ▒  ░
 ░    ░  ▒ ░  ░ ░     ░ ░   
 ░       ░      ░  ░    ░  ░
      ░                     
ALFAMART PEDULI | SCRIPT BY BILL
    -= [ 0851 8666 0986 ]=-
________________________________
    """
    print(f"{GREEN}{header}{RESET}")

def arsip_berisi_db(tool, filepath):
    try:
        output = os.popen(f'{tool} -l "{filepath}"').read()
        return any(".db" in line.lower() for line in output.splitlines())
    except:
        return False

def periksa_dan_ekstrak_arsip(download_path='/storage/emulated/0/Download'):
    for dirpath, _, filenames in os.walk(download_path):
        for file in filenames:
            path_file = os.path.join(dirpath, file)
            nama_lc = file.lower()

            if nama_lc.endswith('_android.zip') and arsip_berisi_db("unzip", path_file):
                print(f"{YELLOW}Ekstrak ZIP: {file}{RESET}")
                os.system(f'unzip -o "{path_file}" -d "{EKSTRAK_DIR}"')

            elif nama_lc.endswith('_android.rar') and arsip_berisi_db("unrar", path_file):
                print(f"{YELLOW}Ekstrak RAR: {file}{RESET}")
                os.system(f'unrar x -o+ "{path_file}" "{EKSTRAK_DIR}/"')

            elif nama_lc.endswith('_android.7z') and arsip_berisi_db("7z", path_file):
                print(f"{YELLOW}Ekstrak 7Z: {file}{RESET}")
                os.system(f'7z x "{path_file}" -o"{EKSTRAK_DIR}" -y')

def cari_semua_db_di_folder(path):
    hasil = []
    for dirpath, _, filenames in os.walk(path):
        for file in filenames:
            if file.endswith('_android.db'):
                hasil.append(os.path.join(dirpath, file))
    return hasil

def cari_file_db_lokal():
    return cari_semua_db_di_folder('/storage/emulated/0/Download')

def tampilkan_menu_file(file_list):
    print(f"{GREEN}\nDitemukan beberapa file database:{RESET}")
    for i, file in enumerate(file_list, start=1):
        print(f"{i}. {file}")
    pilihan = input(f"{GREEN}\nPilih nomor file yang ingin dipakai: ").strip()
    if pilihan.isdigit() and 1 <= int(pilihan) <= len(file_list):
        return file_list[int(pilihan) - 1]
    print("Pilihan tidak valid.")
    return None

def jalankan_query(db_path):
    query = """
    WITH 
      first_row AS (
        SELECT date_tx, user_id FROM tx_tsale ORDER BY rowid LIMIT 1
      ),
      total_value AS (
        SELECT CAST(ROUND(SUM(total_faktur - discount - card - voucher - cash_out - wallet - refund + charity + nom_topup)) AS INTEGER) AS total
        FROM tx_tsale
      ),
      formatted_total AS (
        SELECT 
          total,
          LENGTH(total) AS len,
          total AS tstr
        FROM total_value
      )
    SELECT 
      first_row.date_tx,
      first_row.user_id,
      'Rp ' || 
      CASE
        WHEN len <= 3 THEN tstr
        WHEN len <= 6 THEN 
          substr(tstr, 1, len - 3) || '.' || substr(tstr, -3)
        WHEN len <= 9 THEN 
          substr(tstr, 1, len - 6) || '.' ||
          substr(tstr, len - 5, 3) || '.' ||
          substr(tstr, len - 2, 3)
        ELSE tstr
      END AS formatted_total
    FROM first_row, formatted_total;
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchone()
        if result:
            print(f"\n{YELLOW}Tanggal : {result[0]}{RESET}")
            print(f"{YELLOW}NIK     : {result[1]}{RESET}")
            print(f"{YELLOW}Total   : {result[2]}{RESET}")
        else:
            print("Data tidak ditemukan.")
    except Exception as e:
        print("Kesalahan saat akses database:", e)
    finally:
        if conn:
            conn.close()

def main():
    tampilkan_header()
    print("Memindai arsip (_android.zip/rar/7z) dan mengekstrak jika berisi .db...")
    periksa_dan_ekstrak_arsip()
    print("Mencari file .db di penyimpanan lokal Download...")
    file_list = cari_file_db_lokal()

    if not file_list:
        print("Tidak ada file .db ditemukan.")
        return

    if len(file_list) == 1:
        db_path = file_list[0]
    else:
        db_path = tampilkan_menu_file(file_list)
        if not db_path:
            return

    print(f"{GREEN}Menjalankan query pada file:{RESET} {db_path}")
    jalankan_query(db_path)

if __name__ == '__main__':
    main()
