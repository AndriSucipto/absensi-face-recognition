"""
Modul Face Recognition untuk Sistem Absensi
Menangani deteksi dan pengenalan wajah
"""
import cv2
import face_recognition
import numpy as np
import pickle
import config

class FaceRecognitionModule:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_face_ids = []
    
    def load_known_faces(self, face_data):
        """Memuat data wajah yang sudah terdaftar"""
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_face_ids = []
        
        for employee_id, name, face_encoding_blob in face_data:
            if face_encoding_blob:
                try:
                    face_encoding = pickle.loads(face_encoding_blob)
                    self.known_face_encodings.append(face_encoding)
                    self.known_face_names.append(name)
                    self.known_face_ids.append(employee_id)
                except Exception as e:
                    print(f"Error loading face encoding for {name}: {e}")
    
    def capture_face_from_camera(self):
        """Mengambil foto wajah dari kamera"""
        video_capture = cv2.VideoCapture(config.CAMERA_INDEX)
        video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
        video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)
        
        print("Tekan SPACE untuk mengambil foto, atau ESC untuk batal")
        
        face_image = None
        face_encoding = None
        
        while True:
            ret, frame = video_capture.read()
            if not ret:
                break
            
            # Flip untuk efek mirror
            frame = cv2.flip(frame, 1)
            
            # Deteksi wajah untuk preview
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            
            # Gambar kotak di sekitar wajah
            for (top, right, bottom, left) in face_locations:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, "Wajah Terdeteksi", (left, top - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Tampilkan instruksi
            cv2.putText(frame, "SPACE: Ambil Foto | ESC: Batal", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.imshow('Capture Face', frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == 32:  # SPACE
                if len(face_locations) > 0:
                    # Ambil encoding wajah
                    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
                    if len(face_encodings) > 0:
                        face_image = frame.copy()
                        face_encoding = face_encodings[0]
                        break
                    else:
                        print("Gagal mengekstrak fitur wajah")
                else:
                    print("Tidak ada wajah terdeteksi!")
            
            elif key == 27:  # ESC
                break
        
        video_capture.release()
        cv2.destroyAllWindows()
        
        return face_image, face_encoding
    
    def recognize_face_from_camera(self, callback=None):
        """Mengenali wajah dari kamera secara real-time"""
        video_capture = cv2.VideoCapture(config.CAMERA_INDEX)
        video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
        video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)
        
        print("Tekan ESC untuk keluar")
        
        process_this_frame = True
        recognized_employee = None
        
        while True:
            ret, frame = video_capture.read()
            if not ret:
                break
            
            # Flip untuk efek mirror
            frame = cv2.flip(frame, 1)
            
            # Proses setiap frame kedua untuk performa lebih baik
            if process_this_frame:
                # Resize untuk proses lebih cepat
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                
                # Deteksi wajah
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                
                face_names = []
                face_ids = []
                
                for face_encoding in face_encodings:
                    # Cek kecocokan dengan tolerance
                    matches = face_recognition.compare_faces(
                        self.known_face_encodings, 
                        face_encoding, 
                        tolerance=config.TOLERANCE
                    )
                    name = "Unknown"
                    employee_id = None
                    
                    # Hitung jarak wajah untuk validasi tambahan
                    face_distances = face_recognition.face_distance(
                        self.known_face_encodings, 
                        face_encoding
                    )
                    
                    if len(face_distances) > 0:
                        best_match_index = np.argmin(face_distances)
                        min_distance = face_distances[best_match_index]
                        
                        # Validasi ganda: harus match DAN distance di bawah threshold
                        if matches[best_match_index] and min_distance <= config.MAX_FACE_DISTANCE:
                            name = self.known_face_names[best_match_index]
                            employee_id = self.known_face_ids[best_match_index]
                            
                            if callback and recognized_employee != employee_id:
                                recognized_employee = employee_id
                                callback(employee_id, name)
                    
                    face_names.append(name)
                    face_ids.append(employee_id)
            
            process_this_frame = not process_this_frame
            
            # Gambar hasil
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                # Scale back koordinat
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4
                
                # Gambar kotak
                color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                
                # Gambar label
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                cv2.putText(frame, name, (left + 6, bottom - 6),
                           cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
            
            # Tampilkan instruksi
            cv2.putText(frame, "ESC: Keluar", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.imshow('Face Recognition - Absensi', frame)
            
            if cv2.waitKey(1) & 0xFF == 27:  # ESC
                break
        
        video_capture.release()
        cv2.destroyAllWindows()
        
        return recognized_employee
    
    def encode_face_from_image(self, image_path):
        """Mengekstrak face encoding dari file gambar"""
        try:
            image = face_recognition.load_image_file(image_path)
            face_encodings = face_recognition.face_encodings(image)
            
            if len(face_encodings) > 0:
                return face_encodings[0]
            else:
                return None
        except Exception as e:
            print(f"Error encoding face: {e}")
            return None
    
    def detect_face_in_image(self, image):
        """Mendeteksi apakah ada wajah dalam gambar"""
        if isinstance(image, np.ndarray):
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            rgb_image = face_recognition.load_image_file(image)
        
        face_locations = face_recognition.face_locations(rgb_image)
        return len(face_locations) > 0
