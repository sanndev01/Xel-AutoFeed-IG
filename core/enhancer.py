from PIL import Image, ImageEnhance, ImageFilter


def enhance_ringan(img: Image.Image) -> Image.Image:
    """Tajamkan dan naikkan kontras sedikit (dipakai setelah foto diperbesar)."""
    img = img.filter(ImageFilter.UnsharpMask(radius=1.2, percent=110, threshold=3))
    return ImageEnhance.Contrast(img).enhance(1.05)
