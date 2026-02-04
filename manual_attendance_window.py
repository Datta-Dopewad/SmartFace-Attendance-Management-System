# /DigitalFaceAttendanceSystem/manual_attendance_window.py

import tkinter as tk
from tkinter import ttk, messagebox
import attendance_manager

# --- UPDATED: 'role' parameter add karo ---
class ManualAttendanceWindow:
    def __init__(self, parent, session_id, absent_students_list, refresh_callback, role):
        self.parent = parent
        self.session_id = session_id
        self.absent_students_list = absent_students_list
        self.refresh_callback = refresh_callback
        self.role = role.lower() # 'admin' ya 'teacher'
        
        self.window = tk.Toplevel(parent)
        self.window.title("Mark Manual Attendance")
        self.window.geometry("400x500")
        self.window.transient(parent)
        self.window.grab_set()

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TLabel", font=("Helvetica", 11))
        style.configure("TButton", font=("Helvetica", 11, "bold"))
        style.configure("Header.TLabel", font=("Helvetica", 12, "bold"))

        main_frame = ttk.Frame(self.window, padding=10)
        main_frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(main_frame, text="Select students to mark PRESENT:", style="Header.TLabel").pack(pady=5)
        ttk.Label(main_frame, text=f"Session: {session_id}").pack(pady=(0, 10))

        list_frame = ttk.Frame(main_frame, relief="solid", borderwidth=1)
        list_frame.pack(expand=True, fill=tk.BOTH, pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        self.listbox = tk.Listbox(
            list_frame, 
            selectmode=tk.MULTIPLE,
            yscrollcommand=scrollbar.set,
            font=("Helvetica", 11)
        )
        scrollbar.config(command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        for roll_no, name in self.absent_students_list:
            self.listbox.insert(tk.END, f"{roll_no} - {name}")

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Mark Selected Present", command=self.mark_selected).pack(side=tk.LEFT, expand=True, padx=5, ipady=5)
        ttk.Button(button_frame, text="Cancel", command=self.window.destroy).pack(side=tk.RIGHT, expand=True, padx=5, ipady=5)

    def mark_selected(self):
        selected_indices = self.listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("No Selection", "Please list se kam se kam ek student select karein.", parent=self.window)
            return

        marked_list_for_callback = []
        
        for i in selected_indices:
            item_text = self.listbox.get(i)
            try:
                roll_no, name = item_text.split(" - ", 1)
                roll_no = roll_no.strip()
                name = name.strip()
                
                success = attendance_manager.mark_attendance(roll_no, name, self.session_id)
                
                if success:
                    marked_list_for_callback.append((roll_no, name))
                    
                    # --- NAYA LOG ---
                    log_message = f"Manually marked student present. Roll: {roll_no} for Session: {self.session_id}"
                    attendance_manager.log_activity(self.role, log_message)
                else:
                    print(f"Already marked (skipped): {name}")

            except Exception as e:
                print(f"Error marking {item_text}: {e}")

        if marked_list_for_callback:
            messagebox.showinfo("Success", f"{len(marked_list_for_callback)} students ko manually present mark kar diya gaya hai.", parent=self.window)
            self.refresh_callback(marked_list_for_callback)
        
        self.window.destroy()

# --- UPDATED: 'role' parameter add karo ---
def show_manual_window(parent, session_id, absent_students_list, refresh_callback, role):
    ManualAttendanceWindow(parent, session_id, absent_students_list, refresh_callback, role)