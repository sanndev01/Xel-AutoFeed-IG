import getpass
import os
import subprocess
import sys
import time
from urllib.parse import unquote

from core.config import baca_config, simpan_config, path_sesi
from core.ui import Spinner, hijau, kuning, merah, redup


def _ambil_kunci_launcher_sync(cl) -> bool:
    """
    Ambil ig-set-password-encryption-key-id dan ig-set-password-encryption-pub-key
    dari endpoint launcher/sync/ (pengganti qe/sync/ yang dimatikan Instagram).
    """
    endpoints = (
        ("POST", "https://i.instagram.com/api/v1/launcher/sync/", {
            "id": getattr(cl, "uuid", "") or getattr(cl, "phone_id", ""),
            "server_config_retrieval": "1",
        }),
        ("GET", "https://i.instagram.com/api/v1/si/fetch_headers/?challenge_type=signup", None),
    )

    sess = getattr(cl, "private", None)
    if sess is None:
        return False

    headers = dict(getattr(cl, "headers", None) or {})
    if getattr(cl, "user_agent", None):
        headers.setdefault("User-Agent", cl.user_agent)

    for metode, url, payload in endpoints:
        try:
            if metode == "POST":
                resp = sess.post(url, data=payload, headers=headers, timeout=15)
            else:
                resp = sess.get(url, headers=headers, timeout=15)

            key_id = resp.headers.get("ig-set-password-encryption-key-id")
            pub_key = resp.headers.get("ig-set-password-encryption-pub-key")

            if key_id and pub_key:
                cl.public_key_id = int(key_id)
                cl.public_key = pub_key
                return True
        except Exception:
            continue

    return False


def _pasang_patch_enkripsi(cl) -> None:
    """
    Cegah error TypeError: int() argument ... not 'NoneType' pada instagrapi
    ketika qe/sync/ gagal memberikan public_key_id saat password_encrypt dipanggil.
    """
    asli_encrypt = getattr(cl, "password_encrypt", None)
    if not callable(asli_encrypt):
        return

    def _encrypt_aman(password: str) -> str:
        if not getattr(cl, "public_key_id", None) or not getattr(cl, "public_key", None):
            _ambil_kunci_launcher_sync(cl)

        if getattr(cl, "public_key_id", None) and getattr(cl, "public_key", None):
            try:
                return asli_encrypt(password)
            except TypeError:
                pass

        # Fallback format #PWD_INSTAGRAM versi 0 jika server tidak mengirim header kunci
        return f"#PWD_INSTAGRAM:0:{int(time.time())}:{password}"

    cl.password_encrypt = _encrypt_aman


def login_dengan_sessionid(cl=None) -> object | None:
    """
    Jalur alternatif login menggunakan cookie sessionid dari browser.
    Aman dari kendala enkripsi password atau blokir login perangkat baru.
    """
    try:
        from instagrapi import Client
    except ImportError:
        print(merah("✗ instagrapi belum terpasang."))
        return None

    print("\n=== LOGIN VIA SESSION ID BROWSER ===")
    print(redup("Cara ambil: Login IG di browser (Chrome/Kiwi/Via) → Inspect/Cookies → salin isi 'sessionid'."))
    mentah = input("Masukkan sessionid (kosong = batal): ").strip()
    if not mentah:
        return None

    sessionid = unquote(mentah.strip("'\""))
    cl = cl or Client()
    cl.delay_range = [1, 3]
    _pasang_patch_enkripsi(cl)

    try:
        with Spinner("Masuk menggunakan sessionid"):
            cl.login_by_sessionid(sessionid)

        sesi = path_sesi()
        cl.dump_settings(sesi)

        config = baca_config()
        if getattr(cl, "username", None):
            config["instagram"]["username"] = cl.username
            config["instagram"]["enabled"] = True
            simpan_config(config)

        print(hijau(f"✓ Berhasil masuk & menyimpan sesi di {sesi.name}!"))
        return cl
    except Exception as error:
        print(merah(f"✗ Gagal login via sessionid: {type(error).__name__}: {error}"))
        return None


