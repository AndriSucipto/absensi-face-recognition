HEAD
# Sistem Absensi Face Recognition - Web Version

Aplikasi absensi pegawai dengan teknologi pengenalan wajah (face recognition) menggunakan Python dan Flask.

## Fitur

- ✅ **Registrasi Pegawai** - Daftarkan pegawai baru dengan foto wajah
- ✅ **Check-In/Check-Out** - Absensi otomatis menggunakan face recognition
- ✅ **Daftar Pegawai** - Kelola data pegawai
- ✅ **Riwayat Absensi** - Lihat riwayat absensi dengan filter tanggal
- ✅ **Database SQLite** - Penyimpanan data lokal yang aman
- ✅ **Web Interface** - Tampilan web modern dan responsive
- ✅ **High Accuracy** - Sistem validasi ganda untuk akurasi tinggi

## Teknologi yang Digunakan

- Python 3.7+
- OpenCV - Pemrosesan gambar dan kamera
- face_recognition - Deteksi dan pengenalan wajah
- dlib - Library computer vision
- Flask - Web Framework
- SQLite - Database
- Bootstrap - Responsive UI

## Instalasi

### 1. Clone atau Download Project

Download project ini ke komputer Anda.

### 2. Install Python

Pastikan Python 3.7 atau lebih baru sudah terinstall. Cek dengan:

```bash
python --version
```

### 3. Install Dependencies

#### Windows:

Untuk Windows, install Visual C++ Build Tools terlebih dahulu (diperlukan untuk dlib):

- Download dari: https://visualstudio.microsoft.com/visual-cpp-build-tools/
- Install dengan memilih "Desktop development with C++"

Kemudian install dependencies:

```bash
pip install -r requirements.txt
```

**Catatan:** Jika instalasi dlib gagal, Anda bisa install wheel yang sudah dikompilasi:

```bash
# Download dlib wheel dari https://github.com/z-mahmud22/Dlib_Windows_Python3.x
# Sesuaikan dengan versi Python Anda, contoh:
pip install dlib-19.24.2-cp311-cp311-win_amd64.whl

# Kemudian install sisanya:
pip install opencv-python face-recognition numpy Pillow
```

#### Linux/Mac:

```bash
pip install -r requirements.txt
```

## Cara Menggunakan

### Menjalankan Aplikasi Web

```bash
python app_web.py
```

Kemudian buka browser dan akses: **http://localhost:5000**

---

## Panduan Penggunaan

### 1. Registrasi Pegawai Baru

1. Buka halaman **"Registrasi"** dari menu navigasi
2. Isi formulir dengan data pegawai:
   - ID Pegawai (contoh: EMP001)
   - Nama Lengkap
   - Departemen
   - Jabatan
3. Klik **"Ambil Foto"** untuk mengaktifkan kamera
4. Posisikan wajah dengan baik di depan kamera
5. Pastikan pencahayaan cukup dan wajah terlihat jelas
6. Klik tombol capture untuk mengambil foto
7. Klik **"Daftar Pegawai"** untuk menyimpan

**Catatan:** Sistem akan otomatis mendeteksi jika wajah sudah terdaftar sebelumnya.

### 2. Melakukan Absensi

1. Buka halaman **"Absensi"** dari menu navigasi
2. Kamera akan aktif otomatis
3. Posisikan wajah Anda dengan jelas di depan kamera
4. Klik **"Check In"** untuk absen masuk atau **"Check Out"** untuk absen keluar
5. Sistem akan mengenali wajah dan mencatat absensi
6. Confidence level akan ditampilkan untuk memastikan akurasi

**Tips untuk Akurasi Maksimal:**

- Pastikan pencahayaan cukup dan merata
- Posisikan wajah tegak lurus menghadap kamera
- Jaga jarak sekitar 30-50cm dari kamera
- Hindari menggunakan masker, kacamata tebal, atau topi
- Pastikan background tidak terlalu ramai
- Gunakan foto dengan ekspresi netral saat registrasi
- Sistem menggunakan threshold ketat (confidence min: 55%) untuk mencegah false positive

### 3. Melihat Daftar Pegawai

1. Buka tab **"Daftar Pegawai"**
2. Lihat semua pegawai yang terdaftar
3. Klik **"Refresh"** untuk memperbarui data
4. Pilih pegawai dan klik **"Hapus Pegawai Terpilih"** untuk menghapus

### 4. Melihat Riwayat Absensi

