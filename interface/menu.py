import shutil
from pathlib import Path

from core.analyzer import KOLOM, MAKS_BARIS, analisis_foto, hitung_crop, ukuran_tile
from core.config import OUTPUT_DIR, baca_config
from core.cutter import gabung_hasil, potong_foto
from core.instagram import cek_koneksi_instagram, pengaturan_instagram
from core.queue import buat_antrean
from core.queue_validator import validasi_antrean, validasi_hasil
from core.queue_viewer import tampilkan_antrean
from core.reviewer import batalkan_persetujuan, review_antrean
from core.ui import (
    Spinner, banner, bar, hijau, kuning, merah, redup, tampilkan_menu_dengan_jeda,
)
from core.uploader import simulasi_upload, upload_antrean

DOWNLOAD_DIR = Path.home() / "storage" / "downloads"


def ya(pertanyaan: str, default: bool = True) -> bool:
    jawab = input(f"{pertanyaan} [{'Y/n' if default else 'y/N'}]: ").strip().lower()
    return default if jawab == "" else jawab in {"y", "ya"}


def pilih_foto(prompt: str = "Nama file / path foto (kosong = batal)") -> Path | None:
    while True:
        teks = input(f"\n{prompt}: ").strip().strip("'\"")

        if not teks:
            return None

        path = Path(teks).expanduser()

        if not path.is_absolute() and len(path.parts) == 1:
            path = DOWNLOAD_DIR / path

        if path.is_file():
            return path

        print(merah("✗ File tidak ditemukan. Coba lagi."))


def tampilkan_analisis(data: dict) -> None:
    tw, th = ukuran_tile()

    print("\n=== ANALISIS FOTO ===")
    print(f"Nama   : {Path(data['path']).name}")
    print(f"Ukuran : {data['lebar']} × {data['tinggi']} ({data['format']})")
    print(f"Tile   : {tw} × {th}, {KOLOM} kolom")
    print(redup("\n Baris  Post  Terpakai  Skala"))

    for baris in range(1, MAKS_BARIS + 1):
        skala, terpakai = hitung_crop(data["lebar"], data["tinggi"], baris)
        rekom = data["rekomendasi_baris"] == baris
        print(
            f" {'★' if rekom else ' '}{baris:>3}   {baris * KOLOM:>4}   {terpakai:>6.0%}"
            f"   {skala:>4.1f}×{' ↑' if skala > 1 else ''}"
        )

    print(redup("\nTerpakai = bagian foto yang tidak terpangkas. ↑ = diperbesar + enhance ringan."))


def pilih_baris(rekomendasi: int) -> int:
    while True:
        jawab = input(f"\nJumlah baris 1-{MAKS_BARIS} [Enter = {rekomendasi}]: ").strip()

        if jawab == "":
            return rekomendasi

        if jawab.isdigit() and 1 <= int(jawab) <= MAKS_BARIS:
            return int(jawab)

        print(merah("Masukkan angka yang valid."))


def pilih_fokus(lebar: int, tinggi: int, baris: int) -> float:
    """Tanya posisi crop hanya kalau foto memang terpangkas cukup banyak."""
    _, terpakai = hitung_crop(lebar, tinggi, baris)

    if terpakai > 0.95:
        return 0.5

    tw, th = ukuran_tile()
    samping = lebar / tinggi > (KOLOM * tw) / (baris * th)
    a, b = ("Kiri", "Kanan") if samping else ("Atas", "Bawah")

    print(kuning(f"\nFoto terpangkas {1 - terpakai:.0%} di sisi {a.lower()}/{b.lower()}."))
    jawab = input(f"Fokus crop: [1] {a}  [2] Tengah  [3] {b}  [Enter = tengah]: ").strip()

    return {"1": 0.0, "3": 1.0}.get(jawab, 0.5)


def peta_grid(bloks: list[int]) -> None:
    """Tampilan profil setelah upload; angka = urutan upload. bloks = jumlah baris tiap foto, atas → bawah."""
    total = sum(bloks) * KOLOM
    print("\nTampilan profil (angka = urutan upload):")
    r = 0
    for k, baris in enumerate(bloks, start=1):
        for i in range(baris):
            sel = " ".join(f"[{total - (r * KOLOM + c):02d}]" for c in range(KOLOM))
            print(f"  {sel}" + (f"   ← foto {k}" if len(bloks) > 1 and i == 0 else ""))
            r += 1


