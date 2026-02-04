# /DigitalFaceAttendanceSystem/student_management_dashboard.py

import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
import attendance_manager
import edit_student_window
import add_photos_window 
import student_profile_window

class StudentDashboard:
    # --- UPDATED: 'department' parameter add karo ---
    def __init__(self, parent, role, department):
        self.parent = parent
        self.role = role.lower()
        self.department = department # <-- NAYA: Department store karo
        
        self.window = tk.Toplevel(parent)
        self.window.title("Student Management Dashboard")
        self.window.state('zoomed')
        self.window.configure(bg='#f0f2f5')

        # ... (Styles same hain) ...
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))
        style.configure("TButton", font=("Helvetica", 11))
        style.configure("Header.TLabel", font=("Helvetica", 16, "bold"), background="#f0f2f5")
        style.configure("Import.TButton", font=("Helvetica", 11, "bold"), background="#28a745", foreground="white")
        style.map("Import.TButton", background=[('active', '#218838')])
        
        self.main_frame = ttk.Frame(self.window, padding=20)
        self.main_frame.pack(expand=True, fill=tk.BOTH)

        title_text = "Student Management"
        if self.department:
            title_text += f" (Department: {self.department})"
        ttk.Label(self.main_frame, text=title_text, style="Header.TLabel").pack(pady=10)

        # ... (Button layout same hai) ...
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, pady=10)
        self.delete_button = ttk.Button(self.button_frame, text="Delete Selected", command=self.delete_student)
        self.delete_button.pack(side=tk.LEFT, padx=5)
        self.edit_button = ttk.Button(self.button_frame, text="Edit Selected", state=tk.NORMAL, command=self.open_edit_window)
        self.edit_button.pack(side=tk.LEFT, padx=5)
        self.add_photos_button = ttk.Button(self.button_frame, text="Add More Photos", command=self.open_add_photos_window)
        self.add_photos_button.pack(side=tk.LEFT, padx=5)
        self.import_button = ttk.Button(self.button_frame, text="Import from Excel", command=self.open_bulk_import, style="Import.TButton")
        self.import_button.pack(side=tk.LEFT, padx=15)
        self.refresh_button = ttk.Button(self.button_frame, text="Refresh List", command=self.populate_tree)
        self.refresh_button.pack(side=tk.RIGHT, padx=5)

        # --- Treeview (Student Table) ---
        self.tree_frame = ttk.Frame(self.main_frame)
        self.tree_frame.pack(expand=True, fill=tk.BOTH, pady=10)
        self.tree_scroll_y = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL)
        self.tree_scroll_x = ttk.Scrollbar(self.tree_frame, orient=tk.HORIZONTAL)
        self.tree_columns = ("Roll No", "Name", "Department", "Class", "PRN No", "Contact No", "DOB")
        self.tree = ttk.Treeview(
            self.tree_frame, columns=self.tree_columns, show="headings",
            yscrollcommand=self.tree_scroll_y.set, xscrollcommand=self.tree_scroll_x.set
        )
        self.tree_scroll_y.config(command=self.tree.yview)
        self.tree_scroll_x.config(command=self.tree.xview)
        self.tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(expand=True, fill=tk.BOTH)
        for col in self.tree_columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor=tk.CENTER)
        self.tree.column("Name", width=150)
        self.tree.column("Contact No", width=150)
        self.tree.tag_configure("oddrow", background="#E8E8E8")
        self.tree.tag_configure("evenrow", background="white")
        self.tree.bind("<Double-1>", self.open_profile_viewer)
        
        # --- Teacher Role Restrictions ---
        if self.role == "Teacher":
            self.delete_button.config(state=tk.DISABLED)
            self.import_button.config(state=tk.DISABLED)

        self.populate_tree()

    # --- UPDATED: populate_tree ---
    def populate_tree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        try:
            # department ko pass karo
            records = attendance_manager.get_all_students_list(self.department)
            for i, row in enumerate(records):
                tag = "evenrow" if i % 2 == 0 else "oddrow"
                self.tree.insert("", "end", values=row, tags=(tag,))
        except Exception as e:
            messagebox.showerror("Error", f"Student records load nahi ho sake: {e}", parent=self.window)
            
    # ... (Baaki sabhi functions 'delete_student' se 'open_profile_viewer' tak same hain) ...
    def delete_student(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please list se ek student select karein.", parent=self.window)
            return
        student_data = self.tree.item(selected_item, "values")
        roll_no, name = student_data[0], student_data[1]
        if not messagebox.askyesno("Confirm Delete", f"Kya aap is student ko hamesha ke liye delete karna chahte hain?\n\nRoll No: {roll_no}\nName: {name}", parent=self.window):
            return
        try:
            attendance_manager.delete_student_by_roll(roll_no)
            attendance_manager.log_activity(self.role, f"Deleted student. Roll: {roll_no}, Name: {name}")
            messagebox.showinfo("Success", f"Student {name} (Roll: {roll_no}) delete ho gaya hai.", parent=self.window)
            self.populate_tree()
        except Exception as e:
            messagebox.showerror("Delete Error", f"Student delete nahi ho saka: {e}", parent=self.window)
    def open_edit_window(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please list se ek student select karein jise edit karna hai.", parent=self.window)
            return
        roll_no = self.tree.item(selected_item, "values")[0]
        try:
            current_data = attendance_manager.get_student_by_roll(roll_no)
            if current_data:
                edit_student_window.show_edit_window(self.window, roll_no, current_data, self.populate_tree, self.role)
            else:
                messagebox.showerror("Error", f"Student with Roll No {roll_no} ka data nahi mila.", parent=self.window)
        except Exception as e:
             messagebox.showerror("Error", f"Student data fetch nahi ho saka: {e}", parent=self.window)
    def open_add_photos_window(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please list se ek student select karein jismein photos add karni hain.", parent=self.window)
            return
        student_data_values = self.tree.item(selected_item, "values")
        roll_no, name = student_data_values[0], student_data_values[1]
        add_photos_window.show_add_photos_window(self.window, roll_no, name, self.role)
    def open_bulk_import(self):
        msg = (
            "Kripya import karne ke liye ek Excel (.xlsx) file select karein.\n\n"
            "ZAROORI FORMAT:\n"
            "Column A: Roll No\nColumn B: Name\nColumn C: Department\n"
            "Column D: Class Name\nColumn E: PRN No\nColumn F: Contact No\n"
            "Column G: Date of Birth (YYYY-MM-DD)\n\n"
            "Pehli row (header) ko skip kar diya jaayega."
        )
        messagebox.showinfo("Bulk Import Instructions", msg, parent=self.window)
        filepath = filedialog.askopenfilename(
            parent=self.window, title="Select Student Excel File",
            filetypes=[("Excel files", "*.xlsx")]
        )
        if not filepath: return
        try:
            self.import_button.config(text="Importing...", state=tk.DISABLED)
            self.window.update_idletasks()
            logs = attendance_manager.bulk_import_students(filepath)
            summary_msg = (
                "Bulk Import Complete!\n\n"
                f"Successfully Imported: {logs['success']}\n"
                f"Duplicates Skipped: {logs['duplicates']}\n"
                f"Errors (invalid rows): {logs['errors']}"
            )
            messagebox.showinfo("Import Summary", summary_msg, parent=self.window)
            attendance_manager.log_activity(self.role, f"Bulk imported students. Success: {logs['success']}, Duplicates: {logs['duplicates']}")
            self.populate_tree()
        except Exception as e:
            messagebox.showerror("Import Failed", f"An error occurred during import:\n{e}", parent=self.window)
        finally:
            self.import_button.config(text="Import from Excel", state=tk.NORMAL)
    def open_profile_viewer(self, event):
        selected_item = self.tree.focus()
        if not selected_item: return 
        student_data_values = self.tree.item(selected_item, "values")
        roll_no, name = student_data_values[0], student_data_values[1]
        student_profile_window.show_student_profile(self.window, roll_no, name)

# --- UPDATED: 'department' parameter add karo ---
def show_student_dashboard(parent, role, department):
    StudentDashboard(parent, role, department)