import cv2
import numpy as np
import mediapipe as mp
from keras.models import load_model
from keras.preprocessing.image import img_to_array


model_path = "models/fer2013_mini_XCEPTION.102-0.66.hdf5"
emotion_model = load_model(model_path, compile=False)


EMOTION_LABELS = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']


mp_face = mp.solutions.face_detection
face_detector = mp_face.FaceDetection(model_selection=0, min_detection_confidence=0.6)

def analyze_emotions(video_path, frame_skip=15):
    cap = cv2.VideoCapture(video_path)

    emotion_counts = {label: 0 for label in EMOTION_LABELS}
    total_frames = 0
    frame_idx = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % frame_skip == 0:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_detector.process(frame_rgb)

            if results.detections:
                for detection in results.detections:
                    bboxC = detection.location_data.relative_bounding_box
                    h, w, _ = frame.shape
                    x1 = int(bboxC.xmin * w)
                    y1 = int(bboxC.ymin * h)
                    x2 = int((bboxC.xmin + bboxC.width) * w)
                    y2 = int((bboxC.ymin + bboxC.height) * h)

                    face_img = frame[y1:y2, x1:x2]
                    if face_img.size == 0:
                        continue

                    gray_face = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
                    resized_face = cv2.resize(gray_face, (64, 64))  
                    normalized = resized_face.astype("float32") / 255.0
                    face_array = np.expand_dims(normalized, axis=-1)   
                    face_array = np.expand_dims(face_array, axis=0)   


                    preds = emotion_model.predict(face_array, verbose=0)[0]
                    label = EMOTION_LABELS[np.argmax(preds)]
                    emotion_counts[label] += 1
                    total_frames += 1
                    break  

        frame_idx += 1

    cap.release()

    if total_frames > 0:
        for k in emotion_counts:
            emotion_counts[k] = round((emotion_counts[k] / total_frames) * 100, 2)

    return emotion_counts
