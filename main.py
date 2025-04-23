import cv2
from webcam_utils import *

cap=cv2.VideoCapture(0)
while True:
    frame=webcamframe(cap)
    if frame is None:
        print("Frame not captured!")
        break
    webcamfeed(frame)
    if cv2.waitKey(1) & 0xFF==ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

        