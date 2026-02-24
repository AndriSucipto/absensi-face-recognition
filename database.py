"""
Modul Database untuk Sistem Absensi Face Recognition
Mengelola data pegawai dan catatan absensi
"""
import sqlite3
from datetime import datetime
import config

class DatabaseManager:
    def __init__(self):
        self.db_path = config.DATABASE_PATH
        self.init_database()
    
    def get_connection(self):
        """Membuat koneksi ke database"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Inisialisasi tabel database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabel Pegawai
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                department TEXT,
                position TEXT,
                image_path TEXT,
                face_encoding BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabel Absensi
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id TEXT NOT NULL,
                check_in_time TIMESTAMP,
                check_out_time TIMESTAMP,
                date DATE NOT NULL,
                status TEXT DEFAULT 'Hadir',
                FOREIGN KEY (employee_id) REFERENCES employees (employee_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_employee(self, employee_id, name, department, position, image_path, face_encoding):
        """Menambahkan pegawai baru"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO employees (employee_id, name, department, position, image_path, face_encoding)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (employee_id, name, department, position, image_path, face_encoding))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_all_employees(self):
        """Mendapatkan semua data pegawai"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT employee_id, name, department, position FROM employees")
        employees = cursor.fetchall()
        
        conn.close()
        return employees
    
    def get_employee(self, employee_id):
        """Mendapatkan data pegawai berdasarkan ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM employees WHERE employee_id = ?", (employee_id,))
        employee = cursor.fetchone()
        
        conn.close()
        return employee
    
    def get_all_face_encodings(self):
        """Mendapatkan semua face encoding untuk pengenalan wajah"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT employee_id, name, face_encoding FROM employees")
        data = cursor.fetchall()
        
        conn.close()
        return data
    
    def record_attendance(self, employee_id, attendance_type='check_in'):
        """Mencatat absensi pegawai"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        today = datetime.now().date()
        now = datetime.now()
        
        # Cek apakah sudah ada record hari ini
        cursor.execute("""
            SELECT id, check_in_time, check_out_time FROM attendance 
            WHERE employee_id = ? AND date = ?
        """, (employee_id, today))
        
        existing = cursor.fetchone()
        
        if attendance_type == 'check_in':
            if existing:
                # Sudah check-in hari ini
                conn.close()
                return False, "Sudah melakukan check-in hari ini"
            else:
                # Insert check-in baru
                cursor.execute("""
                    INSERT INTO attendance (employee_id, check_in_time, date)
                    VALUES (?, ?, ?)
                """, (employee_id, now, today))
                conn.commit()
                conn.close()
                return True, "Check-in berhasil"
        
        elif attendance_type == 'check_out':
            if existing:
                if existing[2]:  # Sudah check-out
                    conn.close()
                    return False, "Sudah melakukan check-out hari ini"
                else:
                    # Update check-out
                    cursor.execute("""
                        UPDATE attendance 
                        SET check_out_time = ?
                        WHERE id = ?
                    """, (now, existing[0]))
                    conn.commit()
                    conn.close()
                    return True, "Check-out berhasil"
            else:
                conn.close()
                return False, "Belum melakukan check-in"
    
    def get_attendance_today(self):
        """Mendapatkan semua absensi hari ini"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        today = datetime.now().date()
        
        cursor.execute("""
            SELECT e.employee_id, e.name, a.check_in_time, a.check_out_time, a.status
            FROM attendance a
            JOIN employees e ON a.employee_id = e.employee_id
            WHERE a.date = ?
            ORDER BY a.check_in_time DESC
        """, (today,))
        
        attendance = cursor.fetchall()
        conn.close()
        return attendance
    
    def get_attendance_history(self, employee_id=None, start_date=None, end_date=None):
        """Mendapatkan riwayat absensi"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT e.employee_id, e.name, a.date, a.check_in_time, a.check_out_time, a.status
            FROM attendance a
            JOIN employees e ON a.employee_id = e.employee_id
            WHERE 1=1
        """
        params = []
        
        if employee_id:
            query += " AND e.employee_id = ?"
            params.append(employee_id)
        
        if start_date:
            query += " AND a.date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND a.date <= ?"
            params.append(end_date)
        
        query += " ORDER BY a.date DESC, a.check_in_time DESC"
        
        cursor.execute(query, params)
        history = cursor.fetchall()
        
        conn.close()
        return history
    
    def delete_employee(self, employee_id):
        """Menghapus pegawai"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM employees WHERE employee_id = ?", (employee_id,))
            cursor.execute("DELETE FROM attendance WHERE employee_id = ?", (employee_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting employee: {e}")
            return False
