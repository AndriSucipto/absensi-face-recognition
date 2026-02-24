"""
Aplikasi Web - Sistem Absensi Face Recognition
Menggunakan Flask
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for, Response
from datetime import datetime
import cv2
import pickle
import os
import base64
import numpy as np
import face_recognition as fr

import config
from database import DatabaseManager
from face_recognition_module import FaceRecognitionModule

app = Flask(__name__)
app.config['SECRET_KEY'] = 'absensi-face-recognition-2026'

# Inisialisasi
db = DatabaseManager()
face_rec = FaceRecognitionModule()

# Load face data
face_data = db.get_all_face_encodings()
face_rec.load_known_faces(face_data)

# Variable global untuk streaming video
camera = None


@app.route('/')
def index():
    """Halaman utama / dashboard"""
    # Statistik
    employees = db.get_all_employees()
    attendance_today = db.get_attendance_today()
    
    total_employees = len(employees)
    present_today = len(attendance_today)
    
    stats = {
        'total_employees': total_employees,
        'present_today': present_today,
        'absent_today': total_employees - present_today,
        'date': datetime.now().strftime('%d %B %Y')
    }
    
    return render_template('dashboard.html', stats=stats, attendance=attendance_today)


@app.route('/registrasi')
def registrasi():
    """Halaman registrasi pegawai"""
    return render_template('registrasi.html')


@app.route('/registrasi/submit', methods=['POST'])
def registrasi_submit():
    """Proses registrasi pegawai"""
    try:
        employee_id = request.form.get('employee_id')
        name = request.form.get('name')
        department = request.form.get('department')
        position = request.form.get('position')
        image_data = request.form.get('image_data')
        
        if not all([employee_id, name, image_data]):
            return jsonify({'success': False, 'message': 'Data tidak lengkap!'})
        
        # Decode base64 image
        image_data = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Ekstrak face encoding
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        face_locations = fr.face_locations(rgb_image)
        
        if len(face_locations) == 0:
            return jsonify({'success': False, 'message': 'Tidak ada wajah terdeteksi!'})
        
        face_encodings = fr.face_encodings(rgb_image, face_locations)
        if len(face_encodings) == 0:
            return jsonify({'success': False, 'message': 'Gagal mengekstrak fitur wajah!'})
        
        face_encoding = face_encodings[0]
        
        # Validasi: cek apakah wajah sudah terdaftar
        if len(face_rec.known_face_encodings) > 0:
            face_distances = fr.face_distance(face_rec.known_face_encodings, face_encoding)
            min_distance = np.min(face_distances)
            
            if min_distance <= config.MAX_FACE_DISTANCE:
                similar_idx = np.argmin(face_distances)
                similar_name = face_rec.known_face_names[similar_idx]
                return jsonify({
                    'success': False, 
                    'message': f'Wajah ini sudah terdaftar atas nama: {similar_name}! (similarity: {(1-min_distance)*100:.1f}%)'
                })
        
        # Simpan foto
        image_filename = f"{employee_id}_{name.replace(' ', '_')}.jpg"
        image_path = os.path.join(config.EMPLOYEE_IMAGES_DIR, image_filename)
        cv2.imwrite(image_path, image)
        
        # Serialize face encoding
        face_encoding_blob = pickle.dumps(face_encoding)
        
        # Simpan ke database
        success = db.add_employee(employee_id, name, department, position, 
                                  image_path, face_encoding_blob)
        
        if success:
            # Reload face data
            face_data = db.get_all_face_encodings()
            face_rec.load_known_faces(face_data)
            
            return jsonify({'success': True, 'message': f'Pegawai {name} berhasil didaftarkan!'})
        else:
            return jsonify({'success': False, 'message': 'ID Pegawai sudah terdaftar!'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})


@app.route('/absensi')
def absensi():
    """Halaman absensi"""
    return render_template('absensi.html')


@app.route('/absensi/recognize', methods=['POST'])
def absensi_recognize():
    """Proses pengenalan wajah untuk absensi"""
    try:
        attendance_type = request.form.get('type', 'check_in')
        image_data = request.form.get('image_data')
        
        if not image_data:
            return jsonify({'success': False, 'message': 'Tidak ada gambar!'})
        
        # Decode base64 image
        image_data = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Deteksi wajah
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        face_locations = fr.face_locations(rgb_image)
        
        if len(face_locations) == 0:
            return jsonify({'success': False, 'message': 'Tidak ada wajah terdeteksi!'})
        
        face_encodings = fr.face_encodings(rgb_image, face_locations)
        
        if len(face_encodings) == 0:
            return jsonify({'success': False, 'message': 'Gagal mengenali wajah!'})
        
        face_encoding = face_encodings[0]
        
        # Cocokkan dengan database
        matches = fr.compare_faces(face_rec.known_face_encodings, face_encoding, 
                                   tolerance=config.TOLERANCE)
        
        if True not in matches:
            return jsonify({'success': False, 'message': 'Wajah tidak dikenali! Pastikan Anda sudah terdaftar.'})
        
        # Temukan yang paling cocok
        face_distances = fr.face_distance(face_rec.known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        min_distance = face_distances[best_match_index]
        
        # Validasi ganda: harus match DAN distance di bawah threshold
        if matches[best_match_index] and min_distance <= config.MAX_FACE_DISTANCE:
            employee_id = face_rec.known_face_ids[best_match_index]
            name = face_rec.known_face_names[best_match_index]
            confidence = (1 - min_distance) * 100
            
            # Record attendance
            success, message = db.record_attendance(employee_id, attendance_type)
            
            if success:
                action = "Check-in" if attendance_type == 'check_in' else "Check-out"
                return jsonify({
                    'success': True, 
                    'message': f'{action} berhasil! (Confidence: {confidence:.1f}%)',
                    'employee_id': employee_id,
                    'name': name,
                    'confidence': round(confidence, 1)
                })
            else:
                return jsonify({'success': False, 'message': message})
        else:
            return jsonify({
                'success': False, 
                'message': f'Wajah tidak cukup cocok! (Similarity: {(1-min_distance)*100:.1f}%) Threshold minimum: {(1-config.MAX_FACE_DISTANCE)*100:.1f}%'
            })
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})


@app.route('/pegawai')
def pegawai():
    """Halaman daftar pegawai"""
    employees = db.get_all_employees()
    return render_template('pegawai.html', employees=employees)


@app.route('/pegawai/delete/<employee_id>', methods=['POST'])
def pegawai_delete(employee_id):
    """Hapus pegawai"""
    try:
        success = db.delete_employee(employee_id)
        if success:
            # Reload face data
            face_data = db.get_all_face_encodings()
            face_rec.load_known_faces(face_data)
            
            return jsonify({'success': True, 'message': 'Pegawai berhasil dihapus!'})
        else:
            return jsonify({'success': False, 'message': 'Gagal menghapus pegawai!'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})


@app.route('/riwayat')
def riwayat():
    """Halaman riwayat absensi"""
    # Default: tampilkan hari ini
    start_date = request.args.get('start_date', datetime.now().strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
    
    history = db.get_attendance_history(start_date=start_date, end_date=end_date)
    
    return render_template('riwayat.html', history=history, 
                          start_date=start_date, end_date=end_date)


@app.route('/api/attendance/today')
def api_attendance_today():
    """API untuk mendapatkan absensi hari ini"""
    attendance = db.get_attendance_today()
    
    result = []
    for record in attendance:
        employee_id, name, check_in, check_out, status = record
        result.append({
            'employee_id': employee_id,
            'name': name,
            'check_in': check_in,
            'check_out': check_out,
            'status': status
        })
    
    return jsonify(result)


def generate_frames():
    """Generator untuk video streaming"""
    camera = cv2.VideoCapture(config.CAMERA_INDEX)
    
    while True:
        success, frame = camera.read()
        if not success:
            break
        
        # Flip untuk efek mirror
        frame = cv2.flip(frame, 1)
        
        # Deteksi wajah
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = fr.face_locations(rgb_frame)
        
        # Gambar kotak di sekitar wajah
        for (top, right, bottom, left) in face_locations:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        
        # Encode frame
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    camera.release()


@app.route('/video_feed')
def video_feed():
    """Streaming video dari kamera"""
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Sistem Absensi Face Recognition - Web Version")
    print("=" * 60)
    print("📱 Buka browser dan akses: http://localhost:5000")
    print("⏹️  Tekan CTRL+C untuk berhenti")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
