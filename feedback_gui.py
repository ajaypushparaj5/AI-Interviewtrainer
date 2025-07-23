

import tkinter as tk
from tkinter import filedialog,IntVar,Radiobutton,Button,Label
from main import run_detection_session, run_live_session
import time
import cv2
from ranker import rank_user_behavior 
from modelutils import analyze_emotions
from feedbackmaker import generate_feedback_doc,generate_feedback_folder
import os

class FeedbackApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Interview Trainer")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        self.strictness = "default"
        self.logs = []
        self.show_history = False
        self.video_path = None
        self.stats = None
        self.abnormal_thresholds = {
            "eye_contact_breaks": 4,
            "total_blinks": 20,
            "mouth_touch_count": 1,
            "nose_touch_count": 1,
            "eye_touch_count": 1,
            "ear_touch_count": 1,
            "neck_touch_count": 1,
            "arms_crossed_for_3_sec_count": 2,
            "slouching": 1,
            "leg_crossed_count": 2,
            "leg_bouncing_count": 2,
            "hand_on_hip_count": 2,
            "final_bpm": 20,
        }

        self.init_frames()
        self.show_home()

    def init_frames(self):
        self.home_frame = tk.Frame(self.root)
        self.live_frame = tk.Frame(self.root)
        self.loading_frame = tk.Frame(self.root)
        self.report_frame = tk.Frame(self.root)

        self.init_home()
        self.init_live()
        self.init_loading()
        self.init_report()

    def show_home(self):
        self.hide_all()
        self.home_frame.pack(fill="both", expand=True)

    def show_live(self):
        self.hide_all()
        self.live_frame.pack(fill="both", expand=True)

    def show_loading(self):
        self.hide_all()
        self.loading_frame.pack(fill="both", expand=True)
        self.root.update()  

    def show_report(self):
        self.hide_all()
        self.report_frame.pack(fill="both", expand=True)

    def hide_all(self):
        for frame in [self.home_frame, self.live_frame, self.loading_frame, self.report_frame]:
            frame.pack_forget()

    def init_home(self):
        title = tk.Label(self.home_frame, text="AI INTERVIEW TRAINER", font=("Helvetica", 24, "bold"))
        title.pack(pady=60)

        tk.Button(self.home_frame, text="Upload Video for Analysis", font=("Helvetica", 14), command=self.browse_video).pack(pady=10)
        tk.Button(self.home_frame, text="Live Webcam Eval", font=("Helvetica", 14), command=self.start_live_session).pack(pady=10)
        tk.Button(self.home_frame, text="Record Video for Analysis", font=("Helvetica", 14), command=self.record_video).pack(pady=10)
        tk.Button(self.home_frame, text="Analyze Folder of Videos", font=("Helvetica", 14), command=self.analyze_folder).pack(pady=10)
        tk.Button(self.home_frame, text="Adjust Thresholds", font=("Helvetica", 14), command=self.edit_thresholds).pack(pady=10)

    def edit_thresholds(self):
        popup = tk.Toplevel(self.root)
        popup.title("Adjust Thresholds")
        popup.geometry("400x500")
        popup.transient(self.root)
        popup.grab_set()

        Label(popup, text="Adjust Abnormal Thresholds", font=("Helvetica", 16)).pack(pady=20)

        self.threshold_vars = {}
        for key in self.abnormal_thresholds:
            var = IntVar(value=self.abnormal_thresholds[key])
            self.threshold_vars[key] = var
            frame = tk.Frame(popup)
            frame.pack(fill="x", padx=20, pady=5)
            Label(frame, text=key.replace("_", " ").title(), font=("Helvetica", 12)).pack(side="left")
            tk.Entry(frame, textvariable=var, width=5).pack(side="right")

        Button(popup, text="Save Changes", command=lambda: self.save_thresholds(popup)).pack(pady=20)
        
    def save_thresholds(self, popup):
        for key, var in self.threshold_vars.items():
            self.abnormal_thresholds[key] = var.get()
        popup.destroy()
        print(f"[INFO] Updated thresholds: {self.abnormal_thresholds}")
        
    
    def init_live(self):
        self.latest_log = tk.Label(self.live_frame, text="Waiting for log...", font=("Courier", 12), bg="#f4f4f4", width=80, height=4, anchor="nw", justify="left")
        self.latest_log.pack(pady=10)

        self.log_text = tk.Text(self.live_frame, height=20, width=85, font=("Courier", 10), bg="#f4f4f4")
        self.log_text.pack(padx=10, pady=5)
        self.log_text.pack_forget()

        btn_frame = tk.Frame(self.live_frame)
        btn_frame.pack()

        self.toggle_btn = tk.Button(btn_frame, text="Log History", command=self.toggle_log)
        self.toggle_btn.pack(side="left", padx=10)

        end_btn = tk.Button(btn_frame, text="End Session", command=self.show_log_report)
        end_btn.pack(side="left", padx=10)

    def init_loading(self):
        loading_label = tk.Label(self.loading_frame, text="Generating Report...", font=("Helvetica", 18))
        loading_label.pack(expand=True)

    def init_report(self):
        self.report_text = tk.Text(self.report_frame, height=25, width=100, font=("Courier", 10), bg="#f4f4f4")
        self.report_text.pack(pady=10)

        tk.Button(self.report_frame, text="Back to Home", command=self.show_home).pack(pady=5)
        
        tk.Button(self.report_frame, text="Generate Feedback Document", command=self.generate_feedback_doc).pack(pady=5)

    def browse_video(self):
        file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi *.mov")])
        if file_path:
            self.video_path = file_path
            self.root.after(100, self.start_session)  

    def start_session(self):
        self.show_live()
        self.logs.clear()
        self.root.after(100, self.launch_detection)  

    def launch_detection(self):
        self.write_log(f"[INFO] Analyzing video: {self.video_path}")
        try:
            self.stats = run_detection_session(video_path=self.video_path, log=self.write_log)
        except Exception as e:
            self.write_log(f"[ERROR] {str(e)}")
        self.write_log("[INFO] Analysis complete.")
        self.show_loading()
        self.ask_strictness()
        self.root.after(100, self.generate_and_show_rank)

    def start_live_session(self):
        self.video_path = None
        self.show_live()
        self.logs.clear()
        self.root.after(100, self.launch_live_detection)

    def launch_live_detection(self):
        self.write_log("[INFO] Starting live webcam session...")
        try:
            self.stats = run_live_session(log=self.write_log)
        except Exception as e:
            self.write_log(f"[ERROR] {str(e)}")
        self.write_log("[INFO] Live session ended.")
        self.show_loading()
        self.ask_strictness()
        self.root.after(100, self.generate_and_show_rank)

    def record_video(self):
        self.video_path = "recorded_session.avi"
        self.write_log("[INFO] Recording started...")
        cap = cv2.VideoCapture(0)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(self.video_path, fourcc, 20.0, (640, 480))
        start_time = time.time()
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret or time.time() - start_time > 20:
                break
            out.write(frame)
            cv2.imshow('Recording - Press Q to stop', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        out.release()
        cv2.destroyAllWindows()
        self.confirm_evaluation_prompt()

    def confirm_evaluation_prompt(self):
        self.hide_all()
        prompt_frame = tk.Frame(self.root)
        prompt_frame.pack(fill="both", expand=True)

        label = tk.Label(prompt_frame, text="Video recorded. Ready to evaluate?", font=("Helvetica", 16))
        label.pack(pady=40)

        btn_frame = tk.Frame(prompt_frame)
        btn_frame.pack()

        def evaluate_and_show_score():
            prompt_frame.pack_forget()
            self.root.after(100, self.start_session)
            self.show_loading()

        yes_btn = tk.Button(btn_frame, text="Yes", font=("Helvetica", 14), command=evaluate_and_show_score)
        yes_btn.pack(side="left", padx=20)

        no_btn = tk.Button(btn_frame, text="Retake", font=("Helvetica", 14), command=lambda: [prompt_frame.pack_forget(), self.record_video()])
        no_btn.pack(side="left", padx=20)

        cancel_btn = tk.Button(prompt_frame, text="Back to Home", font=("Helvetica", 12), command=lambda: [prompt_frame.pack_forget(), self.show_home()])
        cancel_btn.pack(pady=20)

    def generate_and_show_rank(self):
        if self.video_path:
            self.write_log("[INFO] Analyzing facial expressions...")
            emotion_stats = analyze_emotions(self.video_path)
            self.write_log(f"[INFO] Emotion stats: {emotion_stats}")
        else:
            emotion_stats = {
                'happy': 0,
                'sad': 0,
                'fear': 0,
                'angry': 0,
                'disgust': 0,
                'neutral': 0,
                'surprise': 0
            }

        grade = rank_user_behavior(self.stats, emotion_stats,self.strictness, self.abnormal_thresholds)
        self.logs.append(f"[SCORE] {grade['rubric_scores']}")
        self.logs.append(f"[RESULT] Total Score: {grade['total_score']}, Average Score: {grade['average_score']} , Rank: {grade['rating']}")
        self.stats['grade'] = grade
        self.show_log_report()

    def write_log(self, message):
        self.logs.append(str(message))
        self.latest_log.config(text=message)
        if self.show_history:
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert("end", message + "\n")
            self.log_text.see("end")
            self.log_text.config(state=tk.DISABLED)

    def toggle_log(self):
        self.show_history = not self.show_history
        if self.show_history:
            self.toggle_btn.config(text="Hide History")
            self.log_text.config(state=tk.NORMAL)
            self.log_text.delete("1.0", "end")
            self.log_text.insert("end", "\n".join(self.logs))
            self.log_text.config(state=tk.DISABLED)
            self.log_text.pack()
        else:
            self.toggle_btn.config(text="Log History")
            self.log_text.pack_forget()

    def show_log_report(self):
        self.show_report()
        self.report_text.delete("1.0", "end")
        self.report_text.insert("end", "\n".join(self.logs))
    
    def analyze_folder(self):
        folder_path = filedialog.askdirectory()
        if not folder_path:
            return

        self.ask_strictness()
        feedback_dir = os.path.join("feedback", os.path.basename(folder_path) + "_batch")
        os.makedirs(feedback_dir, exist_ok=True)

        for file in os.listdir(folder_path):
            if file.lower().endswith((".mp4", ".avi", ".mov")):
                try:
                    video_path = os.path.join(folder_path, file)
                    self.write_log(f"[INFO] Processing: {file}")
                    stats = run_detection_session(video_path=video_path, log=self.write_log)
                    print("[INFO] Analyzing facial expressions...")
                    emotion_stats = analyze_emotions(video_path)
                    print(f"[INFO] Emotion stats: {emotion_stats}")
                    grade = rank_user_behavior(stats, emotion_stats, self.strictness, self.abnormal_thresholds)
                    stats['grade'] = grade
                    out_name = os.path.splitext(file)[0] + ".docx"
                    custom_filename=os.path.join(feedback_dir, out_name)
                    print(f"[INFO] Saving feedback to {custom_filename}")
                    generate_feedback_folder(stats,emotion_stats,grade,custom_filename,self.abnormal_thresholds,self.strictness)
                    print(f"[SUCCESS] Saved: {out_name}")
                except Exception as e:
                    print(f"[ERROR] Failed on {file}: {str(e)}")

        print("[INFO] Folder analysis complete.")
       
    def ask_strictness(self):
        popup = tk.Toplevel(self.root)
        popup.title("Select Analysis Strictness")
        popup.geometry("300x500")
        popup.transient(self.root)
        popup.grab_set()
        
        label = tk.Label(popup, text="Choose strictness level:", font=("Helvetica", 14))
        label.pack(pady=20)
        choice_var = IntVar(value=1)
        options = [("longer videos (More than 10 min)",2), ("shorter videos (Less than 10 min)",3), ("very short videos (Less than 5 min)",4),("default",1)]
        
    
        for label, value in options:
            rb = tk.Radiobutton(popup, text=label, variable=choice_var, value=value, font=("Helvetica", 12))
            rb.pack(anchor="w", padx=20)
            
        def submit():
            self.strictness = choice_var.get()
            popup.destroy()
            
        submit_btn = tk.Button(popup, text="Submit", command=submit, font=("Helvetica", 12))
        submit_btn.pack(pady=20)
        
        self.root.wait_window(popup) 
        
    def generate_feedback_doc(self):
        if not self.stats or 'grade' not in self.stats:
            print("[ERROR] No stats available to generate feedback document.")
            return
        try:
            report = self.stats.copy()
            generate_feedback_doc(report,self.abnormal_thresholds ,self.strictness)
            print("[INFO] Feedback document generated successfully.")
        except Exception as e:
            print(f"[ERROR] Failed to generate feedback document: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FeedbackApp(root)
    root.mainloop()
