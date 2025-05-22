import math
import mediapipe as mp
import time

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

def display_hand(rgb_frame, hand_landmarks):
    mp_drawing.draw_landmarks(
        image=rgb_frame,
        landmark_list=hand_landmarks,
        connections=mp_hands.HAND_CONNECTIONS
    )
    return rgb_frame

def distance(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

def hand_mouth_contact(rgb_frame, face_landmarks, hand_landmarks, threshold=40):
    h, w, _ = rgb_frame.shape

    mouth_indices = [61, 146, 91, 181, 84, 17, 314, 405, 321, 375,
                     291, 308, 324, 318, 402, 317, 14, 87, 178, 88]
    mouth_points = [(int(face_landmarks.landmark[i].x * w),
                     int(face_landmarks.landmark[i].y * h)) for i in mouth_indices]

    mouth_x = sum(p[0] for p in mouth_points) // len(mouth_points)
    mouth_y = sum(p[1] for p in mouth_points) // len(mouth_points)
    mouth_center = (mouth_x, mouth_y)

    fingertip_indices = [4, 8, 12, 16, 20]

    for idx in fingertip_indices:
        x = int(hand_landmarks.landmark[idx].x * w)
        y = int(hand_landmarks.landmark[idx].y * h)
        if distance((x, y), mouth_center) < threshold:
            return True
    return False

def update_touch_state(rgb_frame, face_landmarks, hand_landmarks,
                       last_check_time, touch_start_time, touch_count,
                       contact_func, hold_time=1, check_interval=2):
    current_time = time.time()

    if last_check_time is None:
        last_check_time = current_time
        return False, last_check_time, touch_start_time, touch_count

    if current_time - last_check_time < check_interval:
        return False, last_check_time, touch_start_time, touch_count

    last_check_time = current_time
    touching = contact_func(rgb_frame, face_landmarks, hand_landmarks)

    if touching:
        if touch_start_time is None:
            touch_start_time = current_time
        elif current_time - touch_start_time >= hold_time:
            touch_count += 1
            touch_start_time = None
            return True, last_check_time, touch_start_time, touch_count
    else:
        touch_start_time = None

    return False, last_check_time, touch_start_time, touch_count



def hand_nose_contact(rgb_frame, face_landmarks, hand_landmarks, threshold=40):
    if face_landmarks is None or hand_landmarks is None:
        return False

    h, w, _ = rgb_frame.shape
    nose = face_landmarks.landmark[1]
    nose_point = (int(nose.x * w), int(nose.y * h))

    fingertip_indices = [4, 8, 12, 16, 20]
    for idx in fingertip_indices:
        x = int(hand_landmarks.landmark[idx].x * w)
        y = int(hand_landmarks.landmark[idx].y * h)
        if distance((x, y), nose_point) < threshold:
            return True
    return False


def hand_eye_contact(rgb_frame, face_landmarks, hand_landmarks, threshold=35):
    if face_landmarks is None or hand_landmarks is None:
        return False

    h, w, _ = rgb_frame.shape

    right_eye = face_landmarks.landmark[33]
    left_eye = face_landmarks.landmark[263]

    right_eye_point = (int(right_eye.x * w), int(right_eye.y * h))
    left_eye_point = (int(left_eye.x * w), int(left_eye.y * h))

    fingertip_indices = [4, 8, 12, 16, 20]
    for idx in fingertip_indices:
        x = int(hand_landmarks.landmark[idx].x * w)
        y = int(hand_landmarks.landmark[idx].y * h)
        if distance((x, y), right_eye_point) < threshold or distance((x, y), left_eye_point) < threshold:
            return True
    return False

