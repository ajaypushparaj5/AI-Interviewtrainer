import mediapipe as mp
import cv2
import time

def display_legs(frame,pose_landmarks):
    if not pose_landmarks:
        return frame

    h, w, _ = frame.shape
    lm = pose_landmarks.landmark

    leg_parts = [(23,25,27,31), (24,26,28,32)] 
    
    for hip_id,knee_id, ankle_id, foot_id in leg_parts:
        hip = lm[hip_id]
        knee = lm[knee_id]
        ankle = lm[ankle_id]
        foot = lm[foot_id]

        hip_x, hip_y = int(hip.x * w), int(hip.y * h)
        knee_x, knee_y = int(knee.x * w), int(knee.y * h)
        ankle_x, ankle_y = int(ankle.x * w), int(ankle.y * h)
        foot_x, foot_y = int(foot.x * w), int(foot.y * h)

        cv2.circle(frame, (hip_x, hip_y), 8, (0, 255, 0), -1)
        cv2.circle(frame, (knee_x, knee_y), 8, (0, 255, 0), -1)
        cv2.circle(frame, (ankle_x, ankle_y), 8, (0, 255, 0), -1)
        cv2.circle(frame, (foot_x, foot_y), 8, (0, 255, 0), -1)

        cv2.line(frame, (hip_x, hip_y), (knee_x, knee_y), (255, 0, 0), 2)
        cv2.line(frame, (knee_x, knee_y), (ankle_x, ankle_y), (255, 0, 0), 2)
        cv2.line(frame, (ankle_x, ankle_y), (foot_x, foot_y), (255, 0, 0), 2)
    return frame


def detect_crossed_legs(pose_landmarks,last_crossed_time):
    current_time = time.time()
    if not pose_landmarks:
        return False, last_crossed_time

    lm = pose_landmarks.landmark
    left_ankle = lm[27]
    right_ankle = lm[28]

    x_close= abs(left_ankle.x - right_ankle.x) < 0.05
    y_close = abs(left_ankle.y - right_ankle.y) < 0.05
    if x_close and y_close:
        if current_time - last_crossed_time > 3:
            last_crossed_time = current_time
            return True, current_time
    return False, last_crossed_time

def detect_leg_bouncing(pose_landmarks, last_bounce_time, threshold=0.05, cooldown=0.5):
    current_time = time.time()
    if not pose_landmarks:
        return False, last_bounce_time

    lm = pose_landmarks.landmark
    left_ankle = lm[27]
    right_ankle = lm[28]

    left_y = left_ankle.y
    right_y = right_ankle.y

    if abs(left_y - right_y) > threshold:
        if current_time - last_bounce_time > cooldown:
            last_bounce_time = current_time
            return True, last_bounce_time

    return False, last_bounce_time

def detect_hands_on_hip(pose_landmarks, last_hands_on_hip_time, threshold=0.1, cooldown=0.5):
    current_time = time.time()
    if not pose_landmarks:
        return False, last_hands_on_hip_time

    lm = pose_landmarks.landmark
    left_wrist = lm[15]
    right_wrist = lm[16]
    left_hip = lm[23]
    right_hip = lm[24]
    
    left_distance = ((left_wrist.x - left_hip.x) ** 2 + (left_wrist.y - left_hip.y) ** 2) ** 0.5
    right_distance = ((right_wrist.x - right_hip.x) ** 2 + (right_wrist.y - right_hip.y) ** 2) ** 0.5
    
    left_on_hip = left_distance < threshold
    right_on_hip = right_distance < threshold
    
    if left_on_hip or right_on_hip:
        if current_time - last_hands_on_hip_time > cooldown:
            last_hands_on_hip_time = current_time
            return True, last_hands_on_hip_time
    return False, last_hands_on_hip_time

