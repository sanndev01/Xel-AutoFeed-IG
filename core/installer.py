import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VENV_DIR = ROOT / ".venv"
REQ_FILE = ROOT / "requirements.txt"

MODUL_WAJIB = (
    ("PIL", "Pillow"),
    ("instagrapi", "instagrapi"),
)


def di_termux() -> bool:
    return "com.termux" in os.environ.get("PREFIX", "") or Path("/data/data/com.termux").exists()


def di_dalam_venv() -> bool:
    return sys.prefix != getattr(sys, "base_prefix", sys.prefix) or Path(sys.prefix).resolve() == VENV_DIR.resolve()


def python_venv() -> Path:
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def aktifkan_venv_otomatis() -> None:
    """Jika folder .venv sudah ada, otomatis jalankan ulang script memakai Python .venv."""
    py_venv = python_venv()
    if py_venv.is_file() and not di_dalam_venv():
        os.execv(str(py_venv), [str(py_venv), *sys.argv])


def cek_modul_hilang() -> list[str]:
    hilang = []
    for nama_import, nama_paket in MODUL_WAJIB:
        try:
            __import__(nama_import)
        except ImportError:
            hilang.append(nama_paket)
    return hilang


def _jalankan(cmd: list[str], cek: bool = True) -> int:
    print(f"→ Menjalankan: {' '.join(cmd)}")
    hasil = subprocess.run(cmd)
    if cek and hasil.returncode != 0:
        raise RuntimeError(f"Perintah gagal (kode {hasil.returncode}): {' '.join(cmd)}")
    return hasil.returncode


def _install_pillow_termux() -> None:
    """Di Termux arm64, pasang python-pillow & libjpeg-turbo via pkg agar tidak gagal kompilasi C."""
    if not di_termux() or not shutil.which("pkg"):
        return
    try:
        __import__("PIL")
    except ImportError:
        print("\n[Termux] Memasang python-pillow & libjpeg-turbo bawaan Termux...")
        _jalankan(["pkg", "install", "-y", "python-pillow", "libjpeg-turbo"], cek=False)


def _pip_install(py_exec: str, args: list[str], izinkan_break: bool = False) -> None:
    cmd = [py_exec, "-m", "pip", "install", *args]
    kode = _jalankan(cmd, cek=False)
    if kode != 0 and izinkan_break:
        print("Mencoba ulang dengan --break-system-packages...")
        _jalankan([*cmd, "--break-system-packages"], cek=True)
    elif kode != 0:
        raise RuntimeError("Instalasi pip gagal.")


def install_mode_venv() -> bool:
    """Mode 1: Buat .venv dan install seluruh library di dalamnya."""
    try:
        _install_pillow_termux()
        py_venv = python_venv()

        if not py_venv.is_file():
            print("\nMembuat virtual environment (.venv)...")
            cmd_venv = [sys.executable, "-m", "venv"]
            # Di Termux, gunakan --system-site-packages agar python-pillow dari pkg langsung terbaca
            if di_termux():
                cmd_venv.append("--system-site-packages")
            cmd_venv.append(str(VENV_DIR))
            _jalankan(cmd_venv)

        print("\nMemasang library ke dalam .venv...")
        _pip_install(str(py_venv), ["-U", "-r", str(REQ_FILE)], izinkan_break=False)
        print("\n✓ Instalasi Mode venv selesai!")
        return True
    except Exception as error:
        print(f"\n✗ Gagal memasang di mode venv: {error}")
        return False


def install_mode_langsung() -> bool:
    """Mode 2: Install langsung di environment Termux / sistem tanpa venv."""
    try:
        _install_pillow_termux()
        print("\nMemasang library langsung ke Python aktif...")
        _pip_install(sys.executable, ["-U", "-r", str(REQ_FILE)], izinkan_break=True)
        print("\n✓ Instalasi Mode Langsung selesai!")
        return True
    except Exception as error:
        print(f"\n✗ Gagal memasang secara langsung: {error}")
        return False


def pastikan_dependensi() -> None:
    """Cek library sebelum aplikasi masuk ke menu utama. Jika belum lengkap, tawarkan 2 mode install."""
    hilang = cek_modul_hilang()
    if not hilang:
        return

    print("\n=== SETUP LIBRARY XELGRID ===")
    print(f"Library belum terpasang: {', '.join(hilang)}")
    print("\nPilih mode instalasi:")
    print("[1] Mode Virtual Environment (.venv) — Rapi & terisolasi (Otomatis aktif)")
    print("[2] Mode Langsung di Termux / Sistem — Tanpa venv")
    print("[0] Batal / Keluar")

    while True:
        pilihan = input("\nPilih mode [1/2/0, Enter = 1]: ").strip() or "1"
        if pilihan == "1":
            if install_mode_venv():
                py_venv = python_venv()
                print("Menjalankan ulang XelGrid di dalam .venv...\n")
                os.execv(str(py_venv), [str(py_venv), *sys.argv])
            sys.exit(1)
        elif pilihan == "2":
            if install_mode_langsung():
                return
            sys.exit(1)
        elif pilihan == "0":
            sys.exit(0)
        else:
            print("Pilihan tidak valid.")


def menu_instalasi_library() -> None:
    """Menu pengaturan & pengecekan library dari dalam aplikasi."""
    while True:
        hilang = cek_modul_hilang()
        mode_aktif = "Virtual Environment (.venv)" if di_dalam_venv() else "Langsung (Termux / Sistem)"
        ada_venv = python_venv().is_file()

        print("\n=== PENGATURAN LIBRARY & ENVIRONMENT ===")
        print(f"Mode Aktif : {mode_aktif}")
        print(f"Folder venv: {'Tersedia (.venv)' if ada_venv else 'Belum dibuat'}")
        print(f"Status Lib : {'Lengkap (Pillow, instagrapi)' if not hilang else 'Kurang: ' + ', '.join(hilang)}")
        print("\n[1] Install / Perbarui via Mode Virtual Environment (.venv)")
        print("[2] Install / Perbarui via Mode Langsung (Termux / Sistem)")
        if ada_venv:
            print("[3] Hapus .venv (Gunakan mode langsung)")
        print("[0] Kembali")

        pilihan = input("Pilih menu: ").strip()

        if pilihan == "1":
            if install_mode_venv() and not di_dalam_venv():
                py_venv = python_venv()
                print("Berpindah ke Python .venv...")
                os.execv(str(py_venv), [str(py_venv), *sys.argv])
        elif pilihan == "2":
            install_mode_langsung()
        elif pilihan == "3" and ada_venv:
            konfirmasi = input("Yakin ingin menghapus folder .venv? [y/N]: ").strip().lower()
            if konfirmasi in {"y", "ya"}:
                shutil.rmtree(VENV_DIR, ignore_errors=True)
                print("✓ Folder .venv dihapus.")
        elif pilihan == "0":
            break
        else:
            print("Pilihan tidak valid.")
