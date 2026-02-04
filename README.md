# Digital Face Attendance System for Rural Schools 🏫🛡️

A professional, offline-first Face Recognition Attendance System built with Python. Designed specifically for educational institutions to automate attendance with high security, departmental control, and liveness detection.



## 🚀 Key Features

- **Dual-Role Management:** Specialized dashboards for **Admin** (Full System Access) and **Teacher** (Department-specific access).
- **Face Recognition Engine:** Powered by `dlib` and `face_recognition` with 99.38% accuracy.
- **Security & Anti-Spoofing:** - **Liveness Detection:** Prevents proxy attendance using photos/videos by detecting eye blinks.
    - **Account Lockout:** Automatically locks accounts for 30 minutes after 5 failed login attempts.
    - **Activity Audit Trail:** Logs every action (logins, deletions, settings changes) with timestamps.
- **Departmental Isolation:** Teachers can only manage and view students within their assigned department (e.g., IT, Mechanical).
- **Smart Reporting:** - Export attendance logs to styled Excel files.
    - Automated "Defaulter List" generation.
    - Visual Analytics: 30-day attendance trend charts.
- **Robust Data Management:** - SQLite Database for fast queries.
    - Bulk Student Import via Excel.
    - System Backup & Restore functionality.

## 🛠️ Tech Stack

- **Language:** Python 3.x
- **GUI Framework:** Tkinter (Custom Styled)
- **Computer Vision:** OpenCV, Dlib, Face_Recognition
- **Database:** SQLite3
- **Data Analysis:** Pandas, Matplotlib
- **File Handling:** OpenPyXL

## ⚙️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-username/DigitalFaceAttendanceSystem.git](https://github.com/your-username/DigitalFaceAttendanceSystem.git)
   cd DigitalFaceAttendanceSystem
