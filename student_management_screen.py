# /DigitalFaceAttendanceSystem/student_management_screen.py

import tkinter as tk
from tkinter import ttk, Label
import student_management_logic # Logic file import ki

# --- UPDATED: 'role' aur 'department' parameters add kiye ---
class StudentManagementScreen:
    def __init__(self, parent, role, department):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Register New Student")
        self.window.state('zoomed')
        
        # --- UPDATED: 'role' aur 'department' ko logic class mein pass karo ---
        self.logic = student_management_logic.StudentManagementLogic(self, role, department)

        # --- Main Layout ---
        self.main_frame = ttk.Frame(self.window, padding=20)
        self.main_frame.pack(expand=True, fill=tk.BOTH)

        # --- Form Frame (Left) ---
        self.form_frame = ttk.Frame(self.main_frame, padding=10)
        self.form_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)

        ttk.Label(self.form_frame, text="Register Student", font=("Helvetica", 16, "bold")).pack(pady=10)

        # Form fields...
        ttk.Label(self.form_frame, text="Roll No:").pack(anchor="w", pady=5)
        self.roll_entry = ttk.Entry(self.form_frame, width=30, font=("Helvetica", 12))
        self.roll_entry.pack(fill=tk.X)

        ttk.Label(self.form_frame, text="Name:").pack(anchor="w", pady=5)
        self.name_entry = ttk.Entry(self.form_frame, width=30, font=("Helvetica", 12))
        self.name_entry.pack(fill=tk.X)

        ttk.Label(self.form_frame, text="Department:").pack(anchor="w", pady=5)
        self.dept_entry = ttk.Entry(self.form_frame, width=30, font=("Helvetica", 12))
        self.dept_entry.pack(fill=tk.X)

        ttk.Label(self.form_frame, text="Class Name:").pack(anchor="w", pady=5)
        self.class_entry = ttk.Entry(self.form_frame, width=30, font=("Helvetica", 12))
        self.class_entry.pack(fill=tk.X)

        ttk.Label(self.form_frame, text="PRN No:").pack(anchor="w", pady=5)
        self.prn_entry = ttk.Entry(self.form_frame, width=30, font=("Helvetica", 12))
        self.prn_entry.pack(fill=tk.X)

        ttk.Label(self.form_frame, text="Contact No:").pack(anchor="w", pady=5)
        self.contact_entry = ttk.Entry(self.form_frame, width=30, font=("Helvetica", 12))
        self.contact_entry.pack(fill=tk.X)

        ttk.Label(self.form_frame, text="Date of Birth (YYYY-MM-DD):").pack(anchor="w", pady=5)
        self.dob_entry = ttk.Entry(self.form_frame, width=30, font=("Helvetica", 12))
        self.dob_entry.pack(fill=tk.X)
        
        self.capture_status_label = ttk.Label(self.form_frame, text="Captured 0/3 images", font=("Helvetica", 10, "italic"))
        self.capture_status_label.pack(pady=10)
        
        # --- NAYA: Agar Teacher hai, toh department field ko disable karo ---
        if self.logic.role == "Teacher":
            self.dept_entry.insert(0, self.logic.department)
            self.dept_entry.config(state="readonly")

        # --- Camera Frame (Right) ---
        self.camera_frame = ttk.Frame(self.main_frame)
        self.camera_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=10)

        self.video_label = Label(self.camera_frame, bg="black")
        self.video_label.pack(expand=True, fill=tk.BOTH, pady=10)

        # --- Button Frame (Bottom) ---
        self.button_frame = ttk.Frame(self.form_frame)
        self.button_frame.pack(side=tk.BOTTOM, pady=20, fill=tk.X)

        self.start_cam_button = ttk.Button(self.button_frame, text="Start Camera", command=self.logic.start_webcam)
        self.start_cam_button.pack(fill=tk.X, pady=2)
        self.choose_file_button = ttk.Button(self.button_frame, text="Choose File(s)", command=self.logic.choose_file)
        self.choose_file_button.pack(fill=tk.X, pady=2)
        self.capture_button = ttk.Button(self.button_frame, text="Capture from Webcam (0)", command=self.logic.capture_image, state=tk.DISABLED)
        self.capture_button.pack(fill=tk.X, pady=2)
        self.save_button = ttk.Button(self.button_frame, text="Save Student", command=self.logic.save_student, state=tk.DISABLED)
        self.save_button.pack(fill=tk.X, pady=(10, 2))
        self.reset_button = ttk.Button(self.button_frame, text="Reset", command=self.logic.reset_form)
        self.reset_button.pack(fill=tk.X, pady=2)

        self.window.protocol("WM_DELETE_WINDOW", self.logic.on_close)

# --- UPDATED: 'role' aur 'department' parameters add kiye ---
def show_student_management(parent, role, department):
    StudentManagementScreen(parent, role, department)