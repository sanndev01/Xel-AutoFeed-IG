import itertools
import math
import os
import sys
import threading
import time

TTY = sys.stdout.isatty()
ANSI = TTY and not os.environ.get("NO_COLOR")
FRAMES = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"


def _warna(kode: str):
    return lambda teks: f"\033[{kode}m{teks}\033[0m" if ANSI else str(teks)


tebal, redup = _warna("1"), _warna("2")
merah, hijau, kuning, cyan = _warna("31"), _warna("32"), _warna("33"), _warna("36")


def _tulis(teks: str) -> None:
    sys.stdout.write("\r\033[2K" + teks)
    sys.stdout.flush()


def bar(i: float, total: float, lebar: int = 16) -> str:
    isi = round(lebar * min(i / total, 1)) if total else lebar
    return cyan("■" * isi) + redup("□" * (lebar - isi))


class Spinner:
    """
    Spinner untuk proses yang sedang berjalan.

        with Spinner("Memotong") as sp:
            sp.ubah("Memotong 3/9")
    """

    def __init__(self, teks: str = "Memproses"):
        self.teks = teks
        self._stop = threading.Event()
        self._thread = None

    def ubah(self, teks: str) -> None:
        self.teks = teks

    def _putar(self) -> None:
        for frame in itertools.cycle(FRAMES):
            if self._stop.is_set():
                break
            _tulis(f"{cyan(frame)} {self.teks}")
            self._stop.wait(0.08)

    def __enter__(self):
        if TTY:
            self._thread = threading.Thread(target=self._putar, daemon=True)
            self._thread.start()
        return self

    def __exit__(self, tipe, nilai, tb):
        self._stop.set()
        if self._thread:
            self._thread.join()
        tanda = merah("✗") if tipe else hijau("✓")
        if TTY:
            _tulis(f"{tanda} {self.teks}")
            print()
        else:
            print(f"{tanda} {self.teks}")
        return False


def progress(i: int, total: int, teks: str = "") -> None:
    """Progress bar satu baris; pindah baris otomatis saat selesai."""
    if TTY:
        _tulis(f"{bar(i, total)} {i}/{total} {teks}")
        if i >= total:
            print()
    else:
        print(f"[{i}/{total}] {teks}")


def hitung_mundur(detik: float, teks: str = "Jeda") -> None:
    """Jeda berhitung mundur dengan animasi (jeda tetap berjalan walau bukan terminal)."""
    if not TTY:
        print(f"{teks} {detik:.0f}s...")
        time.sleep(detik)
        return

    akhir = time.monotonic() + detik
    for frame in itertools.cycle(FRAMES):
        sisa = akhir - time.monotonic()
        if sisa <= 0:
            break
        _tulis(f"{kuning(frame)} {teks} {math.ceil(sisa):>3}s {bar(detik - sisa, detik)}")
        time.sleep(0.1)

    _tulis(f"{hijau('✓')} {teks} selesai")
    print()


def ketik(teks: str, kecepatan: float = 0.015) -> None:
    if not TTY:
        print(teks)
        return

    for karakter in teks:
        print(karakter, end="", flush=True)
        time.sleep(kecepatan)
    print()


def tampilkan_menu_dengan_jeda(baris_menu, jeda: float = 0.03) -> None:
    """Menu muncul baris demi baris; baris pertama dianggap judul."""
    for nomor, baris in enumerate(baris_menu):
        print(tebal(cyan(baris)) if nomor == 0 else baris)
        if TTY:
            time.sleep(jeda)


def banner() -> None:
    """Grid 3×3 terisi dalam urutan upload (kanan-bawah → kiri-atas)."""
    if not TTY:
        print("=== XELGRID ===")
        return

    teks = [
        tebal(cyan("X E L G R I D")),
        redup("potong · urutkan · upload"),
        redup("grid Instagram yang nyambung"),
    ]
    isi = [False] * 9

    def gambar(pertama: bool) -> None:
        if not pertama:
            sys.stdout.write("\033[3A")
        for r in range(3):
            sel = " ".join(
                cyan("■") if isi[r * 3 + c] else redup("□") for c in range(3)
            )
            sys.stdout.write(f"\r\033[2K  {sel}   {teks[r]}\n")
        sys.stdout.flush()

    print()
    gambar(True)
    for indeks in reversed(range(9)):
        time.sleep(0.07)
        isi[indeks] = True
        gambar(False)
