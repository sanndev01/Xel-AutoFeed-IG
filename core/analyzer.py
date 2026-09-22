from pathlib import Path
from PIL import Image

from core.config import baca_config

# Grid profil Instagram: 3 kolom, thumbnail 3:4 (sejak 2025).
# Tile harus persis rasio ini supaya IG tidak meng-crop ulang dan sambungan tetap pas.
KOLOM = 3
MAKS_BARIS = 6
UKURAN_TILE = {"3:4": (1080, 1440), "4:5": (1080, 1350), "1:1": (1080, 1080)}


def ukuran_tile() -> tuple[int, int]:
    rasio = baca_config()["grid"].get("rasio", "3:4")
    return UKURAN_TILE.get(rasio, UKURAN_TILE["3:4"])


def hitung_crop(lebar: int, tinggi: int, baris: int) -> tuple[float, float]:
    """
    Kembalikan (skala, terpakai) untuk foto lebar×tinggi yang dipotong `baris` × 3.
    skala > 1 berarti foto diperbesar, terpakai = porsi luas foto yang tidak terpangkas.
    """
    tw, th = ukuran_tile()
    target_w, target_h = KOLOM * tw, baris * th
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
