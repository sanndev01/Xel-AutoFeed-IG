from pathlib import Path

from core.queue import muat_antrean
from core.ui import hijau, kuning, merah, redup

TANDA = {
    "menunggu": redup("○"),
    "mengunggah": kuning("◐"),
    "terunggah": hijau("✓"),
    "gagal": merah("✗"),
}


def tampilkan_antrean(folder_hasil: str | Path) -> None:
    try:
        _, data = muat_antrean(folder_hasil)
    except (FileNotFoundError, ValueError):
        print("Antrean belum ditemukan.")
        return

    print("\n=== ANTREAN UPLOAD ===")
    print(f"Folder : {Path(folder_hasil).name}")
    print(f"Status : {data['status']}")
    print(f"Total  : {data['total']}")
    print(f"Dibuat : {data['dibuat_pada']}")
    print("\nDaftar foto:")

    for item in data["items"]:
        print(
            f"{TANDA.get(item['status'], '?')} "
            f"{item['nomor']:02d}. {Path(item['file']).name}"
        )
