from pathlib import Path
from datetime import datetime
import random
import time

from core.config import baca_config
from core.instagram import login
from core.queue import muat_antrean, simpan_antrean, path_item
from core.queue_validator import validasi_antrean
from core.ui import Spinner, bar, hitung_mundur, ketik, progress


def simulasi_upload(folder_hasil: str | Path) -> None:
    file_antrean, data = muat_antrean(folder_hasil)

    print("\n=== SIMULASI UPLOAD ===")
    print("Mode: DRY-RUN, tidak ada file yang diunggah.\n")

    berhasil = 0

    for nomor, item in enumerate(data["items"], start=1):
        file_foto = path_item(folder_hasil, item)
        time.sleep(0.05)

        if file_foto.is_file():
            berhasil += 1
            progress(nomor, data["total"], f"siap: {file_foto.name}")
        else:
            print(f"\n✗ File tidak ditemukan: {file_foto.name}")

    print(f"\nTotal siap diproses: {berhasil}/{data['total']}")


def upload_antrean(folder_hasil: str | Path) -> bool:
    """Upload item antrean berurutan ke Instagram; bisa dilanjutkan kalau terputus."""
    try:
        file_antrean, data = muat_antrean(folder_hasil)
    except (FileNotFoundError, ValueError) as error:
        print(f"✗ {error}")
        return False

    if data["status"] == "selesai":
        print("✓ Antrean ini sudah selesai diunggah.")
        return True

    if data["status"] not in {"disetujui", "sebagian"}:
        print("✗ Antrean belum disetujui. Jalankan Review antrean dulu.")
        return False

    if not validasi_antrean(folder_hasil):
        return False

    items = data["items"]

    # Item yang terputus di tengah upload mungkin sudah masuk ke profil. Tanya dulu,
    # karena upload ganda akan menggeser seluruh grid.
    for item in items:
        if item["status"] in {"mengunggah", "gagal"}:
            sudah = input(
                f"\nFoto {item['nomor']:02d} terputus di percobaan sebelumnya."
                "\nCek profil: apakah foto ini sudah muncul? [y/N]: "
            ).strip().lower()
            item.pop("error", None)
            item["status"] = "terunggah" if sudah in {"y", "ya"} else "menunggu"
            if item["status"] == "terunggah":
                item["catatan"] = "ditandai manual"

    simpan_antrean(file_antrean, data)
    sisa = [i for i in items if i["status"] != "terunggah"]

    if not sisa:
        data["status"] = "selesai"
        simpan_antrean(file_antrean, data)
        print("✓ Semua foto sudah terunggah.")
        return True

    username = baca_config()["instagram"].get("username", "")

    print("\n=== UPLOAD KE INSTAGRAM ===")
    print(f"Akun    : @{username}")
    print(f"Antrean : {Path(folder_hasil).name}")
    print(f"Sisa    : {len(sisa)} dari {len(items)} foto ({sisa[0]['nomor']:02d} → {sisa[-1]['nomor']:02d})")

    caption = input("Caption (kosong = tanpa caption): ").strip()

    if input(f"\nUnggah {len(sisa)} foto sekarang? [y/N]: ").strip().lower() not in {"y", "ya"}:
        print("Upload dibatalkan.")
        return False

    cl = login()
    if not cl:
        return False

    jeda_min, jeda_max = (baca_config()["upload"][k] for k in ("jeda_min", "jeda_max"))
    total = len(items)

    try:
        for indeks, item in enumerate(sisa):
            nomor = item["nomor"]
            file_foto = path_item(folder_hasil, item)

            # Tandai dulu: kalau proses mati di tengah, status ini yang ditanyakan saat resume
            item["status"] = "mengunggah"
            simpan_antrean(file_antrean, data)

            try:
                with Spinner(f"Mengunggah {nomor:02d}/{total:02d} {bar(nomor, total, 10)} {file_foto.name}"):
                    media = cl.photo_upload(file_foto, caption)
            except Exception as error:
                item["status"] = "gagal"
                item["error"] = f"{type(error).__name__}: {error}"[:300]
                data["status"] = "sebagian"
                simpan_antrean(file_antrean, data)
                print(f"\n✗ Upload berhenti di foto {nomor:02d}: {item['error']}")
                print("Urutan upload menentukan grid, jadi proses dihentikan.")
                print("Cek profil, lalu lanjutkan lewat menu Upload.")
                return False

            item["status"] = "terunggah"
            item["media_pk"] = str(getattr(media, "pk", ""))
            item["diunggah_pada"] = datetime.now().isoformat(timespec="seconds")
            data["status"] = "sebagian"
            simpan_antrean(file_antrean, data)

            if indeks < len(sisa) - 1:
                hitung_mundur(random.uniform(jeda_min, jeda_max), "Jeda anti-spam")

    except KeyboardInterrupt:
        print("\nDihentikan. Progres tersimpan, lanjutkan lewat menu Upload.")
        return False

    data["status"] = "selesai"
    data["selesai_pada"] = datetime.now().isoformat(timespec="seconds")
    simpan_antrean(file_antrean, data)

    ketik("✓ Semua foto terunggah. Cek grid di profil lo!")
    return True
