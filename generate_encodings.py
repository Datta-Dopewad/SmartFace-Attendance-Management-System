# /DigitalFaceAttendanceSystem/generate_encodings.py

import cv2
import face_recognition
import pickle
import os
import numpy as np
from pathlib import Path
import sqlite3 # <-- Naya import, openpyxl hata diya

print("Starting encoding generator (Sync Mode)...")

# --- Configuration ---
BASE_DIR = Path(__file__).resolve().parent
STUDENTS_DIR = BASE_DIR / "students"
DETAILS_FILE = BASE_DIR / "student_details.txt"
ENCODINGS_DIR = BASE_DIR / "encodings"
ENCODINGS_PATH = ENCODINGS_DIR / "encodings.pkl"
# --- UPDATED: Excel ki jagah DB file ---
DB_FILE = BASE_DIR / "attendance.db" 

# --- Naya Helper Function ---
def get_existing_roll_numbers(conn):
    """Database se saare existing roll numbers ki list nikalta hai."""
    roll_numbers = set()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT roll_no FROM students")
        for row in cursor.fetchall():
            roll_numbers.add(str(row[0]))
        return roll_numbers
    except Exception as e:
        print(f"[DB Error] Existing rolls fetch nahi ho sake: {e}")
        return roll_numbers

def process_and_encode():
    """
    student_details.txt se data padhta hai aur naye students ko
    Database (SQLite) aur encodings.pkl file mein add karta hai.
    """
    
    print("[INFO] Loading student details from student_details.txt...")
    if not DETAILS_FILE.exists():
        print(f"[ERROR] '{DETAILS_FILE}' not found. Please register students first.")
        return

    # --- 1. Database (SQLite) se connect karo ---
    conn = None
    try:
        if not DB_FILE.exists():
            print(f"[ERROR] Database file '{DB_FILE}' nahi mili. Pehle 'main.py' run karke setup complete karein.")
            return
            
        conn = sqlite3.connect(DB_FILE)
        existing_rolls = get_existing_roll_numbers(conn)
        print(f"[INFO] Found {len(existing_rolls)} students already in Database.")
    except Exception as e:
        print(f"[ERROR] Database se connect nahi ho saka: {e}")
        if conn:
            conn.close()
        return

    # --- 2. Existing Encodings load karo ---
    try:
        if ENCODINGS_PATH.exists():
            with open(ENCODINGS_PATH, 'rb') as f:
                data = pickle.load(f)
                known_encodings = data.get("encodings", [])
                known_data = data.get("data", [])
            print(f"[INFO] Loaded {len(known_encodings)} existing encodings.")
        else:
            known_encodings = []
            known_data = []
            print("[INFO] 'encodings.pkl' not found. Will create a new one.")
            
    except Exception as e:
        print(f"[ERROR] Failed to load 'encodings.pkl': {e}")
        conn.close()
        return

    # --- 3. student_details.txt padho aur naye students process karo ---
    new_students_added = 0
    try:
        cursor = conn.cursor()
        with open(DETAILS_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                try:
                    # Format: Name,RollNo,Department,Class,PRN,Contact,DOB,Image_Folder_Path
                    name, roll_no, dept, class_name, prn_no, contact_no, dob, img_folder_path = line.split(',')
                except ValueError:
                    print(f"[WARNING] Skipping malformed line in .txt: {line}")
                    continue
                
                if str(roll_no) in existing_rolls:
                    continue # Student pehle se hi DB mein hai, skip karo
                
                print(f"[INFO] Processing NEW student: {name} ({roll_no})")
                new_students_added += 1

                # A. Student ko Database (SQLite) mein add karo
                cursor.execute("""
                INSERT INTO students (roll_no, name, department, class_name, prn_no, contact_no, dob)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (roll_no, name, dept, class_name, prn_no, contact_no, dob))
                
                student_folder = Path(img_folder_path)
                if not student_folder.exists():
                    print(f"  [WARNING] Image folder not found: {student_folder}. Skipping.")
                    continue
                
                # B. Nayi Encodings add karo
                img_count = 0
                for img_file in student_folder.glob("*.png"):
                    try:
                        img_rgb = face_recognition.load_image_file(str(img_file))
                        boxes = face_recognition.face_locations(img_rgb, model='hog')
                        encodings = face_recognition.face_encodings(img_rgb, boxes)

                        if encodings:
                            known_encodings.append(encodings[0])
                            known_data.append({"roll": roll_no, "name": name})
                            img_count += 1
                        else:
                            print(f"  [WARNING] No face found in {img_file}. Skipping.")
                    except Exception as e:
                        print(f"  [ERROR] Failed to process {img_file}: {e}")

                print(f"  [INFO] Processed {img_count} images for {name}.")
                existing_rolls.add(str(roll_no)) # Taki dobara add na ho

    except Exception as e:
        print(f"[ERROR] Failed to read '{DETAILS_FILE}' or update DB: {e}")
        conn.rollback() # Changes ko reverse karo
        conn.close()
        return

    if new_students_added == 0:
        print("\n[INFO] No new students found in 'student_details.txt'. System is already up-to-date.")
        conn.close()
        return

    # --- 4. Saara data save karo ---
    try:
        conn.commit() # Database mein changes save karo
        print(f"[SUCCESS] {new_students_added} new student(s) added to '{DB_FILE}'")
    except Exception as e:
        print(f"[ERROR] Failed to save to database: {e}")
    finally:
        conn.close() # Connection band karo

    try:
        data_to_save = {"encodings": known_encodings, "data": known_data}
        with open(ENCODINGS_PATH, 'wb') as f:
            pickle.dump(data_to_save, f)
        print(f"[SUCCESS] All {len(known_encodings)} encodings saved to '{ENCODINGS_PATH}'")
    except Exception as e:
        print(f"[ERROR] Failed to save encodings file: {e}")

    print("\nEncoding sync complete.")

if __name__ == "__main__":
    process_and_encode()