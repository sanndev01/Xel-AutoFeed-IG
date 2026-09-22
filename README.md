XelGrid

«Instagram grid photo processor & uploader built for Termux.»

XelGrid adalah tools berbasis Python untuk membantu membuat Instagram grid dari foto, mengatur urutan hasilnya, dan mengelola proses upload ke Instagram.

Project ini dibuat dengan fokus pada penggunaan yang sederhana melalui terminal dan struktur yang mudah dikembangkan.

✨ Features

- 🖼️ Memotong foto menjadi beberapa tile Instagram
- 🧩 Membuat grid dari beberapa foto
- 📐 Analisis rasio dan ukuran foto
- 🎨 Penyesuaian crop dan enhancement
- 📋 Upload queue dengan status dan validasi
- 🔍 Preview & review sebelum upload
- 📸 Integrasi dengan Instagram
- ▶️ Upload berdasarkan urutan yang ditentukan
- 💾 Session Instagram tersimpan secara lokal
- 📱 Mendukung penggunaan di Termux

📱 Requirements

- Python 3.10+
- Termux / Linux / environment Python lainnya
- Akun Instagram untuk fitur upload

🚀 Installation

Clone repository:

git clone https://github.com/sanndev01/Xel-AutoFeed-IG.git
cd Xel-AutoFeed-IG

Install dependencies:

pip install -r requirements.txt

Untuk Termux, berikan akses storage jika diperlukan:

termux-setup-storage

▶️ Usage

Jalankan XelGrid dengan:

python xelgrid.py

Menu utama:

=== XELGRID ===

[1] Pengolahan Foto
[2] Antrean Upload
[3] Instagram
[0] Keluar

Pilih menu sesuai kebutuhan untuk memproses foto, mengatur antrean, atau mengelola koneksi Instagram.

📂 Project Structure

Xel-AutoFeed-IG/
├── core/
├── interface/
├── output/
├── config.json
├── requirements.txt
├── xelgrid.py
└── README.md

⚠️ Notes

XelGrid menggunakan library pihak ketiga untuk berinteraksi dengan Instagram. Perubahan pada sistem Instagram dapat memengaruhi fitur login atau upload.

Jangan membagikan session atau credential Instagram kepada orang lain.

🚧 Status

Active Development

XelGrid masih terus dikembangkan dan fitur dapat berubah pada versi berikutnya.

👤 Author

Sann

GitHub: "@sanndev01" (https://github.com/sanndev01)

📄 License

License belum ditentukan.