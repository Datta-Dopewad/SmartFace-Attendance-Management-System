# /DigitalFaceAttendanceSystem/teacher_management_dashboard.py

import tkinter as tk
from tkinter import ttk, messagebox
import user_manager 
import add_edit_teacher_window 
import attendance_manager 

class TeacherDashboard:
    def __init__(self, parent, role):
        self.parent = parent
        self.role = role.lower()
        
        self.window = tk.Toplevel(parent)
        self.window.title("User Management Dashboard (Admin)")
        self.window.state('zoomed')
        self.window.configure(bg='#f0f2f5')

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))
        style.configure("TButton", font=("Helvetica", 11))
        style.configure("Header.TLabel", font=("Helvetica", 16, "bold"), background="#f0f2f5")
        
        self.main_frame = ttk.Frame(self.window, padding=20)
        self.main_frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(self.main_frame, text="User Management (Admins & Teachers)", style="Header.TLabel").pack(pady=10)

        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, pady=10)
        ttk.Button(self.button_frame, text="Add New User", command=self.open_add_user_window).pack(side=tk.LEFT, padx=5, ipady=5)
        ttk.Button(self.button_frame, text="Edit Selected User", command=self.open_edit_user_window).pack(side=tk.LEFT, padx=5, ipady=5)
        ttk.Button(self.button_frame, text="Delete Selected User", command=self.delete_user).pack(side=tk.LEFT, padx=5, ipady=5)
        ttk.Button(self.button_frame, text="Refresh List", command=self.populate_tree).pack(side=tk.RIGHT, padx=5, ipady=5)

        self.tree_frame = ttk.Frame(self.main_frame)
        self.tree_frame.pack(expand=True, fill=tk.BOTH, pady=10)

        self.tree_scroll_y = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL)
        self.tree_scroll_x = ttk.Scrollbar(self.tree_frame, orient=tk.HORIZONTAL)

        # --- UPDATED: Naya column "Department" ---
        self.tree_columns = ("Username", "Full Name", "Role", "Department", "Contact No", "Subject")
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
            self.tree.column(col, width=150, anchor=tk.W)
        self.tree.column("Role", width=80, anchor=tk.CENTER)
        self.tree.column("Department", width=100, anchor=tk.CENTER) # Naya column

        self.tree.tag_configure("oddrow", background="#E8E8E8")
        self.tree.tag_configure("evenrow", background="white")

        self.populate_tree()

    def populate_tree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        try:
            records = user_manager.get_all_users_list() # Yeh ab 6 columns return karega
            for i, row in enumerate(records):
                tag = "evenrow" if i % 2 == 0 else "oddrow"
                self.tree.insert("", "end", values=row, tags=(tag,))
        except Exception as e:
            messagebox.showerror("Error", f"User records load nahi ho sake: {e}", parent=self.window)
            
    def get_selected_username(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please list se ek user select karein.", parent=self.window)
            return None
        return self.tree.item(selected_item, "values")[0]

    def open_add_user_window(self):
        add_edit_teacher_window.show_add_edit_window(self.window, self.populate_tree, self.role) 

    def open_edit_user_window(self):
        username = self.get_selected_username()
        if not username: return
        if username == 'admin':
            messagebox.showinfo("Info", "'admin' user ki details yahaan se edit nahi ki jaa sakti (Settings se karein).", parent=self.window)
            return
        try:
            current_data = user_manager.get_user_profile(username)
            if current_data:
                add_edit_teacher_window.show_add_edit_window(self.window, self.populate_tree, self.role, current_data) # Edit mode
            else:
                messagebox.showerror("Error", "User data fetch nahi ho saka.", parent=self.window)
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}", parent=self.window)

    def delete_user(self):
        username = self.get_selected_username()
        if not username: return
        if username == 'admin':
            messagebox.showerror("Error", "Default 'admin' user ko delete nahi kiya jaa sakta.", parent=self.window)
            return
        if not messagebox.askyesno("Confirm Delete", f"Kya aap user '{username}' ko hamesha ke liye delete karna chahte hain?", parent=self.window):
            return
        try:
            user_manager.delete_user(username)
            attendance_manager.log_activity(self.role, f"Deleted user: {username}")
            messagebox.showinfo("Success", f"User '{username}' delete ho gaya hai.", parent=self.window)
            self.populate_tree()
        except Exception as e:
            messagebox.showerror("Delete Error", f"User delete nahi ho saka: {e}", parent=self.window)

def show_teacher_dashboard(parent, role):
    TeacherDashboard(parent, role)