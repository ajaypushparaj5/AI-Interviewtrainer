import cv2
import numpy as np

def webcamframe(cap):
    ret,frame=cap.read()
    if not ret:
        print("Issue in Frames \n")
        return None
    else:
        return cv2.flip(frame,1)
    
def webcamfeed(frame):
    cv2.imshow("Webcam LiveFeed",frame)
    
    
def bgr2rgb(frame):
    rgbframe=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
    return rgbframe