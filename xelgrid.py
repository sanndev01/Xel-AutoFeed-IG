from core.installer import aktifkan_venv_otomatis, pastikan_dependensi


if __name__ == "__main__":
    try:
        aktifkan_venv_otomatis()
        pastikan_dependensi()
        from interface.menu import tampilkan_menu
        tampilkan_menu()
    except (KeyboardInterrupt, EOFError):
        print("\nXelGrid ditutup.")
