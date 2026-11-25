import shutil
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageOps

from core.analyzer import KOLOM, MAKS_BARIS, info_tile, ukuran_mosaik
from core.config import OUTPUT_DIR
from core.enhancer import enhance_ringan

FORMAT_DIDUKUNG = {".png", ".jpg", ".jpeg", ".webp"}


def _ke_rgb(img: Image.Image) -> Image.Image:
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        latar = Image.new("RGB", img.size, "white")
        latar.paste(img, mask=img.getchannel("A"))
        return latar
    return img.convert("RGB")


def _folder_unik(dasar: Path) -> Path:
    """Pastikan nama folder tidak bentrok jika diproses pada detik yang sama."""
    kandidat = dasar
    indeks = 2
    while kandidat.exists():
        kandidat = dasar.parent / f"{dasar.name}_{indeks}"
        indeks += 1
    return kandidat


def _siapkan_kanvas_foto(
    path: str | Path,
    baris: int,
    fokus: float = 0.5,
    tinggi_tambahan: int = 0,
) -> tuple[Image.Image, float]:
    """
    Baca foto, koreksi orientasi EXIF, lalu crop + resize ke lebar mosaik penuh
    dan tinggi (baris * th + tinggi_tambahan).
    """
    path = Path(path).expanduser()

    if not path.is_file():
        raise FileNotFoundError(f"File tidak ditemukan: {path}")

    if path.suffix.lower() not in FORMAT_DIDUKUNG:
        raise ValueError("Format gambar belum didukung.")

    if not 1 <= baris <= MAKS_BARIS:
        raise ValueError(f"Jumlah baris harus 1-{MAKS_BARIS}.")

    fokus = max(0.0, min(1.0, float(fokus)))
    target_w, target_h = ukuran_mosaik(baris)
    target = (target_w, target_h + tinggi_tambahan)

    with Image.open(path) as img:
        img = _ke_rgb(ImageOps.exif_transpose(img))

    lebar, tinggi = img.size
    skala = max(target[0] / lebar, target[1] / tinggi)
    pusat = (fokus, 0.5) if lebar / tinggi > target[0] / target[1] else (0.5, fokus)

    kanvas = ImageOps.fit(img, target, Image.Resampling.LANCZOS, centering=pusat)
    del img
    return kanvas, skala


def _potong_mosaik_ke_folder(
    mosaik: Image.Image,
    total_baris: int,
    folder_hasil: Path,
    progress=None,
) -> Path:
    """
    Potong kanvas mosaik utuh menjadi total_baris × 3 tile dengan overlap bleed_x
    agar tiap foto tengah, kiri, kanan, atas, dan bawah saling nyambung di profil IG.
    """
    tw, th, bleed_x = info_tile()
    step_x = tw - (2 * bleed_x)
    target_w, target_h = mosaik.size

    folder_upload = folder_hasil / "upload_order"
    folder_upload.mkdir(parents=True, exist_ok=False)

    # IG menaruh post terbaru di kiri-atas, jadi upload dari kanan-bawah ke kiri-atas.
    posisi = [(r, c) for r in range(total_baris) for c in range(KOLOM)][::-1]
    digit = max(2, len(str(len(posisi))))

    for nomor, (r, c) in enumerate(posisi, start=1):
        x0 = c * step_x
        y0 = r * th
        tile = mosaik.crop((x0, y0, x0 + tw, y0 + th))
        tile.save(
            folder_upload / f"{nomor:0{digit}d}_r{r + 1:02d}_c{c + 1:02d}.jpg",
            quality=95,
            subsampling=0,
        )
        if progress:
            progress(nomor, len(posisi))

    # Preview menampilkan area efektif yang terlihat di grid profil 3:4
    area_tampil = (
        mosaik.crop((bleed_x, 0, target_w - bleed_x, target_h))
        if bleed_x > 0
        else mosaik.copy()
    )
    area_tampil.thumbnail((720, max(1440, total_baris * 360)), Image.Resampling.BILINEAR)
    area_tampil.save(folder_hasil / "preview.jpg", quality=85)

    return folder_hasil


def potong_foto(
    path: str | Path,
    baris: int,
    fokus: float = 0.5,
    output_dir: str | Path | None = None,
    progress=None,
) -> Path:
    """
    Crop foto ke rasio grid seamless (memperhitungkan overlap bleed horizontal),
    resize sekali ke ukuran final, lalu potong jadi baris × 3 tile JPEG yang sudah
    diberi nomor sesuai urutan upload.
    """
    path = Path(path).expanduser()
    mosaik, skala = _siapkan_kanvas_foto(path, baris, fokus)

    if skala > 1:
        mosaik = enhance_ringan(mosaik)

    induk = Path(output_dir).expanduser() if output_dir else OUTPUT_DIR
    folder_hasil = _folder_unik(induk / f"{path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

    return _potong_mosaik_ke_folder(mosaik, baris, folder_hasil, progress=progress)


def potong_bertumpuk(
    daftar_foto: list[tuple[str | Path, int, float]],
    blend_px: int = 180,
    output_dir: str | Path | None = None,
    progress=None,
) -> Path:
    """
    Susun beberapa foto dari atas ke bawah menjadi SATU kanvas mosaik utuh yang
    saling nyambung (kiri, kanan, atas, bawah, termasuk transisi halus antar-foto
    sebesar `blend_px` pixel jika blend_px > 0), lalu potong sekaligus.
    """
    if len(daftar_foto) < 2:
        raise ValueError("Minimal 2 foto untuk pemotongan bertumpuk.")

    tw, th, _ = info_tile()
    target_w, _ = ukuran_mosaik(1)
    total_baris = sum(baris for _, baris, _ in daftar_foto)
    total_tinggi = total_baris * th

    blend_px = max(0, min(int(blend_px), th // 2))
    kanvas_gabungan = Image.new("RGB", (target_w, total_tinggi), "white")

    # Mask gradasi vertikal (0 -> 255) untuk menyambung perbatasan atas-bawah antar foto
    mask_blend = None
    if blend_px > 0:
        grad = Image.linear_gradient("L").resize((1, blend_px), Image.Resampling.BILINEAR)
        mask_blend = grad.resize((target_w, blend_px), Image.Resampling.NEAREST)

    y_sekarang = 0
    perlu_enhance = False
    jumlah_foto = len(daftar_foto)

    for idx, (path, baris, fokus) in enumerate(daftar_foto):
        tinggi_blok = baris * th
        # Tambah ekstra ruang overlap di bawah (kecuali foto terakhir) & di atas (kecuali foto pertama)
        ekstra_atas = blend_px // 2 if (blend_px > 0 and idx > 0) else 0
        ekstra_bawah = (blend_px - ekstra_atas) if (blend_px > 0 and idx < jumlah_foto - 1) else 0

        potongan, skala = _siapkan_kanvas_foto(
            path,
            baris,
            fokus,
            tinggi_tambahan=ekstra_atas + ekstra_bawah,
        )
        if skala > 1:
            perlu_enhance = True

        y_tempel = y_sekarang - ekstra_atas

        if ekstra_atas > 0 and mask_blend is not None:
            # Blend area perbatasan sepanjang blend_px di sekitar garis sambungan y_sekarang
            y_mulai_blend = y_tempel
            area_lama = kanvas_gabungan.crop((0, y_mulai_blend, target_w, y_mulai_blend + blend_px))
            area_baru = potongan.crop((0, 0, target_w, blend_px))
            sambungan = Image.composite(area_baru, area_lama, mask_blend)
            kanvas_gabungan.paste(sambungan, (0, y_mulai_blend))
            sisa_baru = potongan.crop((0, blend_px, target_w, potongan.height))
            kanvas_gabungan.paste(sisa_baru, (0, y_mulai_blend + blend_px))
        else:
            kanvas_gabungan.paste(potongan, (0, max(0, y_tempel)))

        y_sekarang += tinggi_blok

    if perlu_enhance:
        kanvas_gabungan = enhance_ringan(kanvas_gabungan)

    induk = Path(output_dir).expanduser() if output_dir else OUTPUT_DIR
    folder_hasil = _folder_unik(induk / f"gabungan_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

    return _potong_mosaik_ke_folder(kanvas_gabungan, total_baris, folder_hasil, progress=progress)


def _urutkan_tile(folder_upload: Path) -> list[Path]:
    return sorted(
        folder_upload.glob("*.jpg"),
        key=lambda f: int(f.name.split("_", 1)[0]) if f.name.split("_", 1)[0].isdigit() else 0,
    )


def gabung_hasil(folders_atas_ke_bawah: list[Path]) -> Path:
    """
    Gabungkan beberapa hasil potong terpisah jadi satu folder siap-antre.
    """
    folders = list(folders_atas_ke_bawah)
    tujuan = _folder_unik(folders[0].parent / f"gabungan_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    folder_upload = tujuan / "upload_order"
    folder_upload.mkdir(parents=True, exist_ok=False)

    semua_tile = [
        (indeks, file)
        for indeks in range(len(folders), 0, -1)
        for file in _urutkan_tile(folders[indeks - 1] / "upload_order")
    ]
    digit = max(2, len(str(len(semua_tile))))

    for nomor, (indeks, file) in enumerate(semua_tile, start=1):
        sisa_nama = file.name.split("_", 1)[1] if "_" in file.name else file.name
        file.replace(folder_upload / f"{nomor:0{digit}d}_f{indeks}_{sisa_nama}")

    lebar, jarak, kepingan = 540, 6, []
    for folder in folders:
        with Image.open(folder / "preview.jpg") as p:
            kepingan.append(
                p.convert("RGB").resize(
                    (lebar, round(p.height * lebar / p.width)), Image.Resampling.BILINEAR
                )
            )

    kanvas = Image.new(
        "RGB",
        (lebar, sum(k.height for k in kepingan) + jarak * (len(kepingan) - 1)),
        "white",
    )
    y = 0
    for k in kepingan:
        kanvas.paste(k, (0, y))
        y += k.height + jarak
    kanvas.save(tujuan / "preview.jpg", quality=85)

    for folder in folders:
        shutil.rmtree(folder)

    return tujuan
