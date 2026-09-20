from pathlib import Path
import json
from datetime import datetime

# Status antrean : siap → disetujui → sebagian → selesai
# Status item    : menunggu → mengunggah → terunggah | gagal


def muat_antrean(folder_hasil: str | Path) -> tuple[Path, dict]:
    file_antrean = Path(folder_hasil).expanduser() / "queue.json"

    if not file_antrean.is_file():
        raise FileNotFoundError("queue.json tidak ditemukan.")

    try:
        return file_antrean, json.loads(file_antrean.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError("Format queue.json tidak valid.") from error


def simpan_antrean(file_antrean: Path, data: dict) -> None:
    file_antrean.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def path_item(folder_hasil: str | Path, item: dict) -> Path:
    """Lokasi file item (disimpan relatif supaya folder bisa dipindah)."""
    return Path(folder_hasil).expanduser() / item["file"]


def buat_antrean(folder_hasil: str | Path) -> Path:
    folder_hasil = Path(folder_hasil).expanduser()
    folder_upload = folder_hasil / "upload_order"

    if not folder_upload.is_dir():
        raise FileNotFoundError(f"Folder upload tidak ditemukan: {folder_upload}")

    daftar_file = sorted(f for f in folder_upload.iterdir() if f.is_file())

    if not daftar_file:
        raise ValueError("Tidak ada foto untuk dimasukkan ke antrean.")

    antrean = {
        "dibuat_pada": datetime.now().isoformat(timespec="seconds"),
        "status": "siap",
        "total": len(daftar_file),
        "items": [
            {
                "nomor": nomor,
                "file": f"upload_order/{file.name}",
                "status": "menunggu",
            }
            for nomor, file in enumerate(daftar_file, start=1)
        ],
    }

    file_antrean = folder_hasil / "queue.json"
    simpan_antrean(file_antrean, antrean)
    return file_antrean
