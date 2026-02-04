# /DigitalFaceAttendanceSystem/dashboard.py

import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import simpledialog 
import student_management_screen
import attend_the_attendance
import reports_screen
import login_screen
import attendance_manager 
from datetime import datetime
import student_management_dashboard 
import settings_window 
import activity_log_viewer
import user_manager
import teacher_management_dashboard 

import matplotlib
matplotlib.use("TkAgg") 
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

# --- UPDATED: 'department' parameter add karo ---
def show_dashboard(role, username, department): 
    
    root = tk.Tk()
    root.title("Rural School Attendance System - Dashboard")
    root.state('zoomed')
    root.configure(bg='#f0f2f5')
    
    role_lower = role.lower() # 'admin' ya 'teacher'

    # --- Styles (No Change) ---
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("Content.TFrame", background="white")
    style.configure("Header.TLabel", background="#f0f2f5", font=("Helvetica", 22, "bold"), foreground="#333333")
    style.configure("Sub.TLabel", background="white", font=("Helvetica", 12), foreground="#555")
    style.configure("Stats.TFrame", background="#f0f2f5")
    style.configure("Stat.TLabel", background="#f0f2f5", font=("Helvetica", 14, "bold"))
    style.configure("StatValue.TLabel", background="#f0f2f5", font=("Helvetica", 18, "bold"))
    style.configure("Dashboard.TButton", font=("Helvetica", 14, "bold"), background="#007bff", foreground="white", padding=(18, 18), width=25, borderwidth=0) 
    style.map("Dashboard.TButton", background=[('active', '#0056b3')])
    style.configure("Exit.TButton", font=("Helvetica", 14, "bold"), background="#6c757d", foreground="white", padding=(18, 18), width=25, borderwidth=0)
    style.map("Exit.TButton", background=[('active', '#5a6268')])
    style.configure("Settings.TButton", font=("Helvetica", 14, "bold"), background="#17a2b8", foreground="white", padding=(18, 18), width=25, borderwidth=0)
    style.map("Settings.TButton", background=[('active', '#138496')])
    style.configure("Log.TButton", font=("Helvetica", 14, "bold"), background="#ffc107", foreground="black", padding=(18, 18), width=25, borderwidth=0)
    style.map("Log.TButton", background=[('active', '#e0a800')])
    style.configure("Mgmt.TButton", font=("Helvetica", 14, "bold"), background="#fd7e14", foreground="white", padding=(18, 18), width=25, borderwidth=0)
    style.map("Mgmt.TButton", background=[('active', '#e66a00')])
    style.configure("Bg.TFrame", background="#f0f2f5")
    
    
    # --- Scrollable Frame (No Change) ---
    canvas = tk.Canvas(root, bg="#f0f2f5", highlightthickness=0)
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas, style="Bg.TFrame")
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    def _on_mousewheel(event):
        if event.num == 4 or event.delta > 0: canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0: canvas.yview_scroll(1, "units")
    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    canvas.bind_all("<Button-4>", _on_mousewheel)
    canvas.bind_all("<Button-5>", _on_mousewheel)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    content_container = ttk.Frame(scrollable_frame, style="Bg.TFrame")
    content_container.pack(expand=True, padx=50)
    
    
    # --- Header (No Change) ---
    header_frame = ttk.Frame(content_container, style="Header.TLabel") 
    header_frame.pack(pady=(20, 10)) 
    title_label = ttk.Label(header_frame, text="Attendance Dashboard", style="Header.TLabel")
    title_label.pack()

    # --- Live Stats (UPDATED) ---
    try:
        # department ko pass karo (Admin ke liye None, Teacher ke liye "IT", etc.)
        stats = attendance_manager.get_dashboard_stats(department) 
    except Exception as e:
        print(f"Stats load nahi ho sake: {e}")
        stats = {"total": "Error", "present": "Error", "absent": "Error"}
    
    stats_frame = ttk.Frame(content_container, style="Stats.TFrame", padding=5)
    stats_frame.pack(pady=5)
    
    # Department filter dikhao
    dept_label = f"({department})" if department else "(All Departments)"
    ttk.Label(stats_frame, text=dept_label, style="Stat.TLabel", foreground="#555").pack(pady=(0, 5))
    
    total_frame = ttk.Frame(stats_frame, style="Stats.TFrame")
    total_frame.pack(side=tk.LEFT, padx=30)
    ttk.Label(total_frame, text="Total Students", style="Stat.TLabel").pack()
    ttk.Label(total_frame, text=stats['total'], style="StatValue.TLabel", foreground="#007bff").pack()
    present_frame = ttk.Frame(stats_frame, style="Stats.TFrame")
    present_frame.pack(side=tk.LEFT, padx=30)
    ttk.Label(present_frame, text="Today's Present", style="Stat.TLabel").pack()
    ttk.Label(present_frame, text=stats['present'], style="StatValue.TLabel", foreground="#28a745").pack()
    absent_frame = ttk.Frame(stats_frame, style="Stats.TFrame")
    absent_frame.pack(side=tk.LEFT, padx=30)
    ttk.Label(absent_frame, text="Today's Absent", style="Stat.TLabel").pack()
    ttk.Label(absent_frame, text=stats['absent'], style="StatValue.TLabel", foreground="#dc3545").pack()

    # --- Chart Frame (UPDATED) ---
    chart_frame = ttk.Frame(content_container, style="Bg.TFrame")
    chart_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=50)

    try:
        # department ko pass karo
        trend_data = attendance_manager.get_monthly_attendance_trend(department)
        fig = Figure(figsize=(10, 3.5), dpi=100)
        fig.patch.set_facecolor('#f0f2f5')
        ax = fig.add_subplot(111)
        
        if not trend_data.empty:
            date_labels = trend_data.index.strftime("%d-%b")
            ax.bar(date_labels, trend_data.values, color="#007bff", width=0.6)
            ax.set_title(f"Attendance Trend {dept_label} (Last 30 Days)", fontsize=12)
            ax.set_ylabel("Attendance %", fontsize=10)
            ax.tick_params(axis='x', rotation=45, labelsize=8)
            ax.set_ylim(0, 100)
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            fig.tight_layout()
        else:
            ax.set_title(f"No attendance data found {dept_label} for the last 30 days.")

        chart_canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        chart_canvas.draw()
        chart_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    except Exception as e:
        print(f"Chart banane mein error: {e}")
        ttk.Label(chart_frame, text="Chart load nahi ho saka. (Libraries install hain?)").pack()

    # --- Main Content Frame (Buttons) ---
    content_frame = ttk.Frame(content_container, style="Content.TFrame", padding=30, relief="solid", borderwidth=1)
    content_frame.pack(side=tk.BOTTOM, pady=(10, 20))
    
    welcome_text = f"Welcome, {role} ({username}). Select an option."
    sub_title = ttk.Label(content_frame, text=welcome_text, style="Sub.TLabel")
    sub_title.pack(pady=(0, 10))

    btn_frame_left = ttk.Frame(content_frame, style="Content.TFrame")
    btn_frame_left.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
    btn_frame_right = ttk.Frame(content_frame, style="Content.TFrame")
    btn_frame_right.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))

    # --- Button Functions (UPDATED) ---
    def open_student_management():
        # department ko pass karo
        student_management_screen.show_student_management(root, role, department) 
    def open_take_attendance():
        subject_name = simpledialog.askstring("Subject Name", "Please enter the Subject Name:", parent=root)
        if subject_name:
            subject_name = subject_name.strip()
            attendance_manager.log_activity(username, f"Started attendance for subject: {subject_name}")
            liveness_enabled = user_manager.get_setting("liveness_check")
            unknown_logging_enabled = user_manager.get_setting("unknown_logging")
            if liveness_enabled:
                messagebox.showinfo("Liveness Check ON", "Anti-Spoofing (Liveness Check) is ENABLED.\nStudents ko blink karna hoga.", parent=root)
            # department ko pass karo
            attend_the_attendance.start_attendance(root, subject_name, role, liveness_enabled, unknown_logging_enabled, department)
        else:
            messagebox.showinfo("Cancelled", "Attendance process cancelled.", parent=root)
    def open_reports():
        # department ko pass karo
        reports_screen.show_reports(root, department)
    def open_student_dashboard():
        # department ko pass karo
        student_management_dashboard.show_student_dashboard(root, role, department)
    def go_back_to_login():
        if messagebox.askokcancel("Log Out", "Are you sure you want to log out?"):
            attendance_manager.log_activity(username, "Logged out.")
            root.destroy()
            login_screen.show_login_screen()
    def open_settings():
        # username ko pass karo
        settings_window.show_settings_window(root, role, username) 
    def open_activity_log():
        activity_log_viewer.show_activity_log_viewer(root)
    def open_teacher_dashboard():
        # role ko pass karo
        teacher_management_dashboard.show_teacher_dashboard(root, role)

    # --- Buttons (Column 1) ---
    btn_register = ttk.Button(btn_frame_left, text="1. Register Student", command=open_student_management, style="Dashboard.TButton")
    btn_register.pack(pady=4, fill=tk.X, expand=True)
    btn_attend = ttk.Button(btn_frame_left, text="2. Take Attendance", command=open_take_attendance, style="Dashboard.TButton")
    btn_attend.pack(pady=4, fill=tk.X, expand=True)
    btn_reports = ttk.Button(btn_frame_left, text="3. View Reports", command=open_reports, style="Dashboard.TButton")
    btn_reports.pack(pady=4, fill=tk.X, expand=True)
    btn_manage = ttk.Button(btn_frame_left, text="4. Student Management", command=open_student_dashboard, style="Dashboard.TButton")
    btn_manage.pack(pady=4, fill=tk.X, expand=True)
    
    # --- Buttons (Column 2) ---
    btn_teacher_manage = ttk.Button(btn_frame_right, text="5. Teacher Management", command=open_teacher_dashboard, style="Mgmt.TButton")
    btn_teacher_manage.pack(pady=4, fill=tk.X, expand=True)
    btn_log = ttk.Button(btn_frame_right, text="6. View Activity Log", command=open_activity_log, style="Log.TButton")
    btn_log.pack(pady=4, fill=tk.X, expand=True)
    btn_settings = ttk.Button(btn_frame_right, text="7. Settings", command=open_settings, style="Settings.TButton")
    btn_settings.pack(pady=4, fill=tk.X, expand=True)
    btn_back_logout = ttk.Button(btn_frame_right, text="Log Out (Back)", command=go_back_to_login, style="Exit.TButton")
    btn_back_logout.pack(pady=4, fill=tk.X, expand=True)
    
    # --- Role Restrictions ---
    if role == "Teacher":
        btn_register.config(state=tk.DISABLED)
        #btn_manage.config(state=tk.DISABLED) # Teacher ab student management dekh sakta hai (sirf apne dept ke)
        btn_log.config(state=tk.DISABLED)
        btn_teacher_manage.config(state=tk.DISABLED)

    root.mainloop()