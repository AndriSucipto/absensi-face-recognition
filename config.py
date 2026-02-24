"""
Konfigurasi untuk Sistem Absensi Face Recognition
"""
import os

# Direktori
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "absensi.db")
EMPLOYEE_IMAGES_DIR = os.path.join(BASE_DIR, "employee_images")
ATTENDANCE_LOGS_DIR = os.path.join(BASE_DIR, "attendance_logs")

# Membuat direktori jika belum ada
os.makedirs(EMPLOYEE_IMAGES_DIR, exist_ok=True)
os.makedirs(ATTENDANCE_LOGS_DIR, exist_ok=True)

# Pengaturan Face Recognition
FACE_DETECTION_CONFIDENCE = 0.5  # Threshold untuk deteksi wajah
TOLERANCE = 0.4  # Semakin kecil, semakin ketat (0.4 = ketat, 0.6 = longgar)
MAX_FACE_DISTANCE = 0.45  # Maximum distance untuk dianggap match (lebih ketat dari TOLERANCE)

# Pengaturan untuk deteksi berkualitas tinggi
FACE_DETECTION_MODEL = 'hog'  # 'hog' lebih cepat, 'cnn' lebih akurat
NUMBER_OF_TIMES_TO_UPSAMPLE = 1  # Meningkatkan deteksi wajah kecil

# Pengaturan Kamera
CAMERA_INDEX = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# Pengaturan Aplikasi
APP_TITLE = "Sistem Absensi Face Recognition"
APP_WIDTH = 1000
APP_HEIGHT = 700
