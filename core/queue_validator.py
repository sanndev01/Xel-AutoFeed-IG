from pathlib import Path
from PIL import Image

from core.analyzer import KOLOM
from core.queue import muat_antrean, path_item


def validasi_hasil(folder_hasil: str | Path) -> bool:
    folder_upload = Path(folder_hasil).expanduser() / "upload_order"

    print("\n=== VALIDASI HASIL FOTO ===")

    if not folder_upload.is_dir():
        print("✗ Folder upload_order tidak ditemukan.")
        return False

    daftar = sorted(folder_upload.glob("*.jpg"))

    if not daftar or len(daftar) % KOLOM:
        print(f"✗ Jumlah potongan ({len(daftar)}) harus kelipatan {KOLOM}.")
        return False

    ukuran = set()

    for file_foto in daftar:
        try:
            with Image.open(file_foto) as gambar:
                ukuran.add(gambar.size)
                gambar.verify()
        except Exception:
            print(f"✗ File rusak: {file_foto.name}")
            return False

    if len(ukuran) != 1:
        print("✗ Ukuran potongan tidak seragam, grid tidak akan nyambung.")
        return False

    lebar, tinggi = ukuran.pop()
    print(f"✓ {len(daftar)} potongan valid ({lebar}×{tinggi}, {len(daftar) // KOLOM}×{KOLOM})")
    return True


def validasi_antrean(folder_hasil: str | Path) -> bool:
    print("\n=== VALIDASI ANTREAN ===")

    try:
        _, data = muat_antrean(folder_hasil)
    except (FileNotFoundError, ValueError) as error:
        print(f"✗ {error}")
        return False

    items = data.get("items", [])

    if not items:
        print("✗ Antrean kosong.")
        return False

    hilang = [i["file"] for i in items if not path_item(folder_hasil, i).is_file()]

    for nama in hilang:
        print(f"✗ File hilang: {Path(nama).name}")

    if not hilang:
        print(f"✓ Semua {len(items)} file antrean tersedia.")

    return not hilang
