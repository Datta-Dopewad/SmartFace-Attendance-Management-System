# /DigitalFaceAttendanceSystem/student_management_logic.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import cv2
from PIL import Image, ImageTk
import attendance_manager
import face_recognition
import os

class StudentManagementLogic:
    # --- UPDATED: 'role' aur 'department' parameters add kiye ---
    def __init__(self, gui, role, department):
        self.gui = gui
        self.role = role # 'Admin' ya 'Teacher'
        self.department = department # Teacher ka department (e.g., 'IT') ya Admin ke liye None
        self.cap = None
        self.captured_images = []
        self.max_captures = 3

    # ... (start_webcam, stop_webcam, update_webcam_feed, capture_image, choose_file, display_image, update_capture_count functions mein koi change nahi) ...
    def start_webcam(self):
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                raise Exception("Could not open webcam.")
            self.gui.start_cam_button.config(text="Stop Camera", command=self.stop_webcam)
            self.gui.capture_button.config(state=tk.NORMAL)
            self.gui.choose_file_button.config(state=tk.DISABLED)
            self.update_webcam_feed()
        except Exception as e:
            messagebox.showerror("Camera Error", str(e), parent=self.gui.window)
    def stop_webcam(self):
        if self.cap:
            self.cap.release()
            self.cap = None
        self.gui.start_cam_button.config(text="Start Camera", command=self.start_webcam)
        self.gui.capture_button.config(state=tk.DISABLED)
        if len(self.captured_images) < self.max_captures:
            self.gui.choose_file_button.config(state=tk.NORMAL)
        self.gui.video_label.config(image=None)
        self.gui.video_label.imgtk = None
    def update_webcam_feed(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                h, w, _ = frame.shape
                cx, cy = w // 2, h // 2
                rh, rw = h // 2, w // 3
                cv2.rectangle(frame, (cx - rw // 2, cy - rh // 2), (cx + rw // 2, cy + rh // 2), (0, 255, 0), 2)
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2image)
                img_width = self.gui.video_label.winfo_width()
                img_height = self.gui.video_label.winfo_height()
                if img_width > 1 and img_height > 1:
                    img = img.resize((img_width, img_height), Image.LANCZOS)
                imgtk = ImageTk.PhotoImage(image=img)
                self.gui.video_label.imgtk = imgtk
                self.gui.video_label.config(image=imgtk)
            self.gui.video_label.after(10, self.update_webcam_feed)
    def capture_image(self):
        if not self.cap or not self.cap.isOpened():
            messagebox.showwarning("Warning", "Camera not started.", parent=self.gui.window)
            return
        ret, frame = self.cap.read()
        if ret:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            boxes = face_recognition.face_locations(rgb_frame)
            if not boxes:
                messagebox.showwarning("No Face", "Webcam se capture ki gayi image mein koi chehra nahi mila. Phir se try karein.", parent=self.gui.window)
                return
            self.captured_images.append(frame)
            self.update_capture_count()
    def choose_file(self):
        current_count = len(self.captured_images)
        if current_count >= self.max_captures:
            messagebox.showwarning("Capture Full", f"Aap pehle hi {self.max_captures} images select kar chuke hain.")
            return
        needed = self.max_captures - current_count
        filepaths = filedialog.askopenfilenames(
            title=f"Select {needed} image(s) (up to {self.max_captures} total)",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
        )
        if not filepaths:
            return
        if len(filepaths) > needed:
            messagebox.showwarning("Too Many Files", f"Aapko sirf {needed} aur image(s) ki zaroorat hai, lekin aapne {len(filepaths)} select ki hain.", parent=self.gui.window)
            return
        for filepath in filepaths:
            try:
                img_rgb = face_recognition.load_image_file(filepath)
                boxes = face_recognition.face_locations(img_rgb)
                if not boxes:
                    messagebox.showwarning("No Face", f"'{os.path.basename(filepath)}' mein koi chehra nahi mila. Is file ko skip kar diya gaya hai.", parent=self.gui.window)
                    continue 
                img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
                self.captured_images.append(img_bgr) 
                self.display_image(img_rgb) 
                self.update_capture_count()
                if len(self.captured_images) >= self.max_captures:
                    break
            except Exception as e:
                messagebox.showerror("Error", f"'{os.path.basename(filepath)}' ko load karne mein error: {e}", parent=self.gui.window)
        if len(self.captured_images) > 0:
            self.gui.start_cam_button.config(state=tk.DISABLED)
    def display_image(self, img_rgb):
        img_pil = Image.fromarray(img_rgb) 
        img_width = self.gui.video_label.winfo_width()
        img_height = self.gui.video_label.winfo_height()
        if img_width > 1 and img_height > 1:
            img_pil.thumbnail((img_width, img_height), Image.LANCZOS)
        imgtk = ImageTk.PhotoImage(image=img_pil)
        self.gui.video_label.imgtk = imgtk
        self.gui.video_label.config(image=imgtk)
    def update_capture_count(self):
        count = len(self.captured_images)
        status_text = f"Captured {count}/{self.max_captures} images"
        self.gui.capture_status_label.config(text=status_text)
        self.gui.capture_button.config(text=f"Capture from Webcam ({count})")
        if count >= self.max_captures:
            self.gui.capture_button.config(state=tk.DISABLED)
            self.gui.choose_file_button.config(state=tk.DISABLED)
            self.gui.save_button.config(state=tk.NORMAL)
            if self.cap:
                self.stop_webcam()
            messagebox.showinfo("Capture Complete", f"Captured {count} images. Ready to save.", parent=self.gui.window)

    # --- UPDATED: save_student ---
    def save_student(self):
        roll_no = self.gui.roll_entry.get().strip()
        name = self.gui.name_entry.get().strip()
        dob = self.gui.dob_entry.get().strip()
        department = self.gui.dept_entry.get().strip()
        class_name = self.gui.class_entry.get().strip()
        prn_no = self.gui.prn_entry.get().strip()
        contact_no = self.gui.contact_entry.get().strip()

        if not all([roll_no, name, dob, department, class_name, prn_no, contact_no]):
            messagebox.showerror("Validation Error", "All fields are required.", parent=self.gui.window)
            return
        
        # --- NAYA: Department Security Check ---
        if self.role == "Teacher":
            if department.lower() != self.department.lower():
                messagebox.showerror("Permission Denied", f"Aap sirf apne department ({self.department}) mein student add kar sakte hain.", parent=self.gui.window)
                return
        
        if len(self.captured_images) < self.max_captures:
            messagebox.showwarning("Warning", f"Please capture all {self.max_captures} images before saving.", parent=self.gui.window)
            return

        try:
            self.gui.save_button.config(text="Processing...", state=tk.DISABLED)
            self.gui.window.update_idletasks()

            attendance_manager.add_student(
                roll_no=roll_no, name=name, dob=dob, class_name=class_name, 
                department=department, prn_no=prn_no, contact_no=contact_no,
                images=self.captured_images
            )
            
            attendance_manager.log_activity(self.role, f"Registered new student. Roll: {roll_no}, Name: {name}")
            
            messagebox.showinfo("Success", f"Student {name} (Roll: {roll_no}) registered successfully.", parent=self.gui.window)
            self.reset_form()
        except ValueError as ve:
             messagebox.showerror("Error", str(ve), parent=self.gui.window)
             self.gui.save_button.config(text="Save Student", state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}", parent=self.gui.window)
            self.gui.save_button.config(text="Save Student", state=tk.NORMAL)

    def reset_form(self):
        self.captured_images = []
        self.gui.capture_status_label.config(text=f"Captured 0/{self.max_captures} images")
        self.gui.start_cam_button.config(text="Start Camera", command=self.start_webcam, state=tk.NORMAL)
        self.gui.choose_file_button.config(state=tk.NORMAL)
        self.gui.capture_button.config(state=tk.DISABLED, text="Capture from Webcam (0)")
        self.gui.save_button.config(state=tk.DISABLED)
        self.gui.video_label.config(image=None)
        self.gui.video_label.imgtk = None
        if self.cap:
            self.stop_webcam()
            
        self.gui.roll_entry.delete(0, tk.END)
        self.gui.name_entry.delete(0, tk.END)
        self.gui.class_entry.delete(0, tk.END)
        self.gui.prn_entry.delete(0, tk.END)
        self.gui.contact_entry.delete(0, tk.END)
        self.gui.dob_entry.delete(0, tk.END)
        
        # Department field ko reset karo (Teacher ke liye readonly rahega)
        if self.role == "Teacher":
            self.gui.dept_entry.config(state="normal")
            self.gui.dept_entry.delete(0, tk.END)
            self.gui.dept_entry.insert(0, self.department)
            self.gui.dept_entry.config(state="readonly")
        else:
            self.gui.dept_entry.delete(0, tk.END)
        
        self.gui.roll_entry.focus()

    def on_close(self):
        if self.cap:
            self.cap.release()
        self.gui.window.destroy()