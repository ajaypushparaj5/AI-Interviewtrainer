import cv2
import mediapipe as mp
import time
from webcam_utils import *
from eye_contact_detector import *
from posture_detector import *  # your posture detector with holistic initialized inside

# Initialize face_mesh separately (for face landmarks + iris)
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# holistic is already initialized inside posture_detector.py, 
# you can either import it or initialize here again if needed.

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

    # Process face mesh (face landmarks)
    face_results = face_mesh.process(rgb_frame)

    # Process pose with holistic inside posture_detector
    pose_results = holistic.process(rgb_frame)

    # Draw face landmarks if detected
    if face_results.multi_face_landmarks:
        frame = display_facial_landmarks(frame, face_results)

    # Draw pose landmarks if detected
    if pose_results.pose_landmarks:
        frame = display_pose(frame, pose_results)

    webcamfeed(frame)

    # Slouch detection using pose_results from holistic
    slouch, lastslouch = slouch_detector(frame, pose_results, lastslouch)
    if slouch:
        print("Sit Straight!")

    # Use face landmarks for eye distance, blinking, gaze detection
    if face_results.multi_face_landmarks:
        face_landmarks = face_results.multi_face_landmarks[0]
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
