from interface.menu import tampilkan_menu


if __name__ == "__main__":
    try:
        tampilkan_menu()
    except (KeyboardInterrupt, EOFError):
        print("\nXelGrid ditutup.")
