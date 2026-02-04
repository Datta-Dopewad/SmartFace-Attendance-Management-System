# /DigitalFaceAttendanceSystem/backup_manager.py

import zipfile
import os
from pathlib import Path
from datetime import datetime
import attendance_manager # Hamare main file paths ke liye

# attendance_manager se zaroori file paths import karo
BASE_DIR = attendance_manager.BASE_DIR
DB_FILE = attendance_manager.DB_FILE
ENCODINGS_PATH = attendance_manager.ENCODINGS_PATH

def create_backup(target_zip_path):
    """
    System ki 2 zaroori files (database aur encodings) ko ek zip file mein save karta hai.
    """
    try:
        # Check karo ki files maujood hain
        if not DB_FILE.exists():
            raise FileNotFoundError("Database file 'attendance.db' nahi mili.")
        if not ENCODINGS_PATH.exists():
            raise FileNotFoundError("Encodings file 'encodings.pkl' nahi mili.")
            
        print(f"Backup shuru ho raha hai -> {target_zip_path}")
        
        # Ek nayi zip file banao
        with zipfile.ZipFile(target_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Database file ko add karo
            zipf.write(DB_FILE, arcname="attendance.db")
            # Encodings file ko add karo
            zipf.write(ENCODINGS_PATH, arcname="encodings.pkl")
            
        print("Backup safaltapoorvak complete hua.")
        return True
        
    except Exception as e:
        # Error hone par raise karo taaki GUI use pakad sake
        raise Exception(f"Backup failed: {e}")

def restore_backup(source_zip_path):
    """
    Ek backup .zip file se system ko restore karta hai.
    """
    try:
        # Check karo ki file valid zip hai
        if not zipfile.is_zipfile(source_zip_path):
            raise zipfile.BadZipFile("Yeh ek valid zip file nahi hai.")
            
        with zipfile.ZipFile(source_zip_path, 'r') as zipf:
            file_list = zipf.namelist()
            
            # Check karo ki zip file mein zaroori files hain
            if "attendance.db" not in file_list or "encodings.pkl" not in file_list:
                raise FileNotFoundError("Yeh ek invalid backup file hai (zaroori files nahi mili).")
            
            print(f"Restore shuru ho raha hai -> {source_zip_path}")
            
            # Saari files ko project ke main folder mein extract (overwrite) karo
            zipf.extractall(BASE_DIR)
        
        print("Restore safaltapoorvak complete hua.")
        return True
        
    except Exception as e:
        raise Exception(f"Restore failed: {e}")