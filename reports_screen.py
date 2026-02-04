# /DigitalFaceAttendanceSystem/reports_screen.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import attendance_manager
# pdf_manager import hata diya gaya hai

class ReportsScreen:
    # --- UPDATED: 'department' parameter add karo ---
    def __init__(self, parent, department):
        self.parent = parent
        self.department = department # <-- NAYA: Department store karo
        self.window = tk.Toplevel(parent)
        self.window.title("Attendance Reports")
        self.window.state('zoomed')

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))
        style.configure("Stats.TLabel", font=("Helvetica", 12, "bold"), background="#f0f2f5")
        style.configure("StudentInfo.TLabel", font=("Helvetica", 11), background="#f0f2f5")

        self.current_report_type = None 
        self.current_report_data = []
        self.current_report_headers = []
        self.current_report_stats = {}
        self.current_student_details = {} 

        self.main_frame = ttk.Frame(self.window, padding=20)
        self.main_frame.pack(expand=True, fill=tk.BOTH)

        # Title ko dynamic banao
        title_text = "Attendance Log"
        if self.department:
            title_text += f" (Department: {self.department})"
        ttk.Label(self.main_frame, text=title_text, font=("Helvetica", 16, "bold")).pack(pady=10)

        # ... (Baaki ka filter frame layout same hai) ...
        self.filter_frame = ttk.Frame(self.main_frame)
        self.filter_frame.pack(fill=tk.X, pady=10)
        ttk.Label(self.filter_frame, text="Filter by Subject:").pack(side=tk.LEFT, padx=5)
        self.subject_entry = ttk.Entry(self.filter_frame, width=20)
        self.subject_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(self.filter_frame, text="OR Date (YYYY-MM-DD):").pack(side=tk.LEFT, padx=(15, 5))
        self.date_entry = ttk.Entry(self.filter_frame, width=15)
        self.date_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(self.filter_frame, text="OR Roll No:").pack(side=tk.LEFT, padx=(15, 5))
        self.roll_no_entry = ttk.Entry(self.filter_frame, width=15)
        self.roll_no_entry.pack(side=tk.LEFT, padx=5)
        self.filter_button = ttk.Button(self.filter_frame, text="Filter / Refresh", command=self.populate_tree)
        self.filter_button.pack(side=tk.LEFT, padx=20)
        self.clear_button = ttk.Button(self.filter_frame, text="Clear Filters", command=self.clear_filters)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # ... (Baaki ka layout same hai) ...
        self.stats_frame = ttk.Frame(self.main_frame, style="Bg.TFrame")
        self.stats_frame.pack(fill=tk.X, pady=10)
        self.lbl_student_info = ttk.Label(self.stats_frame, text="", style="StudentInfo.TLabel")
        self.lbl_student_info.pack(fill=tk.X)
        self.lbl_stats = ttk.Label(self.stats_frame, text="Please filter to see stats.", style="Stats.TLabel")
        self.lbl_stats.pack(fill=tk.X, pady=5)
        self.tree_frame = ttk.Frame(self.main_frame)
        self.tree_frame.pack(expand=True, fill=tk.BOTH, pady=10)
        self.tree_scroll_y = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL)
        self.tree_scroll_x = ttk.Scrollbar(self.tree_frame, orient=tk.HORIZONTAL)
        self.tree = ttk.Treeview(
            self.tree_frame, show="headings",
            yscrollcommand=self.tree_scroll_y.set,
            xscrollcommand=self.tree_scroll_x.set
        )
        self.tree_scroll_y.config(command=self.tree.yview)
        self.tree_scroll_x.config(command=self.tree.xview)
        self.tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(expand=True, fill=tk.BOTH)
        self.tree.tag_configure("Present", foreground="green", font=("Helvetica", 9, "bold"))
        self.tree.tag_configure("Absent", foreground="red", font=("Helvetica", 9, "bold"))
        self.tree.tag_configure("oddrow", background="#E8E8E8")
        self.tree.tag_configure("evenrow", background="white")
        self.export_excel_button = ttk.Button(self.main_frame, text="Export to Excel", command=self.export_report_excel)
        self.export_excel_button.pack(pady=10, ipady=5)

        self.populate_tree()

    def setup_tree_columns(self, columns):
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = columns
        for col in columns:
            self.tree.heading(col, text=col)
            if col == "Roll No": self.tree.column(col, width=80, anchor=tk.CENTER)
            elif col == "Name": self.tree.column(col, width=150)
            elif col == "Status": self.tree.column(col, width=60, anchor=tk.CENTER)
            elif col == "Subject" or "Session" in col: self.tree.column(col, width=150, anchor=tk.CENTER)
            else: self.tree.column(col, width=100, anchor=tk.CENTER)

    def clear_filters(self):
        self.subject_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.roll_no_entry.delete(0, tk.END)
        self.populate_tree()

    # --- UPDATED: populate_tree ---
    def populate_tree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        subject_name = self.subject_entry.get().strip() or None
        date_str = self.date_entry.get().strip() or None
        roll_no = self.roll_no_entry.get().strip() or None
        
        self.current_report_type = None
        self.current_report_data = []
        self.current_report_headers = []
        self.current_report_stats = {}
        self.current_student_details = {}
        
        try:
            if roll_no:
                self.current_report_type = 'individual'
                self.current_filter_value = roll_no
                headers = ("Subject", "Date", "Status")
                self.setup_tree_columns(headers)
                
                # department ko pass karo
                details, report_data, stats = attendance_manager.generate_individual_report(roll_no, self.department)
                
                self.lbl_student_info.config(text=f"Report for: {details['name']} (Roll: {roll_no}) | Dept: {details['department']}, Class: {details['class_name']}")
                self.lbl_stats.config(text=f"Total Lectures: {stats['total']} | Present: {stats['present']} | Absent: {stats['absent']} | Percentage: {stats['percentage']}")
                for i, row in enumerate(report_data):
                    status = row[2]; tag = "Present" if status == "P" else "Absent"
                    bg_tag = "evenrow" if i % 2 == 0 else "oddrow"
                    self.tree.insert("", "end", values=row, tags=(tag, bg_tag))
                self.current_report_headers = headers
                self.current_report_data = report_data
                self.current_report_stats = stats
                self.current_student_details = details
                
            elif subject_name:
                self.current_report_type = 'subject'
                self.current_filter_value = subject_name
                headers = ("Roll No", "Name", "Status", "Date", "Timestamp", "Department", "Class", "PRN No", "Contact No")
                self.setup_tree_columns(headers)
                
                # department ko pass karo
                report_data, stats = attendance_manager.generate_subject_summary_report(subject_name, self.department)
                
                self.lbl_student_info.config(text=f"Showing report for Subject: {subject_name}")
                self.lbl_stats.config(text=f"Total: {stats['total']} | Present: {stats['present']} | Absent: {stats['absent']} | Percentage: {stats['percentage']}")
                for i, row in enumerate(report_data):
                    status = row[2]; tag = "Present" if status == "P" else "Absent"
                    bg_tag = "evenrow" if i % 2 == 0 else "oddrow"
                    self.tree.insert("", "end", values=row, tags=(tag, bg_tag))
                self.current_report_headers = headers
                self.current_report_data = report_data
                self.current_report_stats = stats

            elif date_str:
                self.current_report_type = 'date'
                self.current_filter_value = date_str
                
                # department ko pass karo
                headers, report_data, stats = attendance_manager.generate_date_summary_report(date_str, self.department)
                
                if not report_data:
                    self.setup_tree_columns(["Message"])
                    self.tree.insert("", "end", values=[f"No data found for date {date_str}."])
                    self.lbl_stats.config(text="No data found.")
                    self.lbl_student_info.config(text="")
                    return
                self.setup_tree_columns(headers)
                stats_text = ""
                for session, stat in stats.items():
                    stats_text += f"[{session} -> P: {stat['present']}, A: {stat['absent']}]  "
                self.lbl_student_info.config(text=f"Showing report for Date: {date_str}")
                self.lbl_stats.config(text=stats_text)
                for i, row in enumerate(report_data):
                    bg_tag = "evenrow" if i % 2 == 0 else "oddrow"
                    tags_to_apply = (bg_tag,)
                    if "P" in row: tags_to_apply += ("Present",)
                    if "A" in row: tags_to_apply += ("Absent",)
                    self.tree.insert("", "end", values=row, tags=tags_to_apply)
                self.current_report_headers = headers
                self.current_report_data = report_data
                self.current_report_stats = stats
                
            else:
                self.lbl_stats.config(text="Please enter a Subject, Date, or Roll No to filter.")
                self.lbl_student_info.config(text="")
                self.setup_tree_columns(["Message"])
                self.tree.insert("", "end", values=["Please enter a Subject Name, Date (YYYY-MM-DD), OR Roll No to generate a report."])

        except ValueError as ve: # Catch karo agar teacher galat roll no daale
            messagebox.showerror("Authorization Error", str(ve), parent=self.window)
            self.lbl_stats.config(text="Error.")
            self.lbl_student_info.config(text="")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load records: {e}", parent=self.window)
            self.lbl_stats.config(text="Error loading report.")
            self.lbl_student_info.config(text="")

    def export_report_excel(self):
        if not self.current_report_type:
            messagebox.showwarning("No Data", "Please filter a report before exporting.", parent=self.window)
            return
        try:
            success = False
            if self.current_report_type == 'subject':
                filepath = filedialog.asksaveasfilename(
                    defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")],
                    title="Save Subject Report As",
                    initialfile=f"Subject_Report_{self.current_filter_value.replace(' ', '_')}.xlsx"
                )
                if not filepath: return
                success = attendance_manager.export_subject_report_to_excel(
                    filepath, self.current_report_data, self.current_report_stats, self.current_filter_value
                )
            elif self.current_report_type == 'date':
                filepath = filedialog.asksaveasfilename(
                    defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")],
                    title="Save Date Report As",
                    initialfile=f"Date_Report_{self.current_filter_value}.xlsx"
                )
                if not filepath: return
                success = attendance_manager.export_date_summary_to_excel(
                    filepath, self.current_report_headers, self.current_report_data, self.current_report_stats, self.current_filter_value
                )
            elif self.current_report_type == 'individual':
                filepath = filedialog.asksaveasfilename(
                    defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")],
                    title="Save Individual Report As",
                    initialfile=f"Report_Card_{self.current_filter_value}.xlsx"
                )
                if not filepath: return
                success = attendance_manager.export_individual_report_to_excel(
                    filepath, self.current_student_details, self.current_report_data, self.current_report_stats
                )
            if success:
                messagebox.showinfo("Success", f"Report exported successfully to:\n{filepath}", parent=self.window)
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data to Excel: {e}", parent=self.window)

# --- UPDATED: 'department' parameter add karo ---
def show_reports(parent, department):
    ReportsScreen(parent, department)