import cv2
import numpy as np
import mediapipe as mp
import time

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


def get_eye_distance(rgb_frame,results,top,bottom):
    h, w, _ = rgb_frame.shape
    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            top=face_landmarks.landmark[top]
            bottom=face_landmarks.landmark[bottom]
            topy=int(top.y*h)
            bottomy=int(bottom.y*h)
            return abs(topy-bottomy)
    return 0

def blinking(right,left,lastblinktime,cooldown=0.15):
    currenttime=time.time()
    
    if right<4 and left<4:
        if currenttime-lastblinktime>cooldown:
            lastblinktime=currenttime
            return True,lastblinktime
    return False,lastblinktime

def blinkperminute(blinkcount,lastcounttime):
    currenttime=time.time()
    timex=currenttime-lastcounttime
    if timex==0:
        return 0,lastcounttime
    bpm=(blinkcount/timex)*60
    lastcounttime=currenttime
    return bpm,lastcounttime
        
def gaze_detector(rgb_frame,results,lastgazetime):
    currenttime=time.time()
    h,w,_=rgb_frame.shape
    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            outer=face_landmarks.landmark[33]
            inner=face_landmarks.landmark[133]
            iris=face_landmarks.landmark[468]
            outer_x=outer.x*w
            inner_x=inner.x*w
            iris_x=iris.x*w
            top = face_landmarks.landmark[159]
            bottom = face_landmarks.landmark[145]
            iris_y = iris.y * h
            top_y = top.y * h
            bottom_y = bottom.y * h
            if(inner_x-outer_x==0 or bottom_y-top_y == 0):
                return False,lastgazetime
            gaze_ratio=(iris_x-outer_x)/(inner_x-outer_x)
            gaze_ratio_y=(iris_y-top_y)/(bottom_y-top_y)
            if currenttime-lastgazetime>3:
                if gaze_ratio<0.2 or gaze_ratio>0.6 or gaze_ratio_y<0.2 or gaze_ratio_y>0.6:
                    lastgazetime=currenttime
                    return True,lastgazetime
                
    return False,lastgazetime
    
    
