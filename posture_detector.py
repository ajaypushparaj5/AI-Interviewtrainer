
import cv2
import mediapipe as mp
import time

# def display_pose(rgb_frame, results):
#     if results:
#         landmarks = results.landmark
#         h, w, _ = rgb_frame.shape

#         left_shoulder = landmarks[11]  
#         right_shoulder = landmarks[12]  

#         lx, ly = int(left_shoulder.x * w), int(left_shoulder.y * h)
#         rx, ry = int(right_shoulder.x * w), int(right_shoulder.y * h)

#         cv2.circle(rgb_frame, (lx, ly), 8, (255, 0, 0), -1)
#         cv2.circle(rgb_frame, (rx, ry), 8, (255, 0, 0), -1)
#         cv2.line(rgb_frame, (lx, ly), (rx, ry), (0, 255, 0), 2)

#     return rgb_frame

def display_pose(rgb_frame, results):
    if not results or not results.landmark:
        return rgb_frame

    h, w, _ = rgb_frame.shape
    lm = results.landmark

    lx, ly = int(lm[11].x * w), int(lm[11].y * h)
    rx, ry = int(lm[12].x * w), int(lm[12].y * h)

    cv2.circle(rgb_frame, (lx, ly), 8, (255, 0, 0), -1)
    cv2.circle(rgb_frame, (rx, ry), 8, (255, 0, 0), -1)
    cv2.line(rgb_frame, (lx, ly), (rx, ry), (0, 255, 0), 2)

    ls = lm[11]
    rs = lm[12]
    lh = lm[23]
    rh = lm[24]
    
    x1 = int((min(ls.x, rs.x) + 0.05) * w)
    x2 = int((max(ls.x, rs.x) - 0.05) * w)
    y1 = int(min(ls.y, rs.y) * h) + 10
    y2 = int(max(lh.y, rh.y) * h) - 10

    cv2.rectangle(rgb_frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

    return rgb_frame



def slouch_detector(rgb_frame, results, lastslouch):
    if not results:
        return False, lastslouch

    h, _, _ = rgb_frame.shape
    landmarks = results.landmark

    left_shoulder = landmarks[11]
    right_shoulder = landmarks[12]

    ly = int(left_shoulder.y * h)
    ry = int(right_shoulder.y * h)

    current = time.time()


    if current - lastslouch >= 4:
        if abs(ly - ry) > 20:  
            lastslouch = current
            return True, lastslouch

    return False, lastslouch


def arms_crossed_detector(results, last_arms_crossed_time, threshold=0.15):
    if not results:
        return False, last_arms_crossed_time
    current_time = time.time()
    landmarks = results.landmark

    left_wrist = landmarks[15]
    right_wrist = landmarks[16]
    left_shoulder = landmarks[11]
    right_shoulder = landmarks[12]

    # Condition: wrists are near opposite shoulders (in x-direction)
    left_wrist_near_right_shoulder = abs(left_wrist.x - right_shoulder.x) < threshold
    right_wrist_near_left_shoulder = abs(right_wrist.x - left_shoulder.x) < threshold

    if left_wrist_near_right_shoulder and right_wrist_near_left_shoulder:
        if current_time - last_arms_crossed_time > 3:
            last_arms_crossed_time = current_time
            return True, last_arms_crossed_time
    return False, last_arms_crossed_time
    



def check_hand_in_restricted_zone(frame, pose_landmarks, hand_landmarks, log):
    if pose_landmarks is None or hand_landmarks is None:
        return False        

    h, w, _ = frame.shape
    lm = pose_landmarks.landmark

    left_shoulder = lm[11]
    right_shoulder = lm[12]
    left_hip = lm[23]
    right_hip = lm[24]

    x_min = int((min(left_shoulder.x, right_shoulder.x) + 0.05) * w)
    x_max = int((max(left_shoulder.x, right_shoulder.x) - 0.05) * w)
    y_min = int(min(left_shoulder.y, right_shoulder.y) * h) + 10
    y_max = int(max(left_hip.y, right_hip.y) * h) - 10

    cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 0, 255), 2)

    for lm in hand_landmarks.landmark:
        x = int(lm.x * w)
        y = int(lm.y * h)
        if x_min <= x <= x_max and y_min <= y <= y_max:
            return True
    return False

    
def is_hand_outside_safezone(frame, pose_landmarks, hand_landmarks, log=None):
    if pose_landmarks is None or hand_landmarks is None:
        return False

    h, w, _ = frame.shape
    landmarks = pose_landmarks.landmark

    left_shoulder = landmarks[11]
    right_shoulder = landmarks[12]
    left_hip = landmarks[23]
    right_hip = landmarks[24]

    top_y = int(min(left_shoulder.y, right_shoulder.y) * h)
    bottom_y = int(max(left_hip.y, right_hip.y) * h)
    center_x = int((left_shoulder.x + right_shoulder.x) / 2 * w)
    box_width = int(abs(right_shoulder.x - left_shoulder.x) * w * 1.2)

    left_x = center_x - box_width // 2
    right_x = center_x + box_width // 2

    fingertip_indices = [4, 8, 12, 16, 20]
    out_count = 0
    for idx in fingertip_indices:
        x = int(hand_landmarks.landmark[idx].x * w)
        y = int(hand_landmarks.landmark[idx].y * h)
        if not (left_x <= x <= right_x and top_y <= y <= bottom_y):
            out_count += 1

    if out_count >= 3:
        if log:
            log("[WARNING] Hand moved outside safe zone!")
        return True

    return False
