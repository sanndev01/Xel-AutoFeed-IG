import getpass
import os

from core.config import baca_config, simpan_config, path_sesi
from core.ui import Spinner


def login():
    """
    Login via instagrapi dan kembalikan Client (atau None jika gagal).

    Sesi disimpan di session.json supaya tidak login ulang tiap upload.
    Password tidak pernah disimpan: diambil dari env XEL_IG_PASSWORD atau ditanya.
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
        print("✗ instagrapi belum terpasang. Jalankan: pip install instagrapi")
        return None

    sesi = path_sesi()
    cl = Client()
    cl.delay_range = [1, 3]  # jeda acak antar request supaya tidak terlihat seperti bot

    try:
        if sesi.is_file():
            cl.load_settings(sesi)
            try:
                with Spinner("Memeriksa sesi tersimpan"):
                    cl.get_timeline_feed()
                return cl
            except LoginRequired:
                # Sesi mati: login ulang tapi pertahankan identitas perangkat
                uuids = cl.get_settings().get("uuids")
                cl.set_settings({})
                if uuids:
                    cl.set_uuids(uuids)
                print("Sesi kedaluwarsa, login ulang.")

        password = os.environ.get("XEL_IG_PASSWORD") or getpass.getpass(
            "Password Instagram (tidak disimpan): "
        )

        butuh_2fa = False
        with Spinner("Login ke Instagram") as sp:
            try:
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
        print(f"✗ Login gagal: {type(error).__name__}: {error}")
        print("Jika Instagram meminta verifikasi, setujui dulu lewat aplikasi resmi lalu coba lagi.")
        return None


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

    if input("\nTes login sekarang? [y/N]: ").strip().lower() in {"y", "ya"}:
        cl = login()
        if cl:
            print(f"✓ Login berhasil sebagai @{cl.username or username}")


def pengaturan_instagram() -> None:
    while True:
        config = baca_config()
        ig = config["instagram"]

        print("\n=== PENGATURAN INSTAGRAM ===")
        print(f"Akun     : {'@' + ig['username'] if ig.get('username') else '-'}")
        print(f"Integrasi: {'Aktif' if ig.get('enabled') else 'Nonaktif'}")
        print("[1] Atur akun & aktifkan")
        print("[2] Aktifkan / nonaktifkan integrasi")
        print("[3] Hapus sesi & data login")
        print("[0] Kembali")

        pilihan = input("Pilih menu: ").strip()

        if pilihan == "1":
            username = input("Username Instagram: ").strip().lstrip("@")
            if username:
                ig["username"], ig["enabled"] = username, True
                simpan_config(config)
                print("✓ Akun disimpan. Password akan ditanya saat login (tidak disimpan).")

        elif pilihan == "2":
            if not ig.get("username"):
                print("Atur akun dulu.")
                continue
            ig["enabled"] = not ig.get("enabled", False)
            simpan_config(config)
            print(f"✓ Integrasi {'diaktifkan' if ig['enabled'] else 'dinonaktifkan'}.")

        elif pilihan == "3":
            if input("Yakin hapus sesi & akun tersimpan? [y/N]: ").strip().lower() in {"y", "ya"}:
                path_sesi().unlink(missing_ok=True)
                ig["username"], ig["enabled"] = "", False
                simpan_config(config)
                print("✓ Data login lokal dihapus.")
            else:
                print("Penghapusan dibatalkan.")

        elif pilihan == "0":
            break

        else:
            print("Pilihan tidak valid.")