def atur_foto(foto: Path) -> tuple[Path, int, float] | None:
    """Analisis foto lalu tanya jumlah baris dan fokus crop. None jika foto tidak terbaca."""
    try:
        with Spinner("Menganalisis foto"):
            data = analisis_foto(foto)
    except Exception as error:
        print(merah(f"✗ Foto tidak bisa dibaca: {error}"))
        return None

    tampilkan_analisis(data)

    baris = pilih_baris(data["rekomendasi_baris"])
    skala, _ = hitung_crop(data["lebar"], data["tinggi"], baris)

    if skala > 2.5:
        print(kuning("⚠ Resolusi foto rendah untuk grid ini, hasil bisa terlihat buram."))

    return foto, baris, pilih_fokus(data["lebar"], data["tinggi"], baris)


def proses_potong(foto: Path, baris: int, fokus: float) -> Path | None:
    try:
        with Spinner("Menyiapkan mosaik (crop + resize)") as sp:
            return potong_foto(
                foto, baris, fokus,
                progress=lambda i, t: sp.ubah(f"Memotong {bar(i, t)} {i}/{t}"),
            )
    except (FileNotFoundError, ValueError, OSError) as error:
        print(merah(f"✗ Gagal memotong: {error}"))
        return None


def selesaikan(hasil: Path, bloks: list[int]) -> None:
    """Tampilkan hasil, validasi, lalu buat antrean."""
    print(hijau("\n✓ Pemotongan berhasil!"))
    print(f"Hasil   : {hasil}")
    print(f"Preview : {hasil / 'preview.jpg'}")
    peta_grid(bloks)

    if not validasi_hasil(hasil):
        print(merah("\n✗ Hasil tidak lolos validasi. Antrean upload tidak dibuat."))
        return

    try:
        print(hijau(f"\n✓ Antrean upload dibuat: {buat_antrean(hasil)}"))
        print(redup("Lanjut: Antrean Upload → Review → Upload ke Instagram."))
    except (FileNotFoundError, ValueError) as error:
        print(merah(f"\n✗ Gagal membuat antrean: {error}"))


def jalankan_pemotongan() -> None:
    foto = pilih_foto()
    pilihan = foto and atur_foto(foto)

    if not pilihan:
        return

    foto, baris, fokus = pilihan

    print(f"\nGrid: {baris}×{KOLOM} = {baris * KOLOM} post")
    if not ya("Mulai pemotongan?"):
        print("Pemotongan dibatalkan.")
        return

    hasil = proses_potong(foto, baris, fokus)
    if hasil:
        selesaikan(hasil, [baris])


def jalankan_pemotongan_bertumpuk() -> None:
    """Beberapa foto disusun vertikal di profil dan diupload sebagai satu antrean."""
    print("\nMasukkan foto dari yang paling ATAS di profil sampai paling BAWAH.")
    print(redup("Urutan upload diatur otomatis (foto paling bawah diunggah duluan)."))

    daftar = []

    while True:
        nomor = len(daftar) + 1
        label = f"Foto {nomor}" + (" (paling atas)" if nomor == 1 else "")
        akhir = "kosong = batal" if nomor == 1 else "kosong = selesai"
        foto = pilih_foto(f"{label}: nama file / path ({akhir})")

        if foto is None:
            break

        atur = atur_foto(foto)
        if atur:
            daftar.append(atur)

    if not daftar:
        return

    if len(daftar) < 2:
        print("Minimal 2 foto. Untuk satu foto pakai menu Potong Foto.")
        return

    bloks = [baris for _, baris, _ in daftar]
    total = sum(bloks) * KOLOM

    print("\n=== RINGKASAN ===")
    for nomor, (foto, baris, _) in enumerate(daftar, start=1):
        posisi = " (atas)" if nomor == 1 else " (bawah)" if nomor == len(daftar) else ""
        print(f"Foto {nomor}{posisi:<8}: {foto.name} → {baris} baris")
    print(f"Total {total} post")

    jeda = baca_config()["upload"]
    menit = round(total * (jeda["jeda_min"] + jeda["jeda_max"]) / 2 / 60)
    if total > 12:
        print(kuning(f"⚠ Cukup banyak untuk sekali jalan (±{menit} menit). Upload boleh dicicil:"))
        print(kuning("  Ctrl+C kapan saja, lanjutkan lewat menu Upload, urutan grid tetap benar."))

    if not ya("\nMulai pemotongan?"):
        print("Pemotongan dibatalkan.")
        return

    folders = []

    for nomor, (foto, baris, fokus) in enumerate(daftar, start=1):
        print(redup(f"\nFoto {nomor}/{len(daftar)}: {foto.name}"))
        hasil = proses_potong(foto, baris, fokus)

        if not hasil:
            for folder in folders:
                shutil.rmtree(folder, ignore_errors=True)
            print("Dibatalkan, hasil sementara dibersihkan.")
            return

        folders.append(hasil)

    selesaikan(gabung_hasil(folders), bloks)


