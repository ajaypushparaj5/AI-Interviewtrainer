
import cv2
import mediapipe as mp
import time
from collections import deque
mp_drawing = mp.solutions.drawing_utils


def display_facial_landmarks(rgb_frame, face_landmarks):
    if face_landmarks:
        iris_indices = [468, 469, 470, 471, 472, 473, 474, 475, 476, 477]
        h, w, _ = rgb_frame.shape

        for idx in iris_indices:
            pt = face_landmarks.landmark[idx]
            x, y = int(pt.x * w), int(pt.y * h)
            cv2.circle(rgb_frame, (x, y), 2, (255, 0, 0), -1)

        mp_drawing.draw_landmarks(
            image=rgb_frame,
            landmark_list=face_landmarks,
            connections=mp.solutions.face_mesh.FACEMESH_TESSELATION,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp_drawing.DrawingSpec(
                color=(0, 255, 0), thickness=1, circle_radius=1
            )
        )
    return rgb_frame



def get_eye_distance(rgb_frame, face_landmarks, top_idx, bottom_idx):
    h, w, _ = rgb_frame.shape
    if face_landmarks:
        top = face_landmarks.landmark[top_idx]
        bottom = face_landmarks.landmark[bottom_idx]
        top_y = int(top.y * h)
        bottom_y = int(bottom.y * h)
        return abs(top_y - bottom_y)
    return 0



def gaze_detector(rgb_frame, face_landmarks, lastgazetime):
    currenttime = time.time()
    h, w, _ = rgb_frame.shape
    if face_landmarks:
        landmarks = face_landmarks.landmark

        try:
            outer = landmarks[33]
            inner = landmarks[133]
            iris = landmarks[468]
            top = landmarks[159]
            bottom = landmarks[145]

            outer_x = outer.x * w
            inner_x = inner.x * w
            iris_x = iris.x * w
            iris_y = iris.y * h
            top_y = top.y * h
            bottom_y = bottom.y * h

            if (inner_x - outer_x == 0) or (bottom_y - top_y == 0):
                return False, lastgazetime

            gaze_ratio_x = (iris_x - outer_x) / (inner_x - outer_x)
            gaze_ratio_y = (iris_y - top_y) / (bottom_y - top_y)

            if currenttime - lastgazetime > 3:
                if gaze_ratio_x < 0.2 or gaze_ratio_x > 0.6 or gaze_ratio_y < 0.2 or gaze_ratio_y > 0.6:
                    lastgazetime = currenttime
                    return True, lastgazetime
        except IndexError:
            pass

    return False, lastgazetime




def blinking(right_eye, left_eye, last_blink_time, eye_history, cooldown=0.6):
    avg_eye = (right_eye + left_eye) / 2
    current_time = time.time()
    
    eye_history.append(avg_eye)
    
    if len(eye_history) < 5:
        threshold = 8.0  
    else:
        
        recent_avg = sum(eye_history) / len(eye_history)
        threshold = recent_avg * 0.7
    

    recent_avg = sum(eye_history) / len(eye_history)
    threshold = recent_avg * 0.7
    
    if avg_eye < threshold and (current_time - last_blink_time) > cooldown:
        print(f"Blink detected: {avg_eye:.3f} < {threshold:.3f}")
        return True, current_time
    
    return False, last_blink_time





def blinkperminute(blinkcount, lastcounttime):
    currenttime = time.time()
    timex = currenttime - lastcounttime
    if timex == 0:
        return 0, lastcounttime
    bpm = (blinkcount / timex) * 60
    lastcounttime = currenttime
    return bpm, lastcounttime
