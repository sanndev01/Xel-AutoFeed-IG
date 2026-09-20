XelGrid
Instagram Photo Grid Automation Tool
XelGrid adalah aplikasi CLI berbasis Python untuk membantu membuat Instagram Photo Grid dengan cara memotong foto menjadi beberapa bagian, mengatur urutan upload, dan mengelola proses upload ke Instagram.
XelGrid dirancang dengan alur kerja berbasis antrean agar hasil grid dapat diperiksa terlebih dahulu sebelum dipublikasikan.
Status proyek: Dalam pengembangan.
Integrasi Instagram menggunakan instagrapi. Kompatibilitas dengan Instagram dapat berubah sewaktu-waktu.
✨ Fitur
🖼️ Analisis foto — Menganalisis ukuran dan rasio foto sebelum diproses.
✂️ Potong foto menjadi grid — Membagi foto menjadi beberapa tile dengan tiga kolom.
🎯 Pengaturan fokus crop — Menentukan bagian foto yang diprioritaskan saat pemotongan.
🧩 Grid beberapa foto — Menggabungkan beberapa foto ke dalam satu susunan grid vertikal.
👀 Preview hasil — Melihat pratinjau sebelum melakukan upload.
📋 Antrean upload — Menyimpan daftar file dan urutan upload dalam queue.json.
✅ Review manual — Memastikan antrean disetujui sebelum upload.
🧪 Simulasi upload — Memeriksa kesiapan file tanpa mengunggahnya ke Instagram.
📤 Upload berurutan — Mengunggah foto sesuai urutan yang diperlukan untuk menyusun grid.
🔄 Resume upload — Melanjutkan antrean yang terhenti dengan menyimpan progres.
⚙️ Pengaturan Instagram — Mengatur akun, sesi login, dan status integrasi.
🖥️ Antarmuka CLI — Menu interaktif dengan progress bar dan indikator proses.
🛠️ Teknologi
Python 3.10+ — Bahasa pemrograman utama.
Pillow — Pemrosesan, crop, resize, dan penyimpanan gambar.
instagrapi — Integrasi Instagram.
JSON — Penyimpanan konfigurasi dan data antrean.
📁 Struktur Proyek
XelGrid/
├── xelgrid.py
├── config.json
├── requirements.txt
├── README.md
├── .gitignore
├── core/
│   ├── analyzer.py
│   ├── config.py
│   ├── cutter.py
│   ├── enhancer.py
│   ├── instagram.py
│   ├── queue.py
│   ├── queue_validator.py
│   ├── queue_viewer.py
│   ├── reviewer.py
│   ├── ui.py
│   └── uploader.py
├── interface/
│   └── menu.py
├── media/
├── output/
│   └── .gitkeep
└── utils/
📋 Persyaratan
Python 3.10 atau versi yang lebih baru.
Pillow.
instagrapi.
Akun Instagram jika ingin menggunakan fitur upload.
🚀 Instalasi
1. Clone repository
git clone https://github.com/USERNAME/XelGrid.git
cd XelGrid
Ganti USERNAME dengan nama pengguna GitHub pemilik repository.
2. Buat virtual environment (opsional)
python -m venv .venv
Aktifkan virtual environment:
Linux, Termux, atau macOS:
source .venv/bin/activate
Windows:
.venv\Scripts\activate
3. Instal dependensi
pip install -r requirements.txt
4. Jalankan XelGrid
python xelgrid.py
▶️ Cara Penggunaan
1. Pengolahan Foto
Pilih menu Pengolahan Foto, kemudian pilih salah satu opsi:
Potong Foto — Memproses satu foto menjadi grid.
Potong Beberapa Foto — Menyusun beberapa foto secara vertikal dalam satu antrean.
Tentukan jumlah baris dan fokus crop jika diperlukan. Setelah pemotongan selesai, XelGrid akan membuat preview dan antrean.
2. Review Antrean
Sebelum upload:
Buka menu Antrean Upload.
Pilih Review Antrean.
Periksa preview dan daftar file.
Setujui antrean jika urutannya sudah benar.
3. Simulasi Upload
Gunakan opsi Simulasi Upload untuk memeriksa kesiapan file tanpa mengunggahnya ke Instagram.
4. Upload ke Instagram
Setelah antrean disetujui:
Buka menu Instagram dan atur akun.
Buka menu Antrean Upload.
Pilih Upload ke Instagram.
Ikuti instruksi login jika diperlukan.
Masukkan caption jika diinginkan.
Konfirmasi proses upload.
Penting: Periksa profil Instagram setelah upload. Urutan upload menentukan susunan akhir grid.
⚙️ Konfigurasi
Pengaturan dasar tersimpan dalam config.json.
Contoh konfigurasi:
{
  "instagram": {
    "enabled": false,
    "username": "",
    "session_file": "session.json"
  },
  "grid": {
    "rasio": "3:4"
  },
  "upload": {
    "jeda_min": 30,
    "jeda_max": 75
  }
}
Password Instagram tidak disimpan oleh aplikasi. Password dapat dimasukkan melalui prompt login atau variabel lingkungan XELGRID_IG_PASSWORD.
🔒 Keamanan
Jangan membagikan password atau file sesi Instagram.
Jangan mengunggah session.json ke repository publik.
Jangan menyimpan kredensial pribadi di dalam source code.
Gunakan integrasi sesuai ketentuan dan kebijakan Instagram.
Periksa kembali hasil grid sebelum dipublikasikan.
⚠️ Catatan
XelGrid menggunakan library pihak ketiga untuk integrasi Instagram. Perubahan pada sistem Instagram dapat memengaruhi fitur login dan upload.
Fitur upload tidak menjamin bebas dari pembatasan atau tindakan keamanan dari Instagram.
🗺️ Pengembangan Selanjutnya
Rencana pengembangan dapat mencakup:
Peningkatan validasi hasil grid.
Pengujian otomatis.
Penanganan kesalahan yang lebih lengkap.
Penyempurnaan dokumentasi.
Pengelolaan konfigurasi yang lebih aman.
Pengembangan antarmuka tambahan.
📄 Lisensi
Lisensi proyek belum ditentukan.
👤 Pengembang
Dikembangkan oleh [Nama Pengembang].
⭐ Jika proyek ini bermanfaat, kamu dapat memberikan star pada repository ini.
Did you like this feature?
