from pathlib import Path
from PIL import Image

from core.config import baca_config

# Grid profil Instagram menampilkan thumbnail dalam rasio 3:4.
# Saat mengunggah tile 4:5 (1080x1350) agar aman di API/instagrapi, Instagram
# memangkas ~34px di sisi kiri & kanan tiap tile (area tampil efektif 1012x1350).
# Dengan overlap bleed 34px, sambungan antar-kolom di profil tetap rapat & nyambung.
KOLOM = 3
MAKS_BARIS = 6
UKURAN_TILE = {
    "4:5": (1080, 1350),
    "3:4": (1080, 1440),
    "1:1": (1080, 1080),
}
BLEED_TILE = {
    "4:5": 34,   # 1080 - (2 * 34) = 1012px tampil di grid 3:4 (1012:1350 ≈ 3:4)
    "3:4": 0,    # 1080x1440 sudah 3:4 murni
    "1:1": 135,  # 1080 - (2 * 135) = 810px tampil di grid 3:4 (810:1080 = 3:4)
}


def info_tile() -> tuple[int, int, int]:
    """Kembalikan (lebar_tile, tinggi_tile, bleed_x) sesuai rasio di config."""
    rasio = baca_config()["grid"].get("rasio", "4:5")
    tw, th = UKURAN_TILE.get(rasio, UKURAN_TILE["4:5"])
    bleed_x = BLEED_TILE.get(rasio, BLEED_TILE["4:5"])
    return tw, th, bleed_x


def ukuran_tile() -> tuple[int, int]:
    tw, th, _ = info_tile()
    return tw, th


def ukuran_mosaik(baris: int) -> tuple[int, int]:
    """Ukuran kanvas mosaik penuh (termasuk bleed kiri-kanan) untuk `baris` baris."""
    tw, th, bleed_x = info_tile()
    step_x = tw - (2 * bleed_x)
    target_w = (KOLOM * step_x) + (2 * bleed_x)
    target_h = baris * th
    return target_w, target_h


def hitung_crop(lebar: int, tinggi: int, baris: int) -> tuple[float, float]:
    """
    Kembalikan (skala, terpakai) untuk foto lebar×tinggi yang dipotong `baris` × 3.
    skala > 1 berarti foto diperbesar, terpakai = porsi luas foto yang tidak terpangkas.
    """
    target_w, target_h = ukuran_mosaik(baris)
    skala = max(target_w / lebar, target_h / tinggi)
    terpakai = (target_w * target_h) / (skala**2 * lebar * tinggi)
    return skala, terpakai


def rekomendasi_baris(lebar: int, tinggi: int) -> int:
    """Jumlah baris yang paling sedikit memangkas foto."""
    return max(
        range(1, MAKS_BARIS + 1),
        key=lambda b: hitung_crop(lebar, tinggi, b)[1],
    )


def analisis_foto(path: str | Path) -> dict:
    """Baca ukuran asli foto (memperhitungkan rotasi EXIF) tanpa memuat pixel."""
    path = Path(path).expanduser()

    with Image.open(path) as img:
        lebar, tinggi = img.size
        if img.getexif().get(0x0112, 1) in (5, 6, 7, 8):
            lebar, tinggi = tinggi, lebar
        format_foto, mode = img.format, img.mode

    return {
        "path": str(path),
        "lebar": lebar,
        "tinggi": tinggi,
        "mode": mode,
        "format": format_foto,
        "rekomendasi_baris": rekomendasi_baris(lebar, tinggi),
    }
