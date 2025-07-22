import mediapipe as mp
import cv2
import time
import math
from collections import deque

def display_legs(frame, pose_landmarks):
    """Display leg landmarks and connections"""
    if not pose_landmarks:
        return frame

    h, w, _ = frame.shape
    lm = pose_landmarks.landmark

    # Left leg: hip(23), knee(25), ankle(27), foot(31)
    # Right leg: hip(24), knee(26), ankle(28), foot(32)
    leg_parts = [(23, 25, 27, 31), (24, 26, 28, 32)] 
    colors = [(0, 255, 0), (0, 255, 255)]  # Green for left, Yellow for right
    
    for i, (hip_id, knee_id, ankle_id, foot_id) in enumerate(leg_parts):
        hip = lm[hip_id]
        knee = lm[knee_id]
        ankle = lm[ankle_id]
        foot = lm[foot_id]

        hip_x, hip_y = int(hip.x * w), int(hip.y * h)
        knee_x, knee_y = int(knee.x * w), int(knee.y * h)
        ankle_x, ankle_y = int(ankle.x * w), int(ankle.y * h)
        foot_x, foot_y = int(foot.x * w), int(foot.y * h)

        # Draw circles for joints
        cv2.circle(frame, (hip_x, hip_y), 8, colors[i], -1)
        cv2.circle(frame, (knee_x, knee_y), 8, colors[i], -1)
        cv2.circle(frame, (ankle_x, ankle_y), 8, colors[i], -1)
        cv2.circle(frame, (foot_x, foot_y), 8, colors[i], -1)

        # Draw leg connections
        cv2.line(frame, (hip_x, hip_y), (knee_x, knee_y), (255, 0, 0), 3)
        cv2.line(frame, (knee_x, knee_y), (ankle_x, ankle_y), (255, 0, 0), 3)
        cv2.line(frame, (ankle_x, ankle_y), (foot_x, foot_y), (255, 0, 0), 3)
    
    # Draw body center line for reference
    if len(lm) > 24:
        left_hip = lm[23]
        right_hip = lm[24]
        hip_center_x = int((left_hip.x + right_hip.x) / 2 * w)
        cv2.line(frame, (hip_center_x, 0), (hip_center_x, h), (255, 255, 255), 2)
        
    return frame


def detect_crossed_legs(pose_landmarks, lastlegcross, duration_threshold=3.0):

    current_time = time.time()
    
    if not pose_landmarks:
        return False, lastlegcross

    lm = pose_landmarks.landmark
    
    left_hip = lm[23]
    right_hip = lm[24]
    left_knee = lm[25]
    right_knee = lm[26]
    left_ankle = lm[27]
    right_ankle = lm[28]
    
    hip_center_x = (left_hip.x + right_hip.x) / 2
    
    left_knee_crosses = left_knee.x > hip_center_x
    right_knee_crosses = right_knee.x < hip_center_x
    
    ankle_distance = abs(left_ankle.x - right_ankle.x)
    ankles_close = 0.03 < ankle_distance < 0.15
    
    knee_height_diff = abs(left_knee.y - right_knee.y)
    different_heights = knee_height_diff > 0.03
    
    left_ankle_crosses_center = left_ankle.x < hip_center_x
    right_ankle_crosses_center = right_ankle.x > hip_center_x
    ankles_cross_center = left_ankle_crosses_center or right_ankle_crosses_center
    
    
    currently_crossed = ((left_knee_crosses or right_knee_crosses) and different_heights and ankles_cross_center)
    
    if currently_crossed:
        if current_time - lastlegcross > duration_threshold:
            lastlegcross = current_time
            return True, lastlegcross
    return False, lastlegcross


# def detect_leg_bouncing(pose_landmarks, last_bounce_time, threshold=0.05, cooldown=0.5):
#     current_time = time.time()
#     if not pose_landmarks:
#         return False, last_bounce_time

#     lm = pose_landmarks.landmark
#     left_ankle = lm[27]
#     right_ankle = lm[28]

#     left_y = left_ankle.y
#     right_y = right_ankle.y

#     if abs(left_y - right_y) > threshold:
#         if current_time - last_bounce_time > cooldown:
#             last_bounce_time = current_time
#             return True, last_bounce_time

#     return False, last_bounce_time


# def detect_leg_motion(pose_landmarks, last_motion_time, threshold=0.3, cooldown=0.3, min_visibility=0.5):
#     """
#     Simplified version focusing on key relative motion indicators.
#     """
#     current_time = time.time()
    
#     if not pose_landmarks:
#         return False, last_motion_time
    
#     lm = pose_landmarks.landmark
    
#     # Get key landmarks
#     left_knee = lm[25]
#     right_knee = lm[26]
#     left_ankle = lm[27]
#     right_ankle = lm[28]
    
#     # Check visibility of essential landmarks
#     essential_landmarks = [left_knee, right_knee, left_ankle, right_ankle]
#     for landmark in essential_landmarks:
#         if landmark.visibility < min_visibility:
#             return False, last_motion_time
    
#     # Simple relative motion indicators
#     # 1. Asymmetric knee heights (bouncing/fidgeting)
#     knee_height_diff = abs(left_knee.y - right_knee.y)> threshold
    
#     # 2. Asymmetric ankle heights
#     ankle_height_diff = abs(left_ankle.y - right_ankle.y)> threshold
    
#     # 3. Leg positioning asymmetry (one leg forward/back)
#     knee_horizontal_diff = abs(left_knee.x - right_knee.x)
#     ankle_horizontal_diff = abs(left_ankle.x - right_ankle.x)
#     horizontal_asymmetry = abs(knee_horizontal_diff - ankle_horizontal_diff)
    
#     # Combine indicators
#     total_motion = knee_height_diff or ankle_height_diff or horizontal_asymmetry
    
#     # Check if motion exceeds threshold
#     motion_detected = False
#     if total_motion and (current_time - last_motion_time) > cooldown:
#         motion_detected = True
#         last_motion_time = current_time
    
#     return motion_detected, last_motion_time

def detect_leg_motion(pose_landmarks, motion_history, threshold=0.03):
    """
    Simplified version focusing only on basic horizontal leg swaying.
    """
    current_time = time.time()
    
    if not pose_landmarks:
        return False, motion_history
    
    lm = pose_landmarks.landmark
    
    # Get knee positions (simpler approach)
    left_knee = lm[25]
    right_knee = lm[26]
    
    if left_knee.visibility < 0.5 or right_knee.visibility < 0.5:
        return False, motion_history
    
    # Initialize if needed
    if 'knee_positions' not in motion_history:
        motion_history['knee_positions'] = deque(maxlen=6)
        motion_history['last_sway'] = 0
    
    # Store knee separation distance
    knee_distance = abs(left_knee.x - right_knee.x)
    motion_history['knee_positions'].append(knee_distance)
    
    if len(motion_history['knee_positions']) < 4:
        return False, motion_history
    
    # Check for oscillating knee distance (legs swaying in/out)
    positions = list(motion_history['knee_positions'])
    direction_changes = 0
    
    for i in range(1, len(positions) - 1):
        if (positions[i] - positions[i-1]) * (positions[i+1] - positions[i]) < 0:
            direction_changes += 1
    
    # Check movement magnitude
    movement_range = max(positions) - min(positions)
    
    sway_detected = direction_changes >= 2 and movement_range > threshold
    
    if sway_detected and (current_time - motion_history['last_sway']) > 3:
        motion_history['last_sway'] = current_time
        return True, motion_history
    
    return False, motion_history



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

