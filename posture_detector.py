import cv2
import mediapipe as mp
import time

mp_pose=mp.solutions.pose
pose=mp_pose.Pose()

def display_pose(rgb_frame):
    results=pose.process(rgb_frame)
    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark
        h, w, _ = rgb_frame.shape
        left_shoulder = landmarks[11]
        right_shoulder = landmarks[12]
        lx, ly = int(left_shoulder.x * w), int(left_shoulder.y * h)
        rx, ry = int(right_shoulder.x * w), int(right_shoulder.y * h)
        cv2.circle(rgb_frame, (lx, ly), 8, (255, 0, 0), -1)
        cv2.circle(rgb_frame, (rx, ry), 8, (255, 0, 0), -1)
        cv2.line(rgb_frame, (lx, ly), (rx, ry), (0, 255, 0), 2)
    return rgb_frame

def slouch_detector(rgb_frame,results,lastslouch):
    h,_,_=rgb_frame.shape
    left=results.pose_landmarks.landmark[11]
    right=results.pose_landmarks.landmark[12]
    ly=int(left.y*h)
    ry=int(right.y*h)
    current=time.time()
    if (current-lastslouch>=4):
        if abs(ly-ry)>20:
            lastslouch=current
            return True,lastslouch
    return False,lastslouch