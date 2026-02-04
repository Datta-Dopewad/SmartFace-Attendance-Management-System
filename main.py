# /DigitalFaceAttendanceSystem/main.py

import login_screen
import attendance_manager
import sys
import os

def main():
    # Set high DPI awareness for Windows (improves GUI scaling)
    if os.name == 'nt':
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass # Ignore if it fails
            
    try:
        # 1. Setup environment (create files/folders if they don't exist)
        print("Initializing environment...")
        attendance_manager.setup_environment()
        print("Setup complete.")
        
        # 2. Launch the login screen
        login_screen.show_login_screen()
        
    except Exception as e:
        print(f"FATAL ERROR: Failed to start application.\n{e}")
        # In a real app, you might show this in a basic TK error box
        sys.exit(1)

if __name__ == "__main__":
    main()







