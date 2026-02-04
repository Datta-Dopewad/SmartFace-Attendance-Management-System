# Digital Face Attendance System for Rural Schools 🏫🛡️

A professional, offline-first Face Recognition Attendance System built with Python. Designed specifically for educational institutions to automate attendance with high security, departmental control, and liveness detection.

---

## 🚀 Key Features

* **Dual-Role Management:** Specialized dashboards for **Admin** (Full System Access) and **Teacher** (Department-specific access).
* **Face Recognition Engine:** Powered by `dlib` and `face_recognition` with 99.38% accuracy.
* **Security & Anti-Spoofing:**
    * **Liveness Detection:** Prevents proxy attendance using photos/videos by detecting eye blinks.
    * **Account Lockout:** Automatically locks accounts for 30 minutes after 5 failed login attempts.
    * **Activity Audit Trail:** Logs every action (logins, deletions, settings changes) with timestamps.
* **Departmental Isolation:** Teachers can only manage and view students within their assigned department (e.g., IT, Mechanical).
* **Smart Reporting:** * Export attendance logs to styled Excel files.
    * Automated "Defaulter List" generation.
    * Visual Analytics: 30-day attendance trend charts.
* **Robust Data Management:** * SQLite Database for fast queries.
    * Bulk Student Import via Excel.
    * System Backup & Restore functionality.

---

## 🛠️ Tech Stack

* **Language:** Python 3.9.13
* **GUI Framework:** Tkinter (Custom Styled)
* **Computer Vision:** OpenCV, Dlib, Face_Recognition
* **Database:** SQLite3
* **Data Analysis:** Pandas, Matplotlib
* **File Handling:** OpenPyXL

---

## 📂 Project Structure

```plaintext
DigitalFaceAttendanceSystem/
├── dataset/               # Local storage for student photos (Git Ignored)
├── students/              # Local student records (Git Ignored)
├── unknown_logs/          # Captured images of unrecognized faces
├── encodings/             # Serialized face embeddings (encodings.pkl)
├── backup/                # Optional system backups
├── main.py                # Entry point (Run this to start)
├── login_screen.py        # Secure authentication layer
├── dashboard.py           # User navigation & UI logic
├── attendance_manager.py  # Recognition & attendance logic
├── user_manager.py        # Admin & Teacher management
├── shape_predictor_68_face_landmarks.dat  # Dlib model for Liveness
├── requirements.txt       # List of libraries
└── .gitignore             # Privacy and security filter

## ⚙️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/Datta-Dopewad/DigitalFaceAttendanceSystem.git](https://github.com/Datta-Dopewad/DigitalFaceAttendanceSystem.git)
   cd DigitalFaceAttendanceSystem
