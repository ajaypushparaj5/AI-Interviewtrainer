# import mediapipe as mp
# import time

# mp_hand=mp.solutions.hands
# mp_drawing = mp.solutions.drawing_utils
# hands = mp_hand.Hands(
#     static_image_mode=False,
#     max_num_hands=2,
#     min_detection_confidence=0.5,
#     min_tracking_confidence=0.5
# )

# def display_hand(rgb_frame):
#     results=hands.process(rgb_frame)
#     if results.multi_hand_landmarks:
#         for hand_landmarks in results.multi_hand_landmarks:
#             mp_drawing.draw_landmarks(
#                 image=rgb_frame,
#                 landmark_list=hand_landmarks,
#                 connections=mp_hand.HAND_CONNECTIONS
#             )
#     return rgb_frame

import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

def display_hand(rgb_frame, hand_landmarks):
    mp_drawing.draw_landmarks(
        image=rgb_frame,
        landmark_list=hand_landmarks,
        connections=mp_hands.HAND_CONNECTIONS
    )
    return rgb_frame
