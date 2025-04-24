import cv2
from webcam_utils import *
from eye_contact_detector import *
count=0
lastblinktime=0
cap=cv2.VideoCapture(0)
while True:
    frame=webcamframe(cap)
    rgbframe=bgr2rgb(frame)
    results = face_mesh.process(rgbframe)
    frame=display_facial_landmarks(rgbframe)
    if frame is None:
        print("Frame not captured!")
        break
    webcamfeed(frame)
    righteyedist=get_eye_distance(rgbframe,results,159,145)
    lefteyedist=get_eye_distance(rgbframe,results,386,374)
    blinkcheck,lastblinktime=blinking(righteyedist,lefteyedist,lastblinktime)
    if blinkcheck==True:
        count+=1
        print("\n",count)
           
    if cv2.waitKey(1) & 0xFF==ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

        