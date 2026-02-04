# /DigitalFaceAttendanceSystem/user_manager.py

import sqlite3
import hashlib
from pathlib import Path
import attendance_manager # DB file path ke liye
from datetime import datetime, timedelta

DB_FILE = attendance_manager.DB_FILE
LOCKOUT_DURATION_MINUTES = 30
MAX_FAILED_ATTEMPTS = 5

def hash_password(password):
    """Password ko SHA-256 mein hash karta hai."""
    return hashlib.sha256(password.encode()).hexdigest()

def create_connection():
    """Database connection banata hai."""
    return attendance_manager.create_connection()

def setup_users():
    """Default 'admin' aur 'teacher' users banata hai agar woh maujood nahi hain."""
    conn = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        
        # Check 'admin'
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        if not cursor.fetchone():
            cursor.execute("""
            INSERT INTO users (username, password_hash, role, full_name, failed_attempts, lockout_until, department)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ('admin', hash_password('admin'), 'Admin', 'Administrator', 0, None, None)) # Admin ka koi dept nahi
            print("Default 'admin' user banaya gaya.")

        # Check 'teacher'
        cursor.execute("SELECT * FROM users WHERE username = 'teacher'")
        if not cursor.fetchone():
            cursor.execute("""
            INSERT INTO users (username, password_hash, role, full_name, failed_attempts, lockout_until, department)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ('teacher', hash_password('teacher'), 'Teacher', 'Default Teacher', 0, None, 'Unassigned')) # Default dept
            print("Default 'teacher' user banaya gaya.")
            
        # Default settings
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", ('liveness_check', 'False'))
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", ('unknown_logging', 'True'))
        
        conn.commit()
    except Exception as e:
        print(f"Error setting up default users/settings: {e}")
    finally:
        if conn:
            conn.close()

def verify_user(username, password):
    """
    Username aur password ko check karta hai aur lockout logic handle karta hai.
    Returns: (is_valid, role, username, department, message_or_lock_time)
    """
    conn = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT password_hash, role, failed_attempts, lockout_until, department FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        
        if result:
            stored_hash, role, failed_attempts, lockout_until, department = result
            
            # 1. Check Lockout
            if lockout_until:
                lockout_time = datetime.fromisoformat(lockout_until)
                if datetime.now() < lockout_time:
                    remaining_seconds = int((lockout_time - datetime.now()).total_seconds())
                    return (False, None, None, None, remaining_seconds) 

            # 2. Check Password
            hashed_password_to_check = hash_password(password)
            
            if stored_hash == hashed_password_to_check:
                # Sahi password
                cursor.execute("UPDATE users SET failed_attempts = 0, lockout_until = NULL WHERE username = ?", (username,))
                conn.commit()
                # 'Admin' ka department hamesha None (sab access) hota hai
                user_dept = None if role == 'Admin' else department 
                return (True, role, username, user_dept, "Login successful")
            else:
                # Galat password
                failed_attempts += 1
                if failed_attempts >= MAX_FAILED_ATTEMPTS:
                    lock_time = datetime.now() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
                    lock_time_str = lock_time.isoformat()
                    cursor.execute("UPDATE users SET failed_attempts = ?, lockout_until = ? WHERE username = ?", (failed_attempts, lock_time_str, username))
                    conn.commit()
                    attendance_manager.log_activity(username, f"ACCOUNT LOCKED due to {failed_attempts} failed attempts.")
                    return (False, None, None, None, LOCKOUT_DURATION_MINUTES * 60)
                else:
                    cursor.execute("UPDATE users SET failed_attempts = ? WHERE username = ?", (failed_attempts, username))
                    conn.commit()
                    return (False, None, None, None, "Invalid password")
        
        return (False, None, None, None, "Invalid username")
            
    except Exception as e:
        print(f"Error verifying user: {e}")
        return (False, None, None, None, "Database error")
    finally:
        if conn:
            conn.close()

def get_lockout_status(username):
    """Check karta hai ki user locked hai ya nahi."""
    conn = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT lockout_until FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        
        if result and result[0]:
            lockout_time = datetime.fromisoformat(result[0])
            if datetime.now() < lockout_time:
                return int((lockout_time - datetime.now()).total_seconds())
        return 0
    except Exception as e:
        print(f"Error checking lockout status: {e}")
        return 0
    finally:
        if conn:
            conn.close()

