from feedback_gui import FeedbackApp
import tkinter as tk
import os

class MockApp(FeedbackApp):
    def __init__(self):
        self.abnormal_thresholds = {
            "eye_contact_breaks": 4,
            "total_blinks": 20,
            "mouth_touch_count": 1,
            "nose_touch_count": 1,
            "eye_touch_count": 1,
            "ear_touch_count": 1,
            "neck_touch_count": 1,
            "arms_crossed_for_3_sec_count": 4,
            "slouching": 3,
            "hand_on_hip_count": 2,
            'hands_outside_gesture_box_count': 20,
            'hands_clenched_count': 0,
            'hands_behind_back_count': 2,
            'hands_in_pockets_count': 2,
            'upper_body_sway_percent':40,
            "final_bpm": 20,
        }
        self.strictness = 1
        
    def write_log(self, message):
        print(f"[GUI LOG] {message}")

    def ask_strictness(self):
        pass

import sys
app = MockApp()

folder_path = "test_vids"
os.makedirs(folder_path, exist_ok=True)
with open(os.path.join(folder_path, "dummy.mp4"), "wb") as f:
    f.write(b"0" * 1024)

# reproduce the analyze_folder logic manually
from main import run_detection_session
from modelutils import analyze_emotions
from ranker import rank_user_behavior 
from feedbackmaker import generate_feedback_folder

feedback_dir = os.path.join("feedback", os.path.basename(folder_path) + "_batch")
os.makedirs(feedback_dir, exist_ok=True)
print(f"Checking folder: {folder_path}")

for file in os.listdir(folder_path):
    if file.lower().endswith((".mp4", ".avi", ".mov")):
        try:
            video_path = os.path.join(folder_path, file)
            app.write_log(f"[INFO] Processing: {file}")
            stats = run_detection_session(video_path=video_path, log=app.write_log)
            print("[INFO] Analyzing facial expressions...")
            emotion_stats = analyze_emotions(video_path)
            print(f"[INFO] Emotion stats: {emotion_stats}")
            grade = rank_user_behavior(stats, emotion_stats, app.strictness, app.abnormal_thresholds)
            stats['grade'] = grade
            out_name = os.path.splitext(file)[0] + ".docx"
            custom_filename=os.path.join(feedback_dir, out_name)
            print(f"[INFO] Saving feedback to {custom_filename}")
            generate_feedback_folder(stats,emotion_stats,grade,custom_filename,app.abnormal_thresholds,app.strictness)
            print(f"[SUCCESS] Saved: {out_name}")
        except Exception as e:
            print(f"[ERROR] Failed on {file}: {str(e)}")

print("[INFO] Folder analysis complete.")
