# /DigitalFaceAttendanceSystem/student_profile_window.py

import tkinter as tk
from tkinter import ttk, messagebox, Label
import attendance_manager
import cv2
from PIL import Image, ImageTk

class StudentProfileWindow:
    def __init__(self, parent, roll_no, name):
        self.parent = parent
        self.roll_no = roll_no
        self.name = name
        
        self.window = tk.Toplevel(parent)
        self.window.title(f"Student Profile: {name}")
        self.window.state('zoomed') # Full-screen
        self.window.configure(bg='#f0f2f5') # Main background color
        
        self.window.transient(parent)
        self.window.grab_set()

        # --- Styles ---
        style = ttk.Style()
        style.theme_use('clam')
        
        # Backgrounds
        style.configure("Bg.TFrame", background="#f0f2f5")
        style.configure("Card.TFrame", background="white")

        # Page Title
        style.configure("PageHeader.TLabel", font=("Helvetica", 24, "bold"), background="#f0f2f5", foreground="#333333")
        
        # Photo Card Styles
        style.configure("StudentName.TLabel", font=("Helvetica", 22, "bold"), background="white", foreground="#0056b3") # Dark Blue
        style.configure("StudentRoll.TLabel", font=("Helvetica", 14), background="white", foreground="#555")

        # Details Card Styles
        style.configure("SectionHeader.TLabel", font=("Helvetica", 16, "bold"), background="white", foreground="#333")
        style.configure("Info.TLabel", font=("Helvetica", 12), background="white", foreground="#6c757d") # Label (e.g., "Department:")
        style.configure("Data.TLabel", font=("Helvetica", 12, "bold"), background="white", foreground="#000") # Data (e.g., "IT")
        
        # --- Layout ---
        # Main frame (fills the window)
        main_frame = ttk.Frame(self.window, style="Bg.TFrame", padding=20)
        main_frame.pack(expand=True, fill=tk.BOTH)

        # Page Title
        ttk.Label(main_frame, text="Student Profile", style="PageHeader.TLabel").pack(pady=(10, 20))

        # Card Frame (holds photo and details)
        card_frame = ttk.Frame(main_frame, style="Card.TFrame", relief="solid", borderwidth=1)
        card_frame.pack(expand=True, fill=tk.BOTH, padx=50, pady=20)
        
        # --- Left Panel (Photo, Name, Roll) ---
        left_panel = ttk.Frame(card_frame, style="Card.TFrame", width=400)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(30, 40), pady=30)
        left_panel.pack_propagate(False) # Width ko fix rakho

        self.photo_label = Label(left_panel, bg="#e0e0e0", width=350, height=350, relief="solid", borderwidth=1)
        self.photo_label.pack(pady=(0, 20))

        self.name_label = ttk.Label(left_panel, text="Loading Name...", style="StudentName.TLabel", anchor="center")
        self.name_label.pack(fill=tk.X)
        
        self.roll_label = ttk.Label(left_panel, text="Roll No: ...", style="StudentRoll.TLabel", anchor="center")
        self.roll_label.pack(fill=tk.X, pady=5)

        # --- Right Panel (Details) ---
        right_panel = ttk.Frame(card_frame, style="Card.TFrame")
        right_panel.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=(0, 30), pady=30)
        
        ttk.Label(right_panel, text="Student Information", style="SectionHeader.TLabel").pack(anchor="w", pady=(0, 10))
        ttk.Separator(right_panel, orient="horizontal").pack(fill='x')
        
        # Details grid frame
        details_frame = ttk.Frame(right_panel, style="Card.TFrame")
        details_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Data load karne ke liye placeholders
        self.dept_frame = self._add_detail_row(details_frame, 0, "Department:")
        self.class_frame = self._add_detail_row(details_frame, 1, "Class Name:")
        self.prn_frame = self._add_detail_row(details_frame, 2, "PRN No:")
        self.contact_frame = self._add_detail_row(details_frame, 3, "Contact No:")
        self.dob_frame = self._add_detail_row(details_frame, 4, "Date of Birth:")

        # --- Data Load Karo ---
        self.load_profile_data()

        # Close button
        ttk.Button(right_panel, text="Close", command=self.window.destroy, width=15).pack(side=tk.BOTTOM, anchor="e", pady=(20, 0), ipady=5)

    def _add_detail_row(self, parent, row, label_text, value_text="..."):
        """Details frame mein ek row (grid layout mein) add karta hai."""
        
        # Child frame banata hai taaki data update karna aasaan ho
        row_frame = ttk.Frame(parent, style="Card.TFrame")
        row_frame.grid(row=row, column=0, sticky="ew", pady=10)
        
        ttk.Label(row_frame, text=label_text, style="Info.TLabel", width=15, anchor="w").pack(side=tk.LEFT)
        ttk.Label(row_frame, text=value_text, style="Data.TLabel", anchor="w").pack(side=tk.LEFT)
        return row_frame

    def _update_detail_row(self, frame, label_text, value_text):
        """Pehle se bani row ko naye data se update karta hai."""
        # Purane widgets ko destroy karo
        for widget in frame.winfo_children():
            widget.destroy()
        # Naye widgets add karo
        ttk.Label(frame, text=label_text, style="Info.TLabel", width=15, anchor="w").pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Label(frame, text=value_text, style="Data.TLabel", anchor="w").pack(side=tk.LEFT, padx=5, pady=5)

    def load_profile_data(self):
        """Database se photo aur details load karta hai."""
        try:
            # 1. Details Load Karo
            details = attendance_manager.get_student_by_roll(self.roll_no)
            if not details:
                raise Exception("Student details not found in database.")
            
            # 2. Photo Load Karo
            photo_path = attendance_manager.get_student_photo_path(self.roll_no, self.name)
            
            if photo_path:
                img_bgr = cv2.imread(photo_path)
                img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
                img_pil = Image.fromarray(img_rgb)
                img_pil.thumbnail((350, 350), Image.LANCZOS) # Resize
                img_tk = ImageTk.PhotoImage(img_pil)
                
                self.photo_label.config(image=img_tk, width=350, height=350)
                self.photo_label.image = img_tk # Reference rakho
            else:
                self.photo_label.config(text="No Photo Found", fg="white", font=("Helvetica", 16))

            # 3. Dynamic labels aur details update karo
            self.name_label.config(text=details.get("name", "N/A"))
            self.roll_label.config(text=f"Roll No: {details.get('roll_no', 'N/A')}")
            
            # Placeholders ko real data se update karo
            self._update_detail_row(self.dept_frame, "Department:", details.get("department", "N/A"))
            self._update_detail_row(self.class_frame, "Class Name:", details.get("class_name", "N/A"))
            self._update_detail_row(self.prn_frame, "PRN No:", details.get("prn_no", "N/A"))
            self._update_detail_row(self.contact_frame, "Contact No:", details.get("contact_no", "N/A"))
            self._update_detail_row(self.dob_frame, "Date of Birth:", details.get("dob", "N/A"))
            
        except Exception as e:
            messagebox.showerror("Error", f"Student profile load nahi ho saka: {e}", parent=self.window)
            self.window.destroy()


def show_student_profile(parent, roll_no, name):
    StudentProfileWindow(parent, roll_no, name)