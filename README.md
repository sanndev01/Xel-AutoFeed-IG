XelGrid

Instagram Photo Grid Automation Tool

XelGrid adalah aplikasi CLI berbasis Python yang membantu membuat Instagram Photo Grid dengan memotong foto menjadi beberapa bagian, mengatur urutan upload, dan mengelola proses publikasi ke Instagram.

XelGrid dirancang dengan sistem antrean (queue-based workflow) agar hasil grid dapat diperiksa dan disetujui terlebih dahulu sebelum dipublikasikan.

«Status proyek: Dalam pengembangan.

Catatan: Integrasi Instagram menggunakan "instagrapi". Kompatibilitas dengan Instagram dapat berubah sewaktu-waktu.»

---

✨ Fitur

🖼️ Pengolahan Foto

- Analisis foto — Menganalisis ukuran dan rasio foto sebelum diproses.
- Potong foto menjadi grid — Membagi foto menjadi beberapa tile dengan tiga kolom.
- Pengaturan fokus crop — Menentukan bagian foto yang diprioritaskan saat pemotongan.
- Grid beberapa foto — Menggabungkan beberapa foto ke dalam satu susunan grid vertikal.
- Preview hasil — Melihat pratinjau hasil sebelum melakukan upload.

📋 Manajemen Antrean

- Antrean upload — Menyimpan daftar file dan urutan upload dalam "queue.json".
- Review manual — Memeriksa dan menyetujui antrean sebelum proses upload.
- Simulasi upload — Memeriksa kesiapan file tanpa mengunggahnya ke Instagram.
- Upload berurutan — Mengunggah foto sesuai urutan yang diperlukan untuk menyusun grid.
- Resume upload — Melanjutkan antrean yang terhenti dengan menyimpan progres.

📱 Integrasi Instagram

- Pengaturan akun Instagram.
- Pengelolaan sesi login.
- Pemeriksaan status integrasi Instagram.
- Upload foto sesuai urutan antrean.
- Dukungan caption saat proses upload.

🖥️ Antarmuka

- Antarmuka berbasis Command-Line Interface (CLI).
- Menu interaktif.
- Progress bar dan indikator proses.

---

🛠️ Teknologi

Teknologi| Kegunaan
Python 3.10+| Bahasa pemrograman utama
Pillow| Pemrosesan, crop, resize, dan penyimpanan gambar
instagrapi| Integrasi dengan Instagram
JSON| Penyimpanan konfigurasi dan data antrean

---

📁 Struktur Proyek

XelGrid/
├── xelgrid.py
├── config.json
├── requirements.txt
├── README.md
├── .gitignore
│
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
│
├── interface/
│   └── menu.py
│
├── media/
│
├── output/
│   └── .gitkeep
│
└── utils/

«Struktur folder dapat berubah seiring pengembangan proyek.»

---

📋 Persyaratan

Sebelum menggunakan XelGrid, pastikan perangkat lu memenuhi persyaratan berikut:

- Python versi 3.10 atau lebih baru.
- Library Pillow.
- Library instagrapi.
- Akun Instagram jika ingin menggunakan fitur upload.

---

🚀 Instalasi

1. Clone Repository

git clone https://github.com/sanndev01/Xel-AutoFeed-IG.git
cd Xel-AutoFeed-IG

2. Buat Virtual Environment (Opsional)

Untuk mengisolasi dependensi proyek, lu bisa menggunakan virtual environment.

python -m venv .venv

Aktifkan virtual environment sesuai sistem operasi.

Linux, Termux, atau macOS:

source .venv/bin/activate

Windows:

.venv\Scripts\activate

3. Instal Dependensi

pip install -r requirements.txt

4. Jalankan XelGrid

python xelgrid.py

---

▶️ Cara Penggunaan

1. Pengolahan Foto

Pilih menu Pengolahan Foto, kemudian pilih salah satu opsi yang tersedia:

- Potong Foto — Memproses satu foto menjadi grid.
- Potong Beberapa Foto — Menyusun beberapa foto secara vertikal dalam satu antrean.