1. Buka tab **"Riwayat Absensi"**
2. Masukkan tanggal mulai dan tanggal akhir
3. Klik **"Tampilkan"** untuk melihat riwayat
4. Data akan menampilkan check-in dan check-out pegawai

## Struktur Project

```
UAS Final/
│
├── app_web.py                  # Aplikasi Web (Flask)
├── database.py                 # Modul database
├── face_recognition_module.py  # Modul face recognition
├── config.py                   # Konfigurasi aplikasi
├── requirements.txt            # Dependencies Python
├── README.md                   # Dokumentasi
│
├── templates/                  # Template HTML untuk web
│   ├── base.html
│   ├── dashboard.html
│   ├── registrasi.html
│   ├── absensi.html
│   ├── pegawai.html
│   └── riwayat.html
│
├── static/                     # File statis untuk web
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
│
├── absensi.db                  # Database SQLite (otomatis dibuat)
├── employee_images/            # Folder foto pegawai (otomatis dibuat)
└── attendance_logs/            # Folder log absensi (otomatis dibuat)
```

## Konfigurasi

Edit file `config.py` untuk mengubah pengaturan:

```python
# Pengaturan Face Recognition
FACE_DETECTION_CONFIDENCE = 0.5  # Threshold deteksi wajah
TOLERANCE = 0.4                  # Toleransi pencocokan (lebih rendah = lebih ketat)
MAX_FACE_DISTANCE = 0.45         # Maximum distance untuk match (confidence min ~55%)

# Pengaturan Kamera
CAMERA_INDEX = 0                 # Index kamera (0 = default)
CAMERA_WIDTH = 640               # Lebar frame kamera
CAMERA_HEIGHT = 480              # Tinggi frame kamera
```

### Penjelasan Parameter:

- **TOLERANCE**: Semakin kecil (0.3-0.4) = lebih ketat, semakin besar (0.5-0.6) = lebih longgar
- **MAX_FACE_DISTANCE**: Threshold jarak maksimal untuk dianggap cocok (0.45 = ~55% confidence minimum)
- Untuk keamanan tinggi, gunakan nilai rendah
- Untuk kemudahan akses, gunakan nilai lebih tinggi

## Troubleshooting

### Kamera tidak terdeteksi

- Pastikan webcam terhubung dengan baik
- Coba ubah `CAMERA_INDEX` di `config.py` (0, 1, 2, dst)
- Pastikan aplikasi lain tidak menggunakan kamera

### Face recognition tidak akurat / terlalu ketat

- Tingkatkan pencahayaan ruangan
- Jika terlalu ketat: naikkan `TOLERANCE` dan `MAX_FACE_DISTANCE` di `config.py`
- Jika terlalu longgar: turunkan nilai tersebut
- Ambil ulang foto pegawai dengan kualitas lebih baik
- Pastikan foto registrasi diambil dalam kondisi pencahayaan yang baik

### Wajah berbeda bisa masuk (False Positive)

- Turunkan nilai `TOLERANCE` ke 0.3-0.4
- Turunkan nilai `MAX_FACE_DISTANCE` ke 0.40-0.45
- Ambil ulang foto registrasi dengan kualitas tinggi
- Pastikan hanya 1 wajah terdeteksi saat registrasi

### Error saat install dependencies

- Pastikan Python dan pip versi terbaru
- Install Visual C++ Build Tools (Windows)
- Untuk dlib, gunakan wheel yang sudah dikompilasi

### Database error

- Pastikan folder memiliki permission write
- Hapus file `absensi.db` dan jalankan ulang aplikasi

## Keamanan dan Privacy

- Data wajah disimpan sebagai encoding (bukan foto mentah)
- Database SQLite tersimpan lokal
- Tidak ada koneksi internet diperlukan
- Data pegawai dapat dihapus kapan saja

## Pengembangan Lebih Lanjut

Fitur yang bisa ditambahkan:

- Export laporan ke Excel/PDF
- Notifikasi email untuk absensi
- Integrasi dengan sistem payroll
- Multi-kamera support
- REST API untuk integrasi sistem lain
- Deteksi liveness (anti-spoofing)
- Dashboard analytics dan statistik
- Mobile app version

## Lisensi

Project ini dibuat untuk keperluan tugas dan pembelajaran.

## Kontak

Jika ada pertanyaan atau masalah, silakan hubungi:

- Email: [email Anda]
- GitHub: [link GitHub Anda]

---

**Dibuat dengan ❤️ untuk Tugas UAS Pengolahan Citra Digital**

# absensi-face-recognatiaon 
9d5ed525a9f592f025d936c830269c118620a87c
