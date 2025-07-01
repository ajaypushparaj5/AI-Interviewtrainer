import cv2
from fer import FER

def analyze_emotions(video_path, frame_skip=15):
    detector = FER(mtcnn=True)
    cap = cv2.VideoCapture(video_path)

    emotion_counts = {
        'happy': 0,
        'sad': 0,
        'angry': 0,
        'surprise': 0,
        'neutral': 0,
        'fear': 0,
        'disgust': 0
    }

    total_frames = 0
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % frame_skip == 0:
            result = detector.top_emotion(frame)
            if result:
                emotion, _ = result
                if emotion in emotion_counts:
                    emotion_counts[emotion] += 1
            total_frames += 1

        frame_idx += 1

    cap.release()


    if total_frames > 0:
        for k in emotion_counts:
            emotion_counts[k] = round((emotion_counts[k] / total_frames) * 100, 2)

    return emotion_counts
