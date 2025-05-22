

import cv2
import mediapipe as mp
import time
from webcam_utils import *
from eye_contact_detector import *
from posture_detector import *
from hand_gesture import *

mp_holistic = mp.solutions.holistic
holistic = mp_holistic.Holistic(
    static_image_mode=False,
    model_complexity=1,
    smooth_landmarks=True,
    refine_face_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

count = 0
lastblinktime = 0
lastbpmtime = 0
lastgazetime = time.time()
lastslouch = 0
last_check_time = 0
touch_start_time = None
touch_count = 0


cap = cv2.VideoCapture(0)

while True:
    frame = webcamframe(cap)
    if frame is None:
        print("Frame not captured!")
        break

    rgb_frame = bgr2rgb(frame)
    results = holistic.process(rgb_frame)

    if results.face_landmarks:
        frame = display_facial_landmarks(frame, results.face_landmarks)

    if results.pose_landmarks:
        frame = display_pose(frame, results.pose_landmarks)

    if results.left_hand_landmarks:
        frame = display_hand(frame, results.left_hand_landmarks)
    if results.right_hand_landmarks:
        frame = display_hand(frame, results.right_hand_landmarks)

    webcamfeed(frame)


    slouch, lastslouch = slouch_detector(frame, results.pose_landmarks, lastslouch)
    if slouch:
        print("Sit Straight!")


    if results.face_landmarks:
        face_landmarks = results.face_landmarks
        righteyedist = get_eye_distance(frame, face_landmarks, 159, 145)
        lefteyedist = get_eye_distance(frame, face_landmarks, 386, 374)

        blinkcheck, lastblinktime = blinking(righteyedist, lefteyedist, lastblinktime)
        gazeoff, lastgazetime = gaze_detector(frame, face_landmarks, lastgazetime)
        hand_landmarks = None
        if results.left_hand_landmarks:
            hand_landmarks = results.left_hand_landmarks
        elif results.right_hand_landmarks:
            hand_landmarks = results.right_hand_landmarks

        if gazeoff:
            print("\nDon't look away!")
        if blinkcheck:
            count += 1
            print("Blink Detected: Yes")
        if hand_landmarks is not None:    
            touchedmouth, last_check_time, touch_start_time, mouthtouch_count = update_touch_state(frame, face_landmarks, hand_landmarks,last_check_time, touch_start_time, touch_count,contact_func=hand_mouth_contact)
            touchednose, last_check_time, touch_start_time, nosetouch_count = update_touch_state(frame, face_landmarks, hand_landmarks,last_check_time, touch_start_time, touch_count,contact_func=hand_nose_contact)
            touchedeye, last_check_time, touch_start_time, eyetouch_count = update_touch_state(frame, face_landmarks, hand_landmarks,last_check_time, touch_start_time, touch_count,contact_func=hand_eye_contact)

            if touchedmouth:
                print("Hand touched mouth! Count:", mouthtouch_count)
            if touchednose:
                print("Hand touched nose! Count:", nosetouch_count)
            if touchedeye:
                print("Hand touched eye! Count:", eyetouch_count)

    currenttime = time.time()
    if currenttime - lastbpmtime >= 10:
        bpm, lastbpmtime = blinkperminute(count, lastbpmtime)
        print("\nBPM:", bpm)
        count = 0

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
