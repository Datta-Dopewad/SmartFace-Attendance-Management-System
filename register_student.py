# /DigitalFaceAttendanceSystem/register_student.py

import cv2
import os
import re

# --- Configuration ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STUDENTS_DIR = os.path.join(BASE_DIR, "students")
DETAILS_FILE = os.path.join(BASE_DIR, "student_details.txt")
CAPTURE_COUNT = 1

def sanitize_filename(name):
    name = re.sub(r'\s+', '_', name)
    name = re.sub(r'[^\w\-]', '', name)
    return name

def register_student():
    print("=== Student Registration / Image Capture (Console) ===")
    print("-" * 50)

    # --- 1. Get Student Details ---
    while True:
        name = input("Enter Full Name: ").strip()
        if name: break
        print("Error: Name cannot be empty.")

    while True:
        roll_no = input("Enter Roll Number: ").strip()
        if roll_no: break
        print("Error: Roll number cannot be empty.")
    
    # --- UPDATED: Add new fields ---
    department = input("Enter Department: ").strip()
    class_name = input("Enter Class Name: ").strip()
    prn_no = input("Enter PRN No: ").strip()
    contact_no = input("Enter Contact No: ").strip()
    dob = input("Enter DOB (YYYY-MM-DD): ").strip()

    # --- 2. Setup Folder ---
    sanitized_name = sanitize_filename(name)
    if not sanitized_name:
        print("[ERROR] Sanitized name is empty. Cannot create folder.")
        return

    os.makedirs(STUDENTS_DIR, exist_ok=True)
    student_folder_path = os.path.join(STUDENTS_DIR, sanitized_name)

    if os.path.exists(student_folder_path):
        print(f"[WARNING] Folder '{student_folder_path}' already exists.")
        overwrite = input("Do you want to overwrite (save new image)? (y/n): ").strip().lower()
        if overwrite != 'y':
            print("[INFO] Registration cancelled.")
            return
        else:
            print("[INFO] Proceeding to save new image...")
    
    os.makedirs(student_folder_path, exist_ok=True)
    print(f"[INFO] Saving image to: {student_folder_path}")

    # --- 3. Open Webcam and Capture ---
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Could not open webcam.")
        return

    print(f"\nCamera opened. Press 'q' to capture {CAPTURE_COUNT} image.")
    print("-" * 50)

    img_counter = 0
    while img_counter < CAPTURE_COUNT:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to grab frame.")
            break

        window_title = f"Capture Image {img_counter + 1} of {CAPTURE_COUNT} (Press 'q')"
        cv2.imshow(window_title, frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            img_counter += 1
            img_name = f"{sanitized_name}.png"
            img_path = os.path.join(student_folder_path, img_name)
            
            try:
                cv2.imwrite(img_path, frame)
                print(f"[INFO] Image {img_counter} saved to: {img_path}")
            except Exception as e:
                print(f"[ERROR] Could not save image: {e}")
                img_counter -= 1 
        elif key == 27:
            print("[INFO] Registration cancelled by user.")
            break
    
    cap.release()
    cv2.destroyAllWindows()

    # --- 4. Save Details ---
    if img_counter == CAPTURE_COUNT:
        # --- UPDATED: New data_line format ---
        # Format: Name,RollNo,Department,Class,PRN,Contact,DOB,Image_Folder_Path
        data_line = f"{name},{roll_no},{department},{class_name},{prn_no},{contact_no},{dob},{student_folder_path}\n"
        
        try:
            with open(DETAILS_FILE, "a") as f:
                f.write(data_line)
            print(f"\n[INFO] Student details appended to: {DETAILS_FILE}")
            print("[SUCCESS] Registration complete!")
            print("\n*** IMPORTANT: Run 'generate_encodings.py' to sync with the main system. ***")
        except Exception as e:
            print(f"[ERROR] Failed to write details to file: {e}")
    else:
        print(f"\n[INFO] Registration incomplete. Details not saved.")

if __name__ == "__main__":
    register_student()