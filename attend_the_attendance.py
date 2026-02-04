# /DigitalFaceAttendanceSystem/attend_the_attendance.py

import tkinter as tk
from tkinter import ttk, messagebox, Label
import cv2
import face_recognition
import numpy as np
from PIL import Image, ImageTk
import attendance_manager
from datetime import datetime
import os 
import manual_attendance_window 
import dlib 
from scipy.spatial import distance as dist 
import user_manager

# ... (Blink Detection code same rahega) ...
DLIB_SHAPE_PREDICTOR_PATH = "shape_predictor_68_face_landmarks.dat"
EYE_AR_THRESH = 0.25 
EYE_AR_CONSEC_FRAMES = 2
try:
    if not os.path.exists(DLIB_SHAPE_PREDICTOR_PATH):
        raise FileNotFoundError(f"Model file not found: {DLIB_SHAPE_PREDICTOR_PATH}")
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(DLIB_SHAPE_PREDICTOR_PATH)
    (lStart, lEnd) = (42, 48)
    (rStart, rEnd) = (36, 42)
except Exception as e:
    print(f"CRITICAL ERROR: Dlib model load nahi ho saka. {e}")
    predictor = None
def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5]); B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3]); ear = (A + B) / (2.0 * C)
    return ear

class AttendanceTaker:
    # --- UPDATED: 'department' parameter add karo ---
    def __init__(self, parent, session_id, role, liveness_enabled, unknown_logging_enabled, department):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Take Attendance (Live)")
        self.window.state('zoomed')

        self.session_id = session_id 
        self.role = role.lower()
        self.liveness_enabled = liveness_enabled
        self.unknown_logging_enabled = unknown_logging_enabled 
        self.department = department # <-- NAYA: Department store karo
        
        if predictor is None and self.liveness_enabled:
            messagebox.showerror("Liveness Error", "Dlib model file nahi mili. Liveness check disabled.")
            self.liveness_enabled = False
        
        self.cap = None
        self.known_encodings = []
        self.known_data = []
        self.marked_today = set()
        self.is_running = False
        self.last_unknown_log_time = None
        self.marked_students_list = []
        self.all_students_dict = {}
        self.blink_status = {}
        self.eye_closed_frames = {} 

        # ... (Layout code same rahega) ...
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))
        style.configure("Live.TLabel", font=("Helvetica", 12, "bold"))
        style.configure("Manual.TButton", font=("Helvetica", 11, "bold"), background="#f0ad4e", foreground="black")
        style.map("Manual.TButton", background=[('active', '#ec971f')])
        self.main_frame = ttk.Frame(self.window, padding=10)
        self.main_frame.pack(expand=True, fill=tk.BOTH)
        self.status_label = ttk.Label(self.main_frame, text="Loading encodings...", font=("Helvetica", 14), anchor="center")
        self.status_label.pack(pady=10)
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(expand=True, fill=tk.BOTH)
        self.live_list_frame = ttk.Frame(self.content_frame, width=350)
        self.live_list_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 10), pady=10)
        self.live_list_frame.pack_propagate(False)
        ttk.Label(self.live_list_frame, text="Live Attendance (Last 5)", style="Live.TLabel").pack(pady=5)
        self.live_list_tree = ttk.Treeview(self.live_list_frame, columns=("Roll No", "Name", "Time"), show="headings")
        self.live_list_tree.pack(expand=True, fill=tk.BOTH)
        self.live_list_tree.heading("Roll No", text="Roll No")
        self.live_list_tree.heading("Name", text="Name")
        self.live_list_tree.heading("Time", text="Time")
        self.live_list_tree.column("Roll No", width=60, anchor=tk.CENTER)
        self.live_list_tree.column("Name", width=150)
        self.live_list_tree.column("Time", width=100, anchor=tk.CENTER)
        self.live_list_tree.tag_configure("Present", foreground="green", font=("Helvetica", 10, "bold"))
        self.manual_button = ttk.Button(self.live_list_frame, text="Mark Manual", style="Manual.TButton", command=self.open_manual_marker)
        self.manual_button.pack(fill=tk.X, pady=10, ipady=5)
        self.video_label = Label(self.content_frame, bg="black")
        self.video_label.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10, pady=10)
        self.stop_button = ttk.Button(self.main_frame, text="Stop Attendance", command=self.on_close)
        self.stop_button.pack(pady=10)
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.start_processing()

    # --- UPDATED: start_processing ---
    def start_processing(self):
        try:
            # Sirf apne department ke students ko fetch karo
            self.all_students_dict = attendance_manager.get_student_details_dict(self.department)
            if not self.all_students_dict:
                msg = f"Department '{self.department}' mein koi student register nahi hai." if self.department else "System mein koi bhi student register nahi hai."
                messagebox.showwarning("Error", msg, parent=self.window)
                self.window.after(1000, self.on_close)
                return
            
            # Note: Encodings sabhi students ki load honi chahiye
            self.known_encodings, self.known_data = attendance_manager.load_encodings()
            if not self.known_encodings:
                self.status_label.config(text="No students registered.")
                messagebox.showwarning("No Data", "No student encodings found.", parent=self.window)
                self.window.after(1000, self.on_close)
                return
                
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                raise Exception("Could not open webcam.")
            self.status_label.config(text="Webcam started. Scanning for faces...")
            self.is_running = True
            self.update_feed()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start attendance: {e}", parent=self.window)
            self.on_close()

    # ... (update_live_list, manual_refresh_callback, open_manual_marker functions same hain) ...
    def update_live_list(self):
        for i in self.live_list_tree.get_children():
            self.live_list_tree.delete(i)
        for student_data in self.marked_students_list:
            self.live_list_tree.insert("", "end", values=student_data, tags=("Present",))
    def manual_refresh_callback(self, marked_list):
        for roll_no, name in marked_list:
            session_key = (roll_no, self.session_id)
            if session_key not in self.marked_today:
                self.marked_today.add(session_key)
                timestamp = datetime.now().strftime("%I:%M:%S %p") + " (M)"
                student_data = (roll_no, name, timestamp)
                self.marked_students_list.insert(0, student_data)
        self.marked_students_list = self.marked_students_list[:5]
        self.update_live_list()
    def open_manual_marker(self):
        absent_students_list = []
        # 'all_students_dict' ab pehle se hi filtered hai
        for roll_no, details in self.all_students_dict.items():
            session_key = (roll_no, self.session_id)
            if session_key not in self.marked_today:
                absent_students_list.append((roll_no, details['name']))
        if not absent_students_list:
            messagebox.showinfo("All Present", "Is department ke sabhi students pehle se hi present mark ho chuke hain.", parent=self.window)
            return
        manual_attendance_window.show_manual_window(
            parent=self.window, session_id=self.session_id,
            absent_students_list=absent_students_list,
            refresh_callback=self.manual_refresh_callback, role=self.role 
        )

    # --- UPDATED: update_feed ---
    def update_feed(self):
        if not self.is_running or not self.cap or not self.cap.isOpened():
            return
        ret, frame = self.cap.read()
        if not ret:
            self.video_label.after(10, self.update_feed)
            return
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        for face_encoding, face_location in zip(face_encodings, face_locations):
            matches = face_recognition.compare_faces(self.known_encodings, face_encoding, tolerance=0.6)
            name = "Unknown"
            roll = "N/A"
            color = (0, 0, 255) 
            top, right, bottom, left = face_location
            top *= 4; right *= 4; bottom *= 4; left *= 4
            liveness_text = "" 

            if True in matches:
                face_distances = face_recognition.face_distance(self.known_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                
                if matches[best_match_index]:
                    match_data = self.known_data[best_match_index]
                    
                    # --- NAYA: Department Check ---
                    # Check karo ki kya yeh student is teacher ke department ka hai
                    if str(match_data['roll']) not in self.all_students_dict:
                        name = "Not in Dept"
                        roll = match_data['roll']
                        color = (128, 0, 128) # Purple
                    else:
                        # Ab normal flow chalao
                        name = match_data['name']
                        roll = match_data['roll']
                        session_key = (roll, self.session_id)
                        
                        if session_key in self.marked_today:
                            color = (255, 165, 0) # Orange
                            self.status_label.config(text=f"Already Marked: {name} ({roll})")
                        else:
                            has_blinked = False
                            if self.liveness_enabled:
                                if self.blink_status.get(roll) == True:
                                    has_blinked = True
                                else:
                                    liveness_text = "Please Blink" 
                                    color = (0, 255, 255) # Yellow/Cyan
                            else:
                                has_blinked = True
                            
                            if has_blinked:
                                color = (0, 255, 0) # Green
                                success = attendance_manager.mark_attendance(roll, name, self.session_id)
                                if success:
                                    self.marked_today.add(session_key)
                                    self.status_label.config(text=f"Marked: {name} ({roll})")
                                    timestamp = datetime.now().strftime("%I:%M:%S %p")
                                    student_data = (roll, name, timestamp)
                                    self.marked_students_list.insert(0, student_data)
                                    self.marked_students_list = self.marked_students_list[:5]
                                    self.update_live_list()
                                else:
                                    self.marked_today.add(session_key)
            
            if self.liveness_enabled and name != "Unknown" and name != "Not in Dept":
                rect = dlib.rectangle(left, top, right, bottom)
                shape = predictor(gray, rect)
                shape = np.array([(shape.part(i).x, shape.part(i).y) for i in range(68)])
                leftEye = shape[lStart:lEnd]; rightEye = shape[rStart:rEnd]
                leftEAR = eye_aspect_ratio(leftEye); rightEAR = eye_aspect_ratio(rightEye)
                ear = (leftEAR + rightEAR) / 2.0
                if roll not in self.eye_closed_frames: self.eye_closed_frames[roll] = 0
                if roll not in self.blink_status: self.blink_status[roll] = False
                if ear < EYE_AR_THRESH:
                    self.eye_closed_frames[roll] += 1
                else:
                    if self.eye_closed_frames[roll] >= EYE_AR_CONSEC_FRAMES:
                        self.blink_status[roll] = True
                    self.eye_closed_frames[roll] = 0 
            
            if name == "Unknown" and self.unknown_logging_enabled: 
                now = datetime.now()
                if self.last_unknown_log_time is None or (now - self.last_unknown_log_time).total_seconds() > 5:
                    self.last_unknown_log_time = now
                    padding = 20
                    face_crop = frame[max(0, top - padding):min(frame.shape[0], bottom + padding), 
                                      max(0, left - padding):min(frame.shape[1], right + padding)]
                    try:
                        timestamp_str = now.strftime("%Y%m%d_%H%M%S")
                        filename = f"unknown_{timestamp_str}.png"
                        filepath = os.path.join(attendance_manager.UNKNOWN_LOGS_DIR, filename)
                        cv2.imwrite(filepath, face_crop)
                        self.status_label.config(text="Unknown face detected and logged.")
                    except Exception as e:
                        print(f"Error saving unknown face: {e}")

            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            display_text = f"{name} ({roll})" if not liveness_text else liveness_text
            cv2.putText(frame, display_text, (left + 6, bottom - 6), font, 0.7, (255, 255, 255), 1)

        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv2image)
        img_width = self.video_label.winfo_width()
        img_height = self.video_label.winfo_height()
        if img_width > 1 and img_height > 1:
            img = img.resize((img_width, img_height), Image.LANCZOS)
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_label.imgtk = imgtk
        self.video_label.config(image=imgtk)

        self.video_label.after(10, self.update_feed)

    def on_close(self):
        self.is_running = False
        if self.cap:
            self.cap.release()
        self.window.destroy()

# --- UPDATED: 'department' parameter add karo ---
def start_attendance(parent, session_id, role, liveness_enabled, unknown_logging_enabled, department):
    AttendanceTaker(parent, session_id, role, liveness_enabled, unknown_logging_enabled, department)