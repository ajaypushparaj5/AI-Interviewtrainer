import cv2
from webcam_utils import *
from eye_contact_detector import *
from posture_detector import *
import time
# from feedback_gui import FeedbackGUI
# gui = FeedbackGUI()
# gui.start()
count=0
lastblinktime=0
lastbpmtime=0
lastgazetime=time.time()
lastslouch=0
cap=cv2.VideoCapture(0)
while True:
    frame=webcamframe(cap)
    rgbframe=bgr2rgb(frame)
    results = face_mesh.process(rgbframe)
    results2= pose.process(rgbframe)
    frame=display_facial_landmarks(rgbframe)
    frame=display_pose(rgbframe)
    if frame is None:
        print("Frame not captured!")
        break
    webcamfeed(frame)
    slouch,lastslouch=slouch_detector(rgbframe,results2,lastslouch)
    if slouch==True:
        print("Sit Straight! ")
    # righteyedist=get_eye_distance(rgbframe,results,159,145)
    # lefteyedist=get_eye_distance(rgbframe,results,386,374)
    # blinkcheck,lastblinktime=blinking(righteyedist,lefteyedist,lastblinktime)
    # gazeoff,lastgazetime=gaze_detector(rgbframe,results,lastgazetime)
    # if(gazeoff==True):
    #     print("/nDont look away!")    
    # if blinkcheck==True:
    #     count+=1
    #     print("Blink Detected: Yes")
    # currenttime=time.time()
    # if currenttime-lastbpmtime>=10:
    #     bpm,lastbpmtime=blinkperminute(count,lastbpmtime)
    #     print("\nBPM:",bpm)
    #     count=0
    if cv2.waitKey(1) & 0xFF==ord('q'):
        break
# gui.stop()
cap.release()
cv2.destroyAllWindows()

        