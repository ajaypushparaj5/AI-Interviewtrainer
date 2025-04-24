import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
from webcam_utils import webcamframe, bgr2rgb

class FeedbackGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AI Interview Trainer")
        self.root.geometry("800x600")

        # Webcam frame
        self.video_label = ttk.Label(self.root)
        self.video_label.pack(pady=10)

        # Feedback label
        self.feedback_text = tk.Label(self.root, text="Initializing...", font=("Arial", 14))
        self.feedback_text.pack(pady=5)

        # Text box for feedback logs
        self.log_box = tk.Text(self.root, height=10, width=90)
        self.log_box.pack(pady=10)

        # Start capturing video in a separate thread
        self.cap = cv2.VideoCapture(0)
        self.update_video()

    def update_video(self):
        ret, frame = self.cap.read()
        if ret:
            # Flip the frame horizontally to simulate mirror effect
            flipped_frame = cv2.flip(frame, 1)  # Flip horizontally (mirror effect)
            
            # Convert the flipped frame from BGR to RGB
            rgb = cv2.cvtColor(flipped_frame, cv2.COLOR_BGR2RGB)
            
            # Convert to PIL Image for Tkinter display
            img = Image.fromarray(rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            
            # Update the label with the image
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        # Refresh the frame every 10ms
        self.root.after(10, self.update_video)
        
        
        
        # frame = webcamframe(self.cap)
        # if frame is not None:
        #     rgb = bgr2rgb(frame)
        #     img = Image.fromarray(rgb)
        #     imgtk = ImageTk.PhotoImage(image=img)
        #     self.video_label.imgtk = imgtk
        #     self.video_label.configure(image=imgtk)
        # self.root.after(10, self.update_video)

    def update_feedback_label(self, text):
        self.feedback_text.config(text=text)

    def log_feedback(self, text):
        self.log_box.insert(tk.END, text + "\n")
        self.log_box.see(tk.END)

    def start(self):
        self.root.mainloop()

    def stop(self):
        self.cap.release()
        self.root.destroy()
