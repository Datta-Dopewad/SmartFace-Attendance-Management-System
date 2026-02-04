# /DigitalFaceAttendanceSystem/activity_log_viewer.py

import tkinter as tk
from tkinter import ttk, messagebox
import attendance_manager

class ActivityLogViewer:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("User Activity Log (Audit Trail)")
        self.window.state('zoomed')
        self.window.configure(bg='#f0f2f5')

        # --- Style Configuration ---
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))
        style.configure("TButton", font=("Helvetica", 11))
        style.configure("Header.TLabel", font=("Helvetica", 16, "bold"), background="#f0f2f5")
        
        # --- Main Layout ---
        self.main_frame = ttk.Frame(self.window, padding=20)
        self.main_frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(self.main_frame, text="User Activity Log (Audit Trail)", style="Header.TLabel").pack(pady=10)
        ttk.Label(self.main_frame, text="Yahaan system mein ki gayi sabhi activities record hoti hain (sabse nayi sabse upar).", background="#f0f2f5").pack(pady=(0,10))

        # --- Button Frame ---
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, pady=10)
        
        self.refresh_button = ttk.Button(self.button_frame, text="Refresh Log", command=self.populate_tree)
        self.refresh_button.pack(side=tk.LEFT, padx=5)
        
        self.close_button = ttk.Button(self.button_frame, text="Close", command=self.window.destroy)
        self.close_button.pack(side=tk.RIGHT, padx=5)

        # --- Treeview (Log Table) ---
        self.tree_frame = ttk.Frame(self.main_frame)
        self.tree_frame.pack(expand=True, fill=tk.BOTH, pady=10)

        self.tree_scroll_y = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL)
        self.tree_scroll_x = ttk.Scrollbar(self.tree_frame, orient=tk.HORIZONTAL)

        self.tree_columns = ("Timestamp", "User", "Action")
        self.tree = ttk.Treeview(
            self.tree_frame,
            columns=self.tree_columns,
            show="headings",
            yscrollcommand=self.tree_scroll_y.set,
            xscrollcommand=self.tree_scroll_x.set
        )
        
        self.tree_scroll_y.config(command=self.tree.yview)
        self.tree_scroll_x.config(command=self.tree.xview)
        self.tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(expand=True, fill=tk.BOTH)

        # Columns define karo
        self.tree.heading("Timestamp", text="Timestamp")
        self.tree.heading("User", text="User")
        self.tree.heading("Action", text="Action")
        
        self.tree.column("Timestamp", width=180, anchor="w")
        self.tree.column("User", width=100, anchor="center")
        self.tree.column("Action", width=500)

        # --- NAYA TAG (RED COLOR) ---
        self.tree.tag_configure("FailedLogin", foreground="red", font=("Helvetica", 9, "bold"))
        self.tree.tag_configure("oddrow", background="#E8E8E8")
        self.tree.tag_configure("evenrow", background="white")

        # Initial data load
        self.populate_tree()

    def populate_tree(self):
        """Table ko clear karke saara log data bharta hai."""
        for i in self.tree.get_children():
            self.tree.delete(i)
        try:
            logs = attendance_manager.get_activity_log()
            
            for i, row in enumerate(logs):
                # row = [Timestamp, User, Action]
                action_text = row[2] 
                
                # Default tag
                bg_tag = "evenrow" if i % 2 == 0 else "oddrow"
                final_tags = (bg_tag,) # Tuple
                
                # --- NAYA LOGIC ---
                # Agar 'Action' mein "FAILED LOGIN" text hai, toh red tag add karo
                if "FAILED LOGIN" in action_text:
                    final_tags += ("FailedLogin",)
                # --- NAYA LOGIC KHATAM ---
                
                self.tree.insert("", "end", values=row, tags=final_tags)

        except Exception as e:
            messagebox.showerror("Error", f"Activity log load nahi ho saka: {e}", parent=self.window)

def show_activity_log_viewer(parent):
    ActivityLogViewer(parent)