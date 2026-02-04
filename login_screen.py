# /DigitalFaceAttendanceSystem/login_screen.py

import tkinter as tk
from tkinter import ttk, messagebox
import dashboard
import user_manager 
import attendance_manager 
from datetime import datetime, timedelta

class LoginScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Rural School Attendance System")
        self.root.state('zoomed') 
        self.root.configure(bg='#f0f2f5')

        self.lock_timer_running = False

        # --- Styles ---
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Login.TButton", font=("Helvetica", 12, "bold"), background="#007bff", foreground="white", padding=10, borderwidth=0)
        style.map("Login.TButton", background=[('active', '#0056b3')])
        style.configure("TFrame", background="white")
        style.configure("TLabel", background="white", font=("Helvetica", 10))
        style.configure("Header.TLabel", font=("Helvetica", 18, "bold"))
        style.configure("Sub.TLabel", font=("Helvetica", 10), foreground="#555")
        style.configure("TEntry", font=("Helvetica", 11), padding=8, fieldbackground="white", borderwidth=1)
        style.configure("Error.TLabel", background="white", foreground="red", font=("Helvetica", 10, "bold"))

        # --- Layout ---
        self.login_frame = ttk.Frame(root, style="TFrame", padding=40, relief="solid", borderwidth=1)
        self.login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        title_label = ttk.Label(self.login_frame, text="Welcome Back", style="Header.TLabel", anchor="center")
        title_label.pack(pady=(0, 5))
        
        sub_title = ttk.Label(self.login_frame, text="Secure access to attendance management", style="Sub.TLabel", anchor="center")
        sub_title.pack(pady=(0, 25))

        user_label = ttk.Label(self.login_frame, text="Username:")
        user_label.pack(anchor="w", padx=5)
        self.username_entry = ttk.Entry(self.login_frame, width=35)
        self.username_entry.pack(pady=(0, 15), ipady=4)

        pass_label = ttk.Label(self.login_frame, text="Password:")
        pass_label.pack(anchor="w", padx=5)
        self.password_entry = ttk.Entry(self.login_frame, show="*", width=35)
        self.password_entry.pack(pady=(0, 15), ipady=4)

        self.lockout_label = ttk.Label(self.login_frame, text="", style="Error.TLabel", anchor="center")
        self.lockout_label.pack(pady=(0, 10))

        self.login_button = ttk.Button(self.login_frame, 
                                  text="Sign In", 
                                  command=self.attempt_login, 
                                  style="Login.TButton", 
                                  width=33)
        self.login_button.pack(pady=10, fill='x')
        
        self.root.bind('<Return>', lambda event: self.attempt_login())
        
        # Username entry par focus set karo
        self.username_entry.focus()
        # Bind focus out event
        self.username_entry.bind("<FocusOut>", self.check_initial_lockout)

    def check_initial_lockout(self, event=None):
        """Focus hatne par user ka lockout status check karta hai."""
        username = self.username_entry.get().strip()
        if not username:
            return
        
        remaining_seconds = user_manager.get_lockout_status(username)
        if remaining_seconds > 0:
            self.start_lockout_timer(remaining_seconds)

    def start_lockout_timer(self, seconds_left):
        self.lock_timer_running = True
        self.login_button.config(state=tk.DISABLED)
        self.username_entry.config(state=tk.DISABLED)
        self.password_entry.config(state=tk.DISABLED)
        self.update_timer_label(seconds_left)

    def update_timer_label(self, seconds_left):
        if seconds_left > 0:
            minutes, seconds = divmod(seconds_left, 60)
            self.lockout_label.config(text=f"Account locked. Try again in {minutes:02d}:{seconds:02d}")
            self.root.after(1000, lambda: self.update_timer_label(seconds_left - 1))
        else:
            self.lockout_label.config(text="")
            self.login_button.config(state=tk.NORMAL)
            self.username_entry.config(state=tk.NORMAL)
            self.password_entry.config(state=tk.NORMAL)
            self.lock_timer_running = False

    def attempt_login(self):
        if self.lock_timer_running:
            return 

        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Login Failed", "Username aur Password dono zaroori hain.")
            return

        # --- UPDATED: 5 values receive karo ---
        is_valid, role, username, department, message_or_time = user_manager.verify_user(username, password)
        
        if is_valid:
            messagebox.showinfo("Login Success", f"Welcome, {role} ({username})!")
            self.root.destroy()
            attendance_manager.log_activity(username, "Logged in.")
            # --- UPDATED: department ko pass karo ---
            dashboard.show_dashboard(role, username, department)
        else:
            if isinstance(message_or_time, int):
                attendance_manager.log_activity(username, f"FAILED LOGIN attempt (Account LOCKED).")
                self.start_lockout_timer(message_or_time)
            elif message_or_time == "Invalid password":
                attendance_manager.log_activity(username, f"FAILED LOGIN attempt with password: '{password}'")
                messagebox.showerror("Login Failed", "Galat username ya password.")
            else:
                messagebox.showerror("Login Failed", message_or_time)

def show_login_screen():
    attendance_manager.setup_environment()
    user_manager.setup_users()
    root = tk.Tk()
    app = LoginScreen(root)
    root.mainloop()