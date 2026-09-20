from pathlib import Path
from datetime import datetime

from core.queue import muat_antrean, simpan_antrean


def review_antrean(folder_hasil: str | Path) -> bool:
    try:
        file_antrean, data = muat_antrean(folder_hasil)
    except (FileNotFoundError, ValueError) as error:
        print(f"✗ {error}")
        return False

    items = data.get("items", [])

    if not items:
        print("✗ Antrean kosong.")
        return False

    if data["status"] in {"sebagian", "selesai"}:
        print(f"Antrean berstatus '{data['status']}', tidak perlu review ulang.")
        return False

    print("\n=== REVIEW ANTREAN UPLOAD ===")
    print(f"Total foto: {len(items)}")

    preview = Path(folder_hasil).expanduser() / "preview.jpg"
    if preview.is_file():
        print(f"Preview   : {preview}")
        print("(Buka preview di galeri untuk cek hasil crop.)")

    print()
    for item in items:
        print(f"{item['nomor']:02d}. {Path(item['file']).name}")

    pilihan = input("\nSetujui antrean ini? [y/N]: ").strip().lower()

    if pilihan in {"y", "ya"}:
        data["status"] = "disetujui"
        data["disetujui_pada"] = datetime.now().isoformat(timespec="seconds")
        pesan, hasil = "✓ Antrean disetujui dan disimpan.", True
    else:
        data["status"] = "menunggu_review"
        data.pop("disetujui_pada", None)
        pesan, hasil = "Antrean dikembalikan ke status menunggu_review.", False

    simpan_antrean(file_antrean, data)
    print(pesan)
    return hasil


def batalkan_persetujuan(folder_hasil: str | Path) -> bool:
    try:
        file_antrean, data = muat_antrean(folder_hasil)
    except (FileNotFoundError, ValueError) as error:
        print(f"✗ {error}")
        return False

    if data.get("status") != "disetujui":
        print("Antrean belum berstatus disetujui.")
        return False

    data["status"] = "menunggu_review"
    data.pop("disetujui_pada", None)
    simpan_antrean(file_antrean, data)

    print("✓ Persetujuan antrean dibatalkan.")
    return True
