import cv2
import numpy as np
import mediapipe as mp

mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

def display_facial_landmarks(rgb_frame):
    
    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            iris_indices = [468, 469, 470, 471, 472, 473, 474, 475, 476, 477]
            h, w, _ = rgb_frame.shape
            for idx in iris_indices:
                pt = face_landmarks.landmark[idx]

                x, y = int(pt.x * w), int(pt.y * h)
                cv2.circle(rgb_frame, (x, y), 2, (255, 0, 0), -1)

            mp_drawing.draw_landmarks(
                image=rgb_frame,
                landmark_list=face_landmarks,
                connections=mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=mp_drawing.DrawingSpec(
                    color=(0, 255, 0), thickness=1, circle_radius=1
                )
            )
    return rgb_frame
