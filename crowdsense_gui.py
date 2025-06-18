import tkinter as tk
from tkinter import Label, Button
import cv2
from PIL import Image, ImageTk

# Load pre-recorded video
cap = cv2.VideoCapture("C:/Users/ADITYA SHARMA/Downloads/1643-148614430_small.mp4")  # Replace with your actual video file

# Create Tkinter window
window = tk.Tk()
window.title("CrowdSense - Video Playback")
window.geometry("800x600")

# Display label for video
video_label = Label(window)
video_label.pack()

# Placeholder for your crowd detection function
def detect_crowd(frame):
    # Put your model's detection logic here
    return frame

# Show video in GUI
def update_frame():
    ret, frame = cap.read()
    if ret:
        frame = detect_crowd(frame)
        frame = cv2.resize(frame, (800, 450))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        video_label.imgtk = imgtk
        video_label.configure(image=imgtk)
        video_label.after(30, update_frame)
    else:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Loop safely
        video_label.after(1000, update_frame)


# Buttons
def start_video():
    update_frame()

def stop_video():
    cap.release()
    window.destroy()

Button(window, text="Start", command=start_video).pack(pady=5)
Button(window, text="Exit", command=stop_video).pack(pady=5)

# Run app
window.mainloop()
