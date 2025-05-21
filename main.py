# import cv2
# import mediapipe as mp
# import time
# from webcam_utils import *
# from eye_contact_detector import *
# from posture_detector import * 
# from hand_gesture import *

# mp_face_mesh = mp.solutions.face_mesh
# face_mesh = mp_face_mesh.FaceMesh(
#     static_image_mode=False,
#     max_num_faces=1,
#     refine_landmarks=True,
#     min_detection_confidence=0.5,
#     min_tracking_confidence=0.5
# )


# count = 0
# lastblinktime = 0
# lastbpmtime = 0
# lastgazetime = time.time()
# lastslouch = 0
# cap = cv2.VideoCapture(0)

# while True:
#     frame = webcamframe(cap)
#     if frame is None:
#         print("Frame not captured!")
#         break

#     rgb_frame = bgr2rgb(frame)

#     face_results = face_mesh.process(rgb_frame)

#     pose_results = holistic.process(rgb_frame)
    
#     hand_results = hands.process(rgb_frame)

#     if face_results.multi_face_landmarks:
#         frame = display_facial_landmarks(frame, face_results)

#     if pose_results.pose_landmarks:
#         frame = display_pose(frame, pose_results)
        
#     if hand_results.multi_hand_landmarks:
#         frame = display_hand(frame)

#     webcamfeed(frame)

#     slouch, lastslouch = slouch_detector(frame, pose_results, lastslouch)
#     if slouch:
#         print("Sit Straight!")

#     if face_results.multi_face_landmarks:
#         face_landmarks = face_results.multi_face_landmarks[0]
#         righteyedist = get_eye_distance(frame, face_landmarks, 159, 145)
#         lefteyedist = get_eye_distance(frame, face_landmarks, 386, 374)
#         blinkcheck, lastblinktime = blinking(righteyedist, lefteyedist, lastblinktime)
#         gazeoff, lastgazetime = gaze_detector(frame, face_landmarks, lastgazetime)

#         if gazeoff:
#             print("\nDon't look away!")
#         if blinkcheck:
#             count += 1
#             print("Blink Detected: Yes")

#     currenttime = time.time()
#     if currenttime - lastbpmtime >= 10:
#         bpm, lastbpmtime = blinkperminute(count, lastbpmtime)
#         print("\nBPM:", bpm)
#         count = 0

#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()

# import cv2
# import mediapipe as mp
# import time
# from webcam_utils import *
# from eye_contact_detector import *
# from posture_detector import *
# from hand_gesture import *

# mp_holistic = mp.solutions.holistic
# holistic = mp_holistic.Holistic(
#     static_image_mode=False,
#     model_complexity=1,
#     smooth_landmarks=True,
#     refine_face_landmarks=True,
#     min_detection_confidence=0.5,
#     min_tracking_confidence=0.5
# )

# count = 0
# lastblinktime = 0
# lastbpmtime = 0
# lastgazetime = time.time()
# lastslouch = 0

# cap = cv2.VideoCapture(0)

# while True:
#     frame = webcamframe(cap)
#     if frame is None:
#         print("Frame not captured!")
#         break

#     rgb_frame = bgr2rgb(frame)


#     results = holistic.process(rgb_frame)


#     if results.face_landmarks:
#         frame = display_facial_landmarks(frame, results.face_landmarks)

#     if results.pose_landmarks:
#         frame = display_pose(frame, results.pose_landmarks)


#     if results.left_hand_landmarks:
#         frame = display_hand(frame, results.left_hand_landmarks)
#     if results.right_hand_landmarks:
#         frame = display_hand(frame, results.right_hand_landmarks)

#     webcamfeed(frame)


#     slouch, lastslouch = slouch_detector(frame, results.pose_landmarks, lastslouch)
#     if slouch:
#         print("Sit Straight!")


#     if results.face_landmarks:
#         face_landmarks = results.face_landmarks
#         righteyedist = get_eye_distance(frame, face_landmarks, 159, 145)
#         lefteyedist = get_eye_distance(frame, face_landmarks, 386, 374)
#         blinkcheck, lastblinktime = blinking(righteyedist, lefteyedist, lastblinktime)
#         gazeoff, lastgazetime = gaze_detector(frame, face_landmarks, lastgazetime)

#         if gazeoff:
#             print("\nDon't look away!")
#         if blinkcheck:
#             count += 1
#             print("Blink Detected: Yes")
#     currenttime = time.time()
#     if currenttime - lastbpmtime >= 10:
#         bpm, lastbpmtime = blinkperminute(count, lastbpmtime)
#         print("\nBPM:", bpm)
#         count = 0

#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()


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

        if gazeoff:
            print("\nDon't look away!")
        if blinkcheck:
            count += 1
            print("Blink Detected: Yes")

    currenttime = time.time()
    if currenttime - lastbpmtime >= 10:
        bpm, lastbpmtime = blinkperminute(count, lastbpmtime)
        print("\nBPM:", bpm)
        count = 0

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
