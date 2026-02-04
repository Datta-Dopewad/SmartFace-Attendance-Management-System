# /DigitalFaceAttendanceSystem/edit_student_window.py

import tkinter as tk
from tkinter import ttk, messagebox
import attendance_manager

# --- UPDATED: 'role' parameter add karo ---
class EditStudentWindow:
    def __init__(self, parent, roll_no, current_data, refresh_callback, role):
        self.parent = parent
        self.roll_no = roll_no
        self.current_data = current_data
        self.refresh_callback = refresh_callback
        self.role = role.lower() # 'admin'
        
        self.window = tk.Toplevel(parent)
        self.window.title(f"Edit Student: {current_data['name']}")
        self.window.state('zoomed')
        self.window.transient(parent)
        self.window.grab_set()

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TLabel", font=("Helvetica", 11))
        style.configure("TEntry", font=("Helvetica", 11))
        style.configure("TButton", font=("Helvetica", 11, "bold"))
        style.configure("Header.TLabel", font=("Helvetica", 16, "bold"))

        main_frame = ttk.Frame(self.window, padding=20)
        main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        ttk.Label(main_frame, text=f"Editing Student: {current_data['name']}", style="Header.TLabel").pack(pady=(0, 20))

        # Form fields...
        ttk.Label(main_frame, text="Roll No:").pack(anchor="w")
        self.roll_entry = ttk.Entry(main_frame, font=("Helvetica", 11, "bold"), width=40)
        self.roll_entry.insert(0, current_data["roll_no"])
        self.roll_entry.config(state="readonly")
        self.roll_entry.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(main_frame, text="Name:").pack(anchor="w")
        self.name_entry = ttk.Entry(main_frame, width=40)
        self.name_entry.insert(0, current_data["name"])
        self.name_entry.config(state="readonly")
        self.name_entry.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(main_frame, text="Department:").pack(anchor="w")
        self.dept_entry = ttk.Entry(main_frame, width=40)
        self.dept_entry.insert(0, current_data["department"])
        self.dept_entry.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(main_frame, text="Class Name:").pack(anchor="w")
        self.class_entry = ttk.Entry(main_frame, width=40)
        self.class_entry.insert(0, current_data["class_name"])
        self.class_entry.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(main_frame, text="PRN No:").pack(anchor="w")
        self.prn_entry = ttk.Entry(main_frame, width=40)
        self.prn_entry.insert(0, current_data["prn_no"])
        self.prn_entry.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(main_frame, text="Contact No:").pack(anchor="w")
        self.contact_entry = ttk.Entry(main_frame, width=40)
        self.contact_entry.insert(0, current_data["contact_no"])
        self.contact_entry.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(main_frame, text="Date of Birth (YYYY-MM-DD):").pack(anchor="w")
        self.dob_entry = ttk.Entry(main_frame, width=40)
        self.dob_entry.insert(0, current_data["dob"])
        self.dob_entry.pack(fill=tk.X, pady=(0, 10))
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=10)
        
        ttk.Button(button_frame, text="Save Changes", command=self.save_changes).pack(side=tk.LEFT, expand=True, padx=5, ipady=5)
        ttk.Button(button_frame, text="Cancel", command=self.window.destroy).pack(side=tk.RIGHT, expand=True, padx=5, ipady=5)

    def save_changes(self):
        new_data = {
            "department": self.dept_entry.get().strip(),
            "class_name": self.class_entry.get().strip(),
            "prn_no": self.prn_entry.get().strip(),
            "contact_no": self.contact_entry.get().strip(),
            "dob": self.dob_entry.get().strip()
        }
        
        if not all(new_data.values()):
            messagebox.showerror("Validation Error", "Koi bhi field khaali nahi ho sakti.", parent=self.window)
            return
            
        try:
            attendance_manager.update_student_data(self.roll_no, new_data)
            
            # --- NAYA LOG ---
            attendance_manager.log_activity(self.role, f"Edited student details. Roll: {self.roll_no}")
            
            messagebox.showinfo("Success", "Student details successfully update ho gayi hain.", parent=self.window)
            self.refresh_callback()
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("Update Error", f"Details update nahi ho sakin: {e}", parent=self.window)

# --- UPDATED: 'role' parameter add karo ---
def show_edit_window(parent, roll_no, current_data, refresh_callback, role):
    EditStudentWindow(parent, roll_no, current_data, refresh_callback, role)