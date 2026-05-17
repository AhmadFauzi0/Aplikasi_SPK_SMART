# Aplikasi_SPK_SMART
Implementasi SPK menggunakan Metode SMART dengan Python

**Langkah 1: Struktur Direktori Proyek Web Modern**

Silakan buat folder baru bernama smart_web_dss di komputer Anda, lalu susun direktorinya di VSCode seperti ini:

smart_web_dss/
├── core/
│   ├── __init__.py
│   ├── engine.py          # Logika Perhitungan SMART & ROC (Sesuai Materi)
│   └── models.py          # Skema Database SQLite (Multi-Proyek)
├── templates/
│   ├── base.html          # Template Induk / Navbar & Footer (Bootstrap 5)
│   ├── index.html         # Dashboard Utama & Manajemen Multi-Proyek
│   ├── project.html       # Input Data, Edit Performa, & Fitur Upload
│   └── results.html       # Hasil Perangkingan & Grafik Analisis Sensitivitas
├── data/
│   └── smart_dss.db       # Database SQLite (Otomatis Terbuat)
├── app.py                 # Routing Server Utama (Flask)
└── requirements.txt       # Library yang Dibutuhkan

**Langkah 2: Mengonfigurasi Library (requirements.txt)**

Instal melalui terminal VSCode dengan mengetik pip install -r requirements.txt

**Langkah 3: Logika Perhitungan SMART & ROC (core/engine.py)**

Sesuai dengan materi perkuliahan Anda, modul ini menangani fungsi utilitas linear , pembobotan berbasis peringkat Rank Order Centroid (ROC) , serta redistribusi proporsional untuk analisis sensitivitas One-At-a-Time (OAT).

**Langkah 4: Skema Database & Manajemen Proyek (core/models.py)**

Menggunakan SQLAlchemy ORM agar mahasiswa terbiasa dengan manipulasi database modern tanpa menulis kueri SQL manual yang rentan kesalahan.

**Langkah 5: Controller & Routing Web Utama (app.py)**

File ini berfungsi sebagai jembatan utama (controller) yang mengontrol aliran data, proses unggah file Excel/CSV menggunakan pandas, ekspor data, serta kalkulasi sistem.

**Langkah 6: Pembuatan Frontend Web yang Elegan & Profesional**

Kita akan menggunakan Bootstrap 5 via CDN agar halaman memiliki tampilan modern, bersih, adaptif (responsive), serta dilengkapi efek komponen interaktif yang profesional.

1. templates/base.html (Kerangka Utama)

2. templates/index.html (Halaman Manajemen Multi-Proyek)

3. templates/project.html (Input Matriks & Unggah File Eksternal)

4. templates/results.html (Halaman Presentasi Skor Akhir)

**Cara Menjalankan Aplikasi Web oleh Mahasiswa:**

Jalankan perintah python app.py melalui terminal VSCode.

Server lokal akan aktif pada alamat: http://127.0.0.1:5000/.

Buka alamat tersebut di Google Chrome atau browser web modern lainnya.
