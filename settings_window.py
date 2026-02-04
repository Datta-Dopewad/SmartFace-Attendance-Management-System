# /DigitalFaceAttendanceSystem/settings_window.py

import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog 
import user_manager
import backup_manager 
import attendance_manager 
from datetime import datetime 
import os 

class SettingsWindow:
    def __init__(self, parent, role, username):
        self.parent = parent
        self.username = username
        self.role = role
        
        self.window = tk.Toplevel(parent)
        self.window.title(f"Settings - ({self.username})")
        self.window.state('zoomed') 
        self.window.configure(bg='#f0f2f5') 
        
        self.window.transient(parent)
        self.window.grab_set()

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TLabel", font=("Helvetica", 11), background="#f0f2f5")
        style.configure("TEntry", font=("Helvetica", 11))
        style.configure("TButton", font=("Helvetica", 11, "bold"))
        style.configure("Header.TLabel", font=("Helvetica", 14, "bold"), background="#f0f2f5")
        style.configure("TCheckbutton", font=("Helvetica", 11), background="#f0f2f5")
        style.configure("Card.TFrame", background="white", relief="solid", borderwidth=1)
        style.configure("Danger.TButton", font=("Helvetica", 11, "bold"), background="#dc3545", foreground="white") 
        style.map("Danger.TButton", background=[('active', '#c82333')])
        
        # Naya Style (Warning Button)
        style.configure("Warning.TButton", font=("Helvetica", 11, "bold"), background="#ffc107", foreground="black")
        style.map("Warning.TButton", background=[('active', '#e0a800')])

        style.configure("white.TLabel", background="white")
        style.configure("white.TCheckbutton", background="white")
        style.configure("white.Header.TLabel", background="white")

        # --- Scrollable Frame ---
        canvas = tk.Canvas(self.window, bg="#f0f2f5", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas, style="Bg.TFrame")
        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scrollbar.pack(side="right", fill="y")
        
        content_frame = ttk.Frame(self.scrollable_frame, style="Bg.TFrame")
        content_frame.pack(expand=True, padx=50)

        # --- Teacher Profile Section ---
        if self.role == "Teacher":
            profile_frame = ttk.Frame(content_frame, padding=20, style="Card.TFrame")
            profile_frame.pack(fill=tk.X, expand=True, pady=10)
            ttk.Label(profile_frame, text="My Profile", style="white.Header.TLabel").pack(pady=(0, 20))
            ttk.Label(profile_frame, text="Full Name:", style="white.TLabel").pack(anchor="w")
            self.name_entry = ttk.Entry(profile_frame, width=50)
            self.name_entry.pack(fill=tk.X, pady=(0, 10))
            ttk.Label(profile_frame, text="Contact No:", style="white.TLabel").pack(anchor="w")
            self.contact_entry = ttk.Entry(profile_frame, width=50)
            self.contact_entry.pack(fill=tk.X, pady=(0, 10))
            ttk.Label(profile_frame, text="Subject Specialization:", style="white.TLabel").pack(anchor="w")
            self.subject_entry = ttk.Entry(profile_frame, width=50)
            self.subject_entry.pack(fill=tk.X, pady=(0, 15))
            self.load_user_profile()

        # --- Password Change Section ---
        pass_frame = ttk.Frame(content_frame, padding=20, style="Card.TFrame")
        pass_frame.pack(fill=tk.X, expand=True, pady=10)
        ttk.Label(pass_frame, text=f"Change Password for {self.username}", style="white.Header.TLabel").pack(pady=(0, 20))
        ttk.Label(pass_frame, text="Old Password:", style="white.TLabel").pack(anchor="w")
        self.old_pass_entry = ttk.Entry(pass_frame, show="*", width=50)
        self.old_pass_entry.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(pass_frame, text="New Password:", style="white.TLabel").pack(anchor="w")
        self.new_pass_entry = ttk.Entry(pass_frame, show="*", width=50)
        self.new_pass_entry.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(pass_frame, text="Confirm New Password:", style="white.TLabel").pack(anchor="w")
        self.confirm_pass_entry = ttk.Entry(pass_frame, show="*", width=50)
        self.confirm_pass_entry.pack(fill=tk.X, pady=(0, 15))

        # --- Security Settings Section (Admin Only) ---
        if self.role == "Admin":
            sec_frame = ttk.Frame(content_frame, padding=20, style="Card.TFrame")
            sec_frame.pack(fill=tk.X, expand=True, pady=10)
            ttk.Label(sec_frame, text="Security Settings (Admin)", style="white.Header.TLabel").pack(pady=10)
            self.liveness_var = tk.BooleanVar() 
            self.liveness_var.set(user_manager.get_setting("liveness_check")) 
            self.liveness_check = ttk.Checkbutton(
                sec_frame, text="Enable Liveness Detection (Anti-Spoofing)",
                variable=self.liveness_var, style="white.TCheckbutton"
            )
            self.liveness_check.pack(anchor="w", pady=5)
            self.unknown_log_var = tk.BooleanVar()
            self.unknown_log_var.set(user_manager.get_setting("unknown_logging"))
            self.unknown_log_check = ttk.Checkbutton(
                sec_frame, text="Log Unknown Faces (Security Feature)",
                variable=self.unknown_log_var, style="white.TCheckbutton"
            )
            self.unknown_log_check.pack(anchor="w", pady=5)
        
        # --- Backup & Restore Section (Admin Only) ---
        if self.role == "Admin":
            backup_frame = ttk.Frame(content_frame, padding=20, style="Card.TFrame")
            backup_frame.pack(fill=tk.X, expand=True, pady=10)
            ttk.Label(backup_frame, text="Backup & Restore (Admin Only)", style="white.Header.TLabel").pack(pady=10)
            btn_frame1 = ttk.Frame(backup_frame, style="Card.TFrame")
            btn_frame1.pack(fill=tk.X, pady=5)
            self.backup_button = ttk.Button(btn_frame1, text="Backup System Data", command=self.run_backup)
            self.backup_button.pack(side=tk.LEFT, expand=True, padx=5, ipady=5)
            self.restore_button = ttk.Button(btn_frame1, text="Restore System Data", command=self.run_restore)
            self.restore_button.pack(side=tk.RIGHT, expand=True, padx=5, ipady=5)
        
        # --- Maintenance (Admin Only) ---
        if self.role == "Admin":
            maint_frame = ttk.Frame(content_frame, padding=20, style="Card.TFrame")
            maint_frame.pack(fill=tk.X, expand=True, pady=10)
            ttk.Label(maint_frame, text="System Maintenance (Admin Only)", style="white.Header.TLabel").pack(pady=10)
            btn_frame2 = ttk.Frame(maint_frame, style="Card.TFrame")
            btn_frame2.pack(fill=tk.X, pady=5)
            
            # --- NAYA BUTTON ---
            self.rebuild_button = ttk.Button(btn_frame2, text="Re-build All Encodings", command=self.run_rebuild_encodings, style="Warning.TButton")
            self.rebuild_button.pack(side=tk.LEFT, expand=True, padx=5, ipady=5)
            
            self.clear_att_button = ttk.Button(btn_frame2, text="Clear ALL Attendance Data", command=self.run_clear_attendance, style="Danger.TButton")
            self.clear_att_button.pack(side=tk.LEFT, expand=True, padx=5, ipady=5)
            
            self.clear_log_button = ttk.Button(btn_frame2, text="Clear Unknown Face Logs", command=self.run_clear_unknown_logs, style="Danger.TButton")
            self.clear_log_button.pack(side=tk.RIGHT, expand=True, padx=5, ipady=5)
        
        # --- Save/Cancel Buttons ---
        button_frame = ttk.Frame(content_frame, style="Bg.TFrame")
        button_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=10)
        ttk.Button(button_frame, text="Save Changes", command=self.save_all_settings).pack(side=tk.LEFT, expand=True, padx=5, ipady=5)
        ttk.Button(button_frame, text="Cancel", command=self.window.destroy).pack(side=tk.RIGHT, expand=True, padx=5, ipady=5)

    def load_user_profile(self):
        """Teacher ki existing profile details load karta hai."""
        try:
            profile = user_manager.get_user_profile(self.username)
            if profile:
                self.name_entry.insert(0, profile.get("full_name", ""))
                self.contact_entry.insert(0, profile.get("contact_no", ""))
                self.subject_entry.insert(0, profile.get("subject", ""))
        except Exception as e:
            messagebox.showerror("Error", f"Profile load nahi ho saki: {e}", parent=self.window)

    def run_clear_attendance(self):
        if not messagebox.askokcancel("Confirm Action (WARNING!)", 
                                        "WARNING: Yeh action saara attendance data (sab subjects, sab dates) hamesha ke liye delete kar dega.\n\nStudents ki list delete nahi hogi.\n\nKya aap sach mein sabhi attendance records clear karna chahte hain?", 
                                        icon='warning', parent=self.window):
            return
        try:
            attendance_manager.clear_all_attendance_data()
            attendance_manager.log_activity(self.username, "CLEARED ALL ATTENDANCE DATA.")
            messagebox.showinfo("Success", "Saara attendance data safaltapoorvak clear ho gaya hai.", parent=self.window)
        except Exception as e:
            messagebox.showerror("Error", f"Data clear nahi ho saka: {e}", parent=self.window)

    def run_clear_unknown_logs(self):
        if not messagebox.askokcancel("Confirm Action", 
                                        "Kya aap 'unknown_logs' folder se saari unknown faces ki photos delete karna chahte hain?", 
                                        parent=self.window):
            return
        try:
            count = attendance_manager.clear_unknown_logs()
            attendance_manager.log_activity(self.username, f"Cleared {count} unknown face logs.")
            messagebox.showinfo("Success", f"{count} unknown log files delete ho gayi hain.", parent=self.window)
        except Exception as e:
            messagebox.showerror("Error", f"Logs clear nahi ho sake: {e}", parent=self.window)
    
    # --- NAYA FUNCTION ---
    def run_rebuild_encodings(self):
        """
        encodings.pkl file ko poore database se re-build karta hai.
        """
        if not messagebox.askokcancel("Confirm Action (WARNING!)", 
                                        "WARNING: Yeh action aapki 'encodings.pkl' file ko delete kar dega aur sabhi students ki photos ko phirse scan karega.\n\nIsmein kuch minutes lag sakte hain.\n\nKya aap sach mein encodings ko re-build karna chahte hain?", 
                                        icon='warning', parent=self.window):
            return

        try:
            # Button ko disable karo aur text badlo
            self.rebuild_button.config(text="Re-building... Please wait...", state=tk.DISABLED)
            self.window.update_idletasks() # UI ko update karo
            
            # Backend function call karo
            students_count, images_count = attendance_manager.rebuild_all_encodings()
            
            attendance_manager.log_activity(self.username, f"REBUILT all encodings. Processed {students_count} students / {images_count} images.")
            messagebox.showinfo("Success", f"Encodings successfully re-built!\n\nProcessed {students_count} students.\nTotal {images_count} images encoded.", parent=self.window)
        
        except Exception as e:
            messagebox.showerror("Re-build Failed", f"An error occurred during re-build:\n{e}", parent=self.window)
        finally:
            # Button ko normal state mein wapas lao
            self.rebuild_button.config(text="Re-build All Encodings", state=tk.NORMAL)

    def run_backup(self):
        default_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        filepath = filedialog.asksaveasfilename(
            parent=self.window, title="Save Backup As",
            initialfile=default_name, defaultextension=".zip",
            filetypes=[("Zip Files", "*.zip")]
        )
        if not filepath: return
        try:
            backup_manager.create_backup(filepath)
            messagebox.showinfo("Backup Successful", f"System data successfully backed up to:\n{filepath}", parent=self.window)
            attendance_manager.log_activity(self.username, f"Created system backup: {os.path.basename(filepath)}")
        except Exception as e:
            messagebox.showerror("Backup Failed", f"An error occurred during backup:\n{e}", parent=self.window)

    def run_restore(self):
        if not messagebox.askokcancel("Confirm Restore", 
                                        "WARNING:\nYeh aapke current data (students, attendance, faces) ko backup file se badal dega.\n\nKya aap sach mein restore karna chahte hain?", 
                                        icon='warning', parent=self.window):
            return
        filepath = filedialog.askopenfilename(
            parent=self.window, title="Select Backup File to Restore",
            filetypes=[("Zip Files", "*.zip")]
        )
        if not filepath: return
        try:
            backup_manager.restore_backup(filepath)
            attendance_manager.log_activity(self.username, f"RESTORED system from backup: {os.path.basename(filepath)}")
            messagebox.showinfo("Restore Successful", "System data has been restored.\n\nKripya application ko restart karein.", parent=self.window)
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Restore Failed", f"An error occurred during restore:\n{e}", parent=self.window)

    def save_all_settings(self):
        old_pass = self.old_pass_entry.get()
        new_pass = self.new_pass_entry.get()
        confirm_pass = self.confirm_pass_entry.get()
        password_changed = False
        log_msg = ""
        
        if old_pass or new_pass or confirm_pass:
            if not all([old_pass, new_pass, confirm_pass]):
                messagebox.showerror("Password Error", "Password badalne ke liye sabhi 3 password fields zaroori hain.", parent=self.window)
                return
            if new_pass != confirm_pass:
                messagebox.showerror("Password Error", "Naya password aur confirm password match nahi ho rahe.", parent=self.window)
                return
            if len(new_pass) < 4:
                messagebox.showwarning("Password Warning", "Password chhota hai. Kam se kam 4 characters ka rakhein.", parent=self.window)
                return
            try:
                user_manager.change_password(self.username, old_pass, new_pass)
                password_changed = True
                log_msg += "(Password Changed) "
            except ValueError as ve: 
                messagebox.showerror("Password Error", str(ve), parent=self.window)
                return
            except Exception as e:
                messagebox.showerror("Password Error", f"Password save nahi ho saka: {e}", parent=self.window)
                return
        
        try:
            if self.role == "Admin":
                liveness_set = self.liveness_var.get()
                unknown_log_set = self.unknown_log_var.get()
                user_manager.save_setting("liveness_check", liveness_set)
                user_manager.save_setting("unknown_logging", unknown_log_set)
                log_msg += f"Saved Admin settings. Liveness: {liveness_set}, Unknown Logging: {unknown_log_set}."
            
            if self.role == "Teacher":
                profile_data = {
                    "full_name": self.name_entry.get().strip(),
                    "contact_no": self.contact_entry.get().strip(),
                    "subject": self.subject_entry.get().strip(),
                    "department": user_manager.get_user_profile(self.username).get("department"), # Department change nahi kar sakte
                    "role": "Teacher" # Role change nahi kar sakte
                }
                user_manager.update_user_profile(self.username, profile_data)
                log_msg += "Updated profile details."

            if log_msg: # Agar kuch save hua hai tabhi log karo
                attendance_manager.log_activity(self.username, log_msg)
            
            messagebox.showinfo("Success", "Aapki details successfully save ho gayi hain.", parent=self.window)
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("Settings Error", f"Settings save nahi ho sakin: {e}", parent=self.window)

def show_settings_window(parent, role, username):
    SettingsWindow(parent, role, username)