Tentukan jumlah baris dan fokus crop jika diperlukan.

Setelah proses pemotongan selesai, XelGrid akan membuat preview dan antrean upload.

2. Review Antrean

Sebelum melakukan upload, periksa terlebih dahulu antrean yang telah dibuat.

1. Buka menu Antrean Upload.
2. Pilih Review Antrean.
3. Periksa preview dan daftar file.
4. Setujui antrean jika urutannya sudah benar.

3. Simulasi Upload

Gunakan opsi Simulasi Upload untuk memeriksa kesiapan file tanpa benar-benar mengunggahnya ke Instagram.

Fitur ini dapat digunakan untuk memastikan file dan antrean telah siap diproses.

4. Upload ke Instagram

Setelah antrean disetujui, ikuti langkah berikut:

1. Buka menu Instagram dan atur akun.
2. Buka menu Antrean Upload.
3. Pilih Upload ke Instagram.
4. Ikuti instruksi login jika diperlukan.
5. Masukkan caption jika diinginkan.
6. Konfirmasi proses upload.

«Penting: Periksa profil Instagram setelah upload. Urutan upload menentukan susunan akhir grid.»

---

⚙️ Konfigurasi

Pengaturan dasar XelGrid disimpan dalam file "config.json".

Contoh Konfigurasi

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

Penjelasan Konfigurasi

Pengaturan| Keterangan
"instagram.enabled"| Mengaktifkan atau menonaktifkan integrasi Instagram
"instagram.username"| Nama pengguna Instagram
"instagram.session_file"| Lokasi file sesi Instagram
"grid.rasio"| Rasio foto yang digunakan dalam pengolahan grid
"upload.jeda_min"| Jeda minimum antarproses upload
"upload.jeda_max"| Jeda maksimum antarproses upload

«Password Instagram tidak disimpan oleh aplikasi. Password dapat dimasukkan melalui prompt login atau variabel lingkungan "XELGRID_IG_PASSWORD".»

---

🔒 Keamanan

Untuk menjaga keamanan akun dan data pribadi, perhatikan hal-hal berikut:

- Jangan membagikan password atau file sesi Instagram.
- Jangan mengunggah "session.json" ke repository publik.
- Jangan menyimpan kredensial pribadi di dalam source code.
- Gunakan integrasi sesuai ketentuan dan kebijakan Instagram.
- Periksa kembali hasil grid sebelum dipublikasikan.

---

⚠️ Catatan Penting

- XelGrid menggunakan library pihak ketiga untuk integrasi Instagram.
- Perubahan pada sistem Instagram dapat memengaruhi fitur login dan upload.
- Fitur upload tidak menjamin bebas dari pembatasan atau tindakan keamanan Instagram.
- Pastikan penggunaan aplikasi sesuai dengan ketentuan layanan Instagram.

---

🗺️ Rencana Pengembangan

Pengembangan XelGrid dapat mencakup beberapa hal berikut:

- [ ] Peningkatan validasi hasil grid.
- [ ] Penambahan pengujian otomatis.
- [ ] Penanganan kesalahan yang lebih lengkap.
- [ ] Penyempurnaan dokumentasi.
- [ ] Pengelolaan konfigurasi yang lebih aman.
- [ ] Pengembangan antarmuka tambahan.

«Daftar di atas merupakan rencana pengembangan dan bukan jaminan fitur yang akan tersedia pada versi berikutnya.»

---

📄 Lisensi

Lisensi proyek belum ditentukan.

---

👤 Pengembang

Dikembangkan oleh Sann.

GitHub: "@sanndev01" (https://github.com/sanndev01)

---

⭐ Dukungan

Jika XelGrid bermanfaat buat lu, jangan lupa berikan Star pada repository ini!

"⭐ Berikan Star di GitHub" (https://github.com/sanndev01/Xel-AutoFeed-IG)

---

XelGrid — Simplify your Instagram grid workflow.