def cari_folder_terbaru() -> Path | None:
    if not OUTPUT_DIR.is_dir():
        return None

    daftar = [
        f for f in OUTPUT_DIR.iterdir()
        if f.is_dir() and (f / "queue.json").is_file()
    ]

    return max(daftar, key=lambda f: f.stat().st_mtime) if daftar else None


def dengan_antrean(aksi, pesan_kosong: str = "Antrean belum tersedia.") -> None:
    """Jalankan aksi(folder) pada antrean terbaru, atau beri tahu kalau belum ada."""
    folder = cari_folder_terbaru()

    if not folder:
        print(pesan_kosong)
        return

    print(redup(f"Antrean: {folder.name}"))

    try:
        aksi(folder)
    except (FileNotFoundError, ValueError) as error:
        print(merah(f"✗ {error}"))


def kelola_hasil_lama() -> None:
    if not OUTPUT_DIR.is_dir():
        print("\nBelum ada hasil pemotongan.")
        return

    daftar = sorted(
        (f for f in OUTPUT_DIR.iterdir() if f.is_dir()),
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    )

    while daftar:
        print("\n=== KELOLA HASIL LAMA ===")
        for nomor, folder in enumerate(daftar, start=1):
            print(f"[{nomor}] {folder.name}")
        print("[0] Kembali")

        pilihan = input("\nPilih folder yang ingin dihapus: ").strip()

        if pilihan == "0":
            return

        try:
            nomor = int(pilihan)
            if nomor < 1:
                raise IndexError
            target = daftar[nomor - 1]
        except (ValueError, IndexError):
            print("Pilihan tidak valid.")
            continue

        print(f"\nFolder yang dipilih: {target.name}")

        if not ya("Yakin ingin menghapus folder ini?", default=False):
            print("Penghapusan dibatalkan.")
            continue

        try:
            shutil.rmtree(target)
            daftar.remove(target)
            print(hijau("✓ Folder berhasil dihapus."))
        except OSError as error:
            print(merah(f"✗ Gagal menghapus folder: {error}"))

    print("Tidak ada hasil pemotongan tersisa.")


def menu_pengolahan() -> None:
    while True:
        tampilkan_menu_dengan_jeda([
            "=== PENGOLAHAN FOTO ===",
            "[1] Potong Foto",
            "[2] Potong Beberapa Foto (Bertumpuk)",
            "[0] Kembali",
        ])

        pilihan = input("Pilih menu: ").strip()

        if pilihan == "1":
            jalankan_pemotongan()
        elif pilihan == "2":
            jalankan_pemotongan_bertumpuk()
        elif pilihan == "0":
            break
        else:
            print("Pilihan tidak valid.")


def menu_antrean() -> None:
    while True:
        tampilkan_menu_dengan_jeda([
            "=== ANTREAN UPLOAD ===",
            "[1] Lihat Antrean",
            "[2] Review Antrean",
            "[3] Simulasi Upload",
            "[4] Upload ke Instagram",
            "[5] Batalkan Persetujuan",
            "[6] Kelola Hasil Lama",
            "[0] Kembali",
        ])

        pilihan = input("Pilih menu: ").strip()

        if pilihan == "1":
            dengan_antrean(lambda f: validasi_antrean(f) and tampilkan_antrean(f))
        elif pilihan == "2":
            dengan_antrean(review_antrean)
        elif pilihan == "3":
            dengan_antrean(lambda f: validasi_antrean(f) and simulasi_upload(f))
        elif pilihan == "4":
            dengan_antrean(upload_antrean)
        elif pilihan == "5":
            dengan_antrean(batalkan_persetujuan)
        elif pilihan == "6":
            kelola_hasil_lama()
        elif pilihan == "0":
            break
        else:
            print("Pilihan tidak valid.")


def menu_instagram() -> None:
    while True:
        tampilkan_menu_dengan_jeda([
            "=== INSTAGRAM ===",
            "[1] Cek Koneksi",
            "[2] Pengaturan Instagram",
            "[0] Kembali",
        ])

        pilihan = input("Pilih menu: ").strip()

        if pilihan == "1":
            cek_koneksi_instagram()
        elif pilihan == "2":
            pengaturan_instagram()
        elif pilihan == "0":
            break
        else:
            print("Pilihan tidak valid.")


def tampilkan_menu() -> None:
    banner()

    while True:
        print()
        tampilkan_menu_dengan_jeda([
            "=== MENU UTAMA ===",
            "[1] Pengolahan Foto",
            "[2] Antrean Upload",
            "[3] Instagram",
            "[0] Keluar",
        ])

        pilihan = input("Pilih menu: ").strip()

        if pilihan == "1":
            menu_pengolahan()
        elif pilihan == "2":
            menu_antrean()
        elif pilihan == "3":
            menu_instagram()
        elif pilihan == "0":
            print("XelGrid ditutup.")
            break
        else:
            print("Pilihan tidak valid.")
