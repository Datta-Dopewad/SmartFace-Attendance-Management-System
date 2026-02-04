# /DigitalFaceAttendanceSystem/add_edit_teacher_window.py

import tkinter as tk
from tkinter import ttk, messagebox
import user_manager
import attendance_manager

class AddEditTeacherWindow:
    def __init__(self, parent, refresh_callback, role, current_data=None):
        self.parent = parent
        self.refresh_callback = refresh_callback
        self.role = role.lower()
        self.current_data = current_data
        self.is_edit_mode = (current_data is not None)
        
        self.window = tk.Toplevel(parent)
        title = "Edit Teacher" if self.is_edit_mode else "Add New User"
        self.window.title(title)
        self.window.geometry("400x550") # Thodi height badhayi
        self.window.transient(parent)
        self.window.grab_set()

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TLabel", font=("Helvetica", 11))
        style.configure("TEntry", font=("Helvetica", 11))
        style.configure("TButton", font=("Helvetica", 11, "bold"))
        style.configure("Header.TLabel", font=("Helvetica", 14, "bold"))
        style.configure("TRadiobutton", font=("Helvetica", 11))

        main_frame = ttk.Frame(self.window, padding=20)
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        ttk.Label(main_frame, text=title, style="Header.TLabel").pack(pady=(0, 20))

        # Username
        ttk.Label(main_frame, text="Username:").pack(anchor="w")
        self.username_entry = ttk.Entry(main_frame, width=40)
        self.username_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Password
        password_label_text = "Password (khaali chhod dein agar change nahi karna):" if self.is_edit_mode else "Password:"
        ttk.Label(main_frame, text=password_label_text).pack(anchor="w")
        self.pass_entry = ttk.Entry(main_frame, show="*", width=40)
        self.pass_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Full Name
        ttk.Label(main_frame, text="Full Name (e.g., Prof. Joshi):").pack(anchor="w")
        self.name_entry = ttk.Entry(main_frame, width=40)
        self.name_entry.pack(fill=tk.X, pady=(0, 10))
        
        # --- NAYA FIELD: Department ---
        ttk.Label(main_frame, text="Department (e.g., IT, Mechanical):").pack(anchor="w")
        self.dept_entry = ttk.Entry(main_frame, width=40)
        self.dept_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Contact No
        ttk.Label(main_frame, text="Contact No:").pack(anchor="w")
        self.contact_entry = ttk.Entry(main_frame, width=40)
        self.contact_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Subject
        ttk.Label(main_frame, text="Subject Specialization:").pack(anchor="w")
        self.subject_entry = ttk.Entry(main_frame, width=40)
        self.subject_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Role
        ttk.Label(main_frame, text="Role:").pack(anchor="w")
        self.role_var = tk.StringVar(value="Teacher")
        role_frame = ttk.Frame(main_frame)
        role_frame.pack(anchor="w", pady=(0, 15))
        ttk.Radiobutton(role_frame, text="Teacher", variable=self.role_var, value="Teacher").pack(side=tk.LEFT)
        ttk.Radiobutton(role_frame, text="Admin", variable=self.role_var, value="Admin").pack(side=tk.LEFT, padx=10)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=10)
        ttk.Button(button_frame, text="Save User", command=self.save).pack(side=tk.LEFT, expand=True, padx=5, ipady=5)
        ttk.Button(button_frame, text="Cancel", command=self.window.destroy).pack(side=tk.RIGHT, expand=True, padx=5, ipady=5)

        # Agar Edit mode hai, toh fields populate karo
        if self.is_edit_mode:
            self.username_entry.insert(0, self.current_data["username"])
            self.username_entry.config(state="readonly")
            self.name_entry.insert(0, self.current_data["full_name"])
            self.contact_entry.insert(0, self.current_data.get("contact_no", ""))
            self.subject_entry.insert(0, self.current_data.get("subject", ""))
            self.dept_entry.insert(0, self.current_data.get("department", "")) # Naya
            self.role_var.set(self.current_data["role"])

    def save(self):
        try:
            username = self.username_entry.get().strip()
            password = self.pass_entry.get()
            role = self.role_var.get()
            full_name = self.name_entry.get().strip()
            department = self.dept_entry.get().strip() # Naya
            contact = self.contact_entry.get().strip()
            subject = self.subject_entry.get().strip()

            if not all([username, full_name, department]):
                raise ValueError("Username, Full Name, aur Department zaroori hai.")
            if role == "Admin": # Admin ka koi department nahi hota
                department = None
            
            if self.is_edit_mode:
                # --- Edit Logic ---
                new_data = {
                    "full_name": full_name, "contact_no": contact, 
                    "subject": subject, "department": department, "role": role
                }
                user_manager.update_user_profile(username, new_data)
                
                if password:
                    new_hash = user_manager.hash_password(password)
                    conn = user_manager.create_connection()
                    conn.execute("UPDATE users SET password_hash = ? WHERE username = ?", (new_hash, username))
                    conn.commit()
                    conn.close()
                
                attendance_manager.log_activity(self.role, f"Edited user profile: {username}")
                messagebox.showinfo("Success", f"User '{username}' ki details update ho gayi hain.", parent=self.window)
            
            else:
                # --- Add New Logic ---
                if not password:
                    raise ValueError("Naye user ke liye password zaroori hai.")
                
                user_manager.add_new_user(username, password, role, full_name, contact, subject, department)
                attendance_manager.log_activity(self.role, f"Added new user: {username} (Role: {role})")
                messagebox.showinfo("Success", f"Naya user '{username}' banaya gaya.", parent=self.window)

            self.refresh_callback()
            self.window.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Save nahi ho saka: {e}", parent=self.window)

def show_add_edit_window(parent, refresh_callback, role, current_data=None):
    AddEditTeacherWindow(parent, refresh_callback, role, current_data)