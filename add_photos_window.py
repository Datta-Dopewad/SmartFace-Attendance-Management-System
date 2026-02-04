# /DigitalFaceAttendanceSystem/add_photos_window.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, Label
import cv2
from PIL import Image, ImageTk
import attendance_manager
import face_recognition
import os

# --- UPDATED: 'role' parameter add karo ---
class AddPhotosWindow:
    def __init__(self, parent, roll_no, name, role):
        self.parent = parent
        self.roll_no = roll_no
        self.name = name
        self.role = role.lower() # 'admin'
        
        self.window = tk.Toplevel(parent)
        self.window.title(f"Add Photos for {name} ({roll_no})")
        self.window.geometry("800x600")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.cap = None
        self.captured_images = []
        self.max_captures = 3

        # --- Layout (No Change) ---
        self.main_frame = ttk.Frame(self.window, padding=20)
        self.main_frame.pack(expand=True, fill=tk.BOTH)
        self.form_frame = ttk.Frame(self.main_frame, padding=10)
        self.form_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        ttk.Label(self.form_frame, text="Add New Photos", font=("Helvetica", 16, "bold")).pack(pady=10)
        ttk.Label(self.form_frame, text=f"Student: {name}", font=("Helvetica", 12)).pack(anchor="w", pady=2)
        ttk.Label(self.form_frame, text=f"Roll No: {roll_no}", font=("Helvetica", 12)).pack(anchor="w", pady=2)
        self.capture_status_label = ttk.Label(self.form_frame, text="Captured 0/3 new images", font=("Helvetica", 10, "italic"))
        self.capture_status_label.pack(pady=20)
        self.camera_frame = ttk.Frame(self.main_frame)
        self.camera_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=10)
        self.video_label = Label(self.camera_frame, bg="black")
        self.video_label.pack(expand=True, fill=tk.BOTH, pady=10)
        self.button_frame = ttk.Frame(self.form_frame)
        self.button_frame.pack(side=tk.BOTTOM, pady=20, fill=tk.X)
        self.start_cam_button = ttk.Button(self.button_frame, text="Start Camera", command=self.start_webcam)
        self.start_cam_button.pack(fill=tk.X, pady=2)
        self.choose_file_button = ttk.Button(self.button_frame, text="Choose File(s)", command=self.choose_file)
        self.choose_file_button.pack(fill=tk.X, pady=2)
        self.capture_button = ttk.Button(self.button_frame, text="Capture from Webcam (0)", command=self.capture_image, state=tk.DISABLED)
        self.capture_button.pack(fill=tk.X, pady=2)
        self.save_button = ttk.Button(self.button_frame, text="Save New Photos", command=self.save_new_photos, state=tk.DISABLED)
        self.save_button.pack(fill=tk.X, pady=(10, 2))
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

    # --- Logic Functions (No Change) ---
    def start_webcam(self):
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                raise Exception("Could not open webcam.")
            self.start_cam_button.config(text="Stop Camera", command=self.stop_webcam)
            self.capture_button.config(state=tk.NORMAL)
            self.choose_file_button.config(state=tk.DISABLED)
            self.update_webcam_feed()
        except Exception as e:
            messagebox.showerror("Camera Error", str(e), parent=self.window)
    def stop_webcam(self):
        if self.cap:
            self.cap.release()
            self.cap = None
        self.start_cam_button.config(text="Start Camera", command=self.start_webcam)
        self.capture_button.config(state=tk.DISABLED)
        if len(self.captured_images) < self.max_captures:
            self.choose_file_button.config(state=tk.NORMAL)
        self.video_label.config(image=None)
        self.video_label.imgtk = None
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
                img_width = self.video_label.winfo_width()
                img_height = self.video_label.winfo_height()
                if img_width > 1 and img_height > 1:
                    img = img.resize((img_width, img_height), Image.LANCZOS)
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_label.imgtk = imgtk
                self.video_label.config(image=imgtk)
            self.video_label.after(10, self.update_webcam_feed)
    def capture_image(self):
        if not self.cap or not self.cap.isOpened():
            messagebox.showwarning("Warning", "Camera not started.", parent=self.window)
            return
        ret, frame = self.cap.read()
        if ret:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            boxes = face_recognition.face_locations(rgb_frame)
            if not boxes:
                messagebox.showwarning("No Face", "Webcam se capture ki gayi image mein koi chehra nahi mila. Phir se try karein.", parent=self.window)
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
            messagebox.showwarning("Too Many Files", f"Aapko sirf {needed} aur image(s) ki zaroorat hai, lekin aapne {len(filepaths)} select ki hain.", parent=self.window)
            return
        for filepath in filepaths:
            try:
                img_rgb = face_recognition.load_image_file(filepath)
                boxes = face_recognition.face_locations(img_rgb)
                if not boxes:
                    messagebox.showwarning("No Face", f"'{os.path.basename(filepath)}' mein koi chehra nahi mila. Is file ko skip kar diya gaya hai.", parent=self.window)
                    continue 
                img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
                self.captured_images.append(img_bgr) 
                self.display_image(img_rgb) 
                self.update_capture_count()
                if len(self.captured_images) >= self.max_captures:
                    break
            except Exception as e:
                messagebox.showerror("Error", f"'{os.path.basename(filepath)}' ko load karne mein error: {e}", parent=self.window)
        if len(self.captured_images) > 0:
            self.start_cam_button.config(state=tk.DISABLED) # self.gui ko self se badla
    def display_image(self, img_rgb):
        img_pil = Image.fromarray(img_rgb) 
        img_width = self.video_label.winfo_width()
        img_height = self.video_label.winfo_height()
        if img_width > 1 and img_height > 1:
            img_pil.thumbnail((img_width, img_height), Image.LANCZOS)
        imgtk = ImageTk.PhotoImage(image=img_pil)
        self.video_label.imgtk = imgtk
        self.video_label.config(image=imgtk)
    def update_capture_count(self):
        count = len(self.captured_images)
        status_text = f"Captured {count}/{self.max_captures} images"
        self.capture_status_label.config(text=status_text)
        self.capture_button.config(text=f"Capture from Webcam ({count})")
        if count >= self.max_captures:
            self.capture_button.config(state=tk.DISABLED)
            self.choose_file_button.config(state=tk.DISABLED)
            self.save_button.config(state=tk.NORMAL)
            if self.cap:
                self.stop_webcam()
            messagebox.showinfo("Capture Complete", f"Captured {count} images. Ready to save.", parent=self.window)

    # --- UPDATED: save_new_photos ---
    def save_new_photos(self):
        """Nayi photos ko save karta hai."""
        
        if len(self.captured_images) < self.max_captures:
            messagebox.showwarning("Warning", f"Please capture all {self.max_captures} new images before saving.", parent=self.window)
            return

        try:
            self.save_button.config(text="Processing...", state=tk.DISABLED)
            self.window.update_idletasks()

            attendance_manager.add_photos_to_student(
                roll_no=self.roll_no, 
                name=self.name,
                images=self.captured_images
            )
            
            # --- NAYA LOG ---
            attendance_manager.log_activity(self.role, f"Added {len(self.captured_images)} new photos to student. Roll: {self.roll_no}")
            
            messagebox.showinfo("Success", f"{len(self.captured_images)} nayi photos {self.name} ke liye add ho gayi hain.\nSystem ab update ho gaya hai.", parent=self.window)
            self.on_close()

        except ValueError as ve:
             messagebox.showerror("Error", str(ve), parent=self.window)
             self.save_button.config(text="Save New Photos", state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}", parent=self.window)
            self.save_button.config(text="Save New Photos", state=tk.NORMAL)

    def on_close(self):
        if self.cap:
            self.cap.release()
        self.window.destroy()

# --- UPDATED: 'role' parameter add karo ---
def show_add_photos_window(parent, roll_no, name, role):
    AddPhotosWindow(parent, roll_no, name, role)