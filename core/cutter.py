import shutil
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageOps

from core.analyzer import KOLOM, MAKS_BARIS, ukuran_tile
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


def potong_foto(
    path: str | Path,
    baris: int,
    fokus: float = 0.5,
    output_dir: str | Path | None = None,
    progress=None,
) -> Path:
    """
    Crop foto ke rasio grid, resize sekali ke ukuran final, lalu potong jadi
    baris × 3 tile JPEG yang sudah diberi nomor sesuai urutan upload.

    fokus: 0.0 / 0.5 / 1.0 = posisi crop di sumbu yang terpangkas (atas-kiri / tengah / bawah-kanan).
    progress: callback opsional progress(i, total) saat tile disimpan.
    """
    path = Path(path).expanduser()

    if not path.is_file():
        raise FileNotFoundError(f"File tidak ditemukan: {path}")

    if path.suffix.lower() not in FORMAT_DIDUKUNG:
        raise ValueError("Format gambar belum didukung.")

    if not 1 <= baris <= MAKS_BARIS:
        raise ValueError(f"Jumlah baris harus 1-{MAKS_BARIS}.")

    tw, th = ukuran_tile()
    target = (KOLOM * tw, baris * th)

    with Image.open(path) as img:
        img = _ke_rgb(ImageOps.exif_transpose(img))

    lebar, tinggi = img.size
    skala = max(target[0] / lebar, target[1] / tinggi)
    pusat = (fokus, 0.5) if lebar / tinggi > target[0] / target[1] else (0.5, fokus)

    # Satu kali crop + resize langsung ke ukuran final (tanpa file perantara)
    mosaik = ImageOps.fit(img, target, Image.Resampling.LANCZOS, centering=pusat)
    del img

    if skala > 1:
        mosaik = enhance_ringan(mosaik)

    folder_hasil = (
        Path(output_dir).expanduser() if output_dir else OUTPUT_DIR
    ) / f"{path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    folder_upload = folder_hasil / "upload_order"
    folder_upload.mkdir(parents=True, exist_ok=False)

    # IG menaruh post terbaru di kiri-atas, jadi upload dari kanan-bawah ke kiri-atas.
    posisi = [(r, c) for r in range(baris) for c in range(KOLOM)][::-1]

    for nomor, (r, c) in enumerate(posisi, start=1):
        tile = mosaik.crop((c * tw, r * th, (c + 1) * tw, (r + 1) * th))
        tile.save(
            folder_upload / f"{nomor:02d}_r{r + 1:02d}_c{c + 1:02d}.jpg",
            quality=95,
            subsampling=0,
        )
        if progress:
            progress(nomor, len(posisi))

    # Preview hasil crop, untuk dicek sebelum upload
    mosaik.thumbnail((720, 1440), Image.Resampling.BILINEAR)
    mosaik.save(folder_hasil / "preview.jpg", quality=85)

    return folder_hasil


def gabung_hasil(folders_atas_ke_bawah: list[Path]) -> Path:
    """
    Gabungkan beberapa hasil potong jadi satu folder siap-antre.

    Urutan folder = urutan di profil dari atas ke bawah. Karena IG menaruh post
    terbaru di atas, foto paling bawah harus diupload lebih dulu, jadi tile
    diberi nomor mulai dari foto terakhir. Tiap foto sudah kelipatan 3 tile,
    jadi baris antar foto tetap sejajar.
    """
    folders = list(folders_atas_ke_bawah)
    tujuan = folders[0].parent / f"gabungan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    folder_upload = tujuan / "upload_order"
    folder_upload.mkdir(parents=True, exist_ok=False)

    nomor = 0
    for indeks in range(len(folders), 0, -1):
        for file in sorted((folders[indeks - 1] / "upload_order").glob("*.jpg")):
            nomor += 1
            # 01_r02_c03.jpg -> 07_f2_r02_c03.jpg (f = foto ke-berapa dari atas)
            file.replace(folder_upload / f"{nomor:02d}_f{indeks}_{file.name[3:]}")

    # Preview: susun preview tiap foto dari atas ke bawah
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