def change_password(username, old_password, new_password):
    """User ka password badalta hai."""
    is_valid, _, _, _, _ = verify_user(username, old_password)
    if not is_valid:
        # Check karo ki kya yeh galat password tha ya lockout
        if isinstance(_, int): # Agar time return hua (locked)
             raise ValueError(f"Account locked hai. { _ // 60 } minutes baad try karein.")
        raise ValueError("Purana password galat hai.")
        
    conn = None
    try:
        conn = create_connection()
        new_hash = hash_password(new_password)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password_hash = ?, failed_attempts = 0, lockout_until = NULL WHERE username = ?", (new_hash, username))
        conn.commit()
        return True
    except Exception as e:
        raise Exception(f"Naya password save nahi ho saka: {e}")
    finally:
        if conn:
            conn.close()

def get_setting(key):
    conn = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        result = cursor.fetchone()
        if result:
            return result[0] == 'True'
        else:
            return True if key == 'unknown_logging' else False
    except Exception as e:
        print(f"Error getting setting {key}: {e}")
        return False
    finally:
        if conn:
            conn.close()

def save_setting(key, value):
    conn = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving setting {key}: {e}")
        return False

def get_user_profile(username):
    """Ek user ki profile details DB se nikalta hai."""
    conn = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username, role, full_name, contact_no, subject_specialization, department FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        if row:
            return {
                "username": row[0], "role": row[1], "full_name": row[2],
                "contact_no": row[3], "subject": row[4], "department": row[5] # Naya
            }
        return None
    except Exception as e:
        print(f"Error getting user profile: {e}")
        return None
    finally:
        if conn:
            conn.close()

def update_user_profile(username, new_data):
    """Ek user ki profile details update karta hai."""
    conn = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE users 
        SET full_name = ?, contact_no = ?, subject_specialization = ?, department = ?, role = ?
        WHERE username = ?
        """, (
            new_data["full_name"], new_data["contact_no"], 
            new_data["subject"], new_data["department"], new_data["role"], username
        ))
        conn.commit()
        return True
    except Exception as e:
        raise Exception(f"Profile update karne mein error: {e}")
    finally:
        if conn:
            conn.close()

def get_all_users_list():
    """Sabhi users (Admins aur Teachers) ki list nikalta hai."""
    conn = None
    users_list = []
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username, full_name, role, department, contact_no, subject_specialization FROM users ORDER BY role, username")
        for row in cursor.fetchall():
            users_list.append(list(row))
        return users_list
    except Exception as e:
        print(f"Error getting all users: {e}")
        return []
    finally:
        if conn:
            conn.close()

def add_new_user(username, password, role, full_name, contact, subject, department):
    """Admin dwara naya user (Teacher) add karta hai."""
    if not all([username, password, role, full_name, department]):
        raise ValueError("Username, Password, Role, Full Name aur Department zaroori hai.")
    
    conn = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            raise ValueError(f"Username '{username}' pehle se maujood hai.")
        
        cursor.execute("""
        INSERT INTO users (username, password_hash, role, full_name, contact_no, subject_specialization, department, failed_attempts, lockout_until)
        VALUES (?, ?, ?, ?, ?, ?, ?, 0, NULL)
        """, (username, hash_password(password), role, full_name, contact, subject, department))
        conn.commit()
        return True
    except Exception as e:
        raise Exception(f"Naya user add karne mein error: {e}")
    finally:
        if conn:
            conn.close()

def delete_user(username):
    """Ek user ko delete karta hai (Admin ko chhodkar)."""
    if username == 'admin':
        raise ValueError("Default 'admin' user ko delete nahi kiya jaa sakta.")
    conn = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE username = ?", (username,))
        conn.commit()
        if cursor.rowcount == 0:
            raise ValueError(f"User '{username}' nahi mila.")
        return True
    except Exception as e:
        raise Exception(f"User delete karne mein error: {e}")
    finally:
        if conn:
            conn.close()