def login():
    """
    Login via instagrapi dan kembalikan Client (atau None jika gagal).

    Sesi disimpan di session.json supaya tidak login ulang tiap upload.
    Password tidak pernah disimpan: diambil dari env XELGRID_IG_PASSWORD atau ditanya.
    """
    ig = baca_config()["instagram"]
    username = ig.get("username", "").strip()

    if not (ig.get("enabled") and username):
        print("✗ Instagram belum diaktifkan. Atur dulu di Instagram → Pengaturan.")
        return None

    try:
        from instagrapi import Client
        from instagrapi.exceptions import LoginRequired, TwoFactorRequired
    except ImportError:
        print("✗ instagrapi belum terpasang. Jalankan: pip install -U instagrapi")
        return None

    sesi = path_sesi()
    cl = Client()
    cl.delay_range = [1, 3]
    _pasang_patch_enkripsi(cl)

    try:
        if sesi.is_file():
            cl.load_settings(sesi)
            try:
                with Spinner("Memeriksa sesi tersimpan"):
                    cl.get_timeline_feed()
                return cl
            except LoginRequired:
                uuids = cl.get_settings().get("uuids")
                cl.set_settings({})
                if uuids:
                    cl.set_uuids(uuids)
                print(kuning("Sesi kedaluwarsa, login ulang."))

        password = os.environ.get("XELGRID_IG_PASSWORD") or getpass.getpass(
            "Password Instagram (tidak disimpan, Enter kosong = pakai sessionid): "
        )

        if not password:
            return login_dengan_sessionid(cl)

        butuh_2fa = False
        with Spinner("Login ke Instagram") as sp:
            try:
                _ambil_kunci_launcher_sync(cl)
                cl.login(username, password)
            except TwoFactorRequired:
                butuh_2fa = True
                sp.ubah("Instagram meminta kode 2FA")

        if butuh_2fa:
            kode = input("Kode 2FA: ").strip()
            with Spinner("Verifikasi 2FA"):
                cl.login(username, password, verification_code=kode)

        cl.dump_settings(sesi)
        return cl

    except Exception as error:
        print(merah(f"✗ Login password gagal: {type(error).__name__}: {error}"))
        print(kuning("Tip: Jika login password ditolak server IG, gunakan jalur Session ID browser."))
        if input("Coba login pakai Session ID sekarang? [Y/n]: ").strip().lower() in {"", "y", "ya"}:
            return login_dengan_sessionid(cl)
        return None


def update_instagrapi() -> None:
    """Perbarui paket instagrapi ke versi paling baru."""
    print("\nMemperbarui instagrapi ke versi terbaru...")
    cmd = [sys.executable, "-m", "pip", "install", "-U", "instagrapi"]
    kode = subprocess.run(cmd).returncode
    if kode != 0:
        subprocess.run([*cmd, "--break-system-packages"])
    else:
        print(hijau("✓ instagrapi berhasil diperbarui!"))


def cek_koneksi_instagram() -> None:
    ig = baca_config()["instagram"]
    aktif = ig.get("enabled", False)
    username = ig.get("username", "")

    print("\n=== STATUS INSTAGRAM ===")
    print(f"Integrasi : {'Aktif' if aktif else 'Nonaktif'}")
    print(f"Akun      : {'@' + username if username else '-'}")
    print(f"Sesi      : {'tersimpan' if path_sesi().is_file() else 'belum ada'}")

    if not (aktif and username):
        print("\nAtur akun dulu di Pengaturan Instagram.")
        return

    print("\n[1] Tes Login (Password / Cek Sesi)")
    print("[2] Login via Session ID Browser (Bypass jika login password gagal)")
    print("[0] Kembali")
    pilihan = input("Pilih aksi [Enter = 1]: ").strip() or "1"

    if pilihan == "1":
        cl = login()
        if cl:
            print(hijau(f"✓ Login berhasil sebagai @{getattr(cl, 'username', None) or username}"))
    elif pilihan == "2":
        cl = login_dengan_sessionid()
        if cl:
            print(hijau(f"✓ Login berhasil sebagai @{getattr(cl, 'username', None) or username}"))


def pengaturan_instagram() -> None:
    while True:
        config = baca_config()
        ig = config["instagram"]

        print("\n=== PENGATURAN INSTAGRAM ===")
        print(f"Akun     : {'@' + ig['username'] if ig.get('username') else '-'}")
        print(f"Integrasi: {'Aktif' if ig.get('enabled') else 'Nonaktif'}")
        print(f"Sesi     : {'Tersimpan (session.json)' if path_sesi().is_file() else 'Belum ada'}")
        print("[1] Atur akun & aktifkan")
        print("[2] Login via Session ID Browser")
        print("[3] Update library instagrapi ke versi terbaru")
        print("[4] Aktifkan / nonaktifkan integrasi")
        print("[5] Hapus sesi & data login")
        print("[0] Kembali")

        pilihan = input("Pilih menu: ").strip()

        if pilihan == "1":
            username = input("Username Instagram: ").strip().lstrip("@")
            if username:
                ig["username"], ig["enabled"] = username, True
                simpan_config(config)
                print(hijau("✓ Akun disimpan. Password akan ditanya saat login (tidak disimpan)."))

        elif pilihan == "2":
            login_dengan_sessionid()

        elif pilihan == "3":
            update_instagrapi()

        elif pilihan == "4":
            if not ig.get("username"):
                print("Atur akun dulu.")
                continue
            ig["enabled"] = not ig.get("enabled", False)
            simpan_config(config)
            print(hijau(f"✓ Integrasi {'diaktifkan' if ig['enabled'] else 'dinonaktifkan'}."))

        elif pilihan == "5":
            if input("Yakin hapus sesi & akun tersimpan? [y/N]: ").strip().lower() in {"y", "ya"}:
                path_sesi().unlink(missing_ok=True)
                ig["username"], ig["enabled"] = "", False
                simpan_config(config)
                print(hijau("✓ Data login lokal dihapus."))
            else:
                print("Penghapusan dibatalkan.")

        elif pilihan == "0":
            break

        else:
            print("Pilihan tidak valid.")
