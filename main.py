# from webcam_utils import *
# from eye_contact_detector import *
# from posture_detector import *
# from hand_gesture import *

# def run_detection_session(video_path, log=print):
#     cap = cv2.VideoCapture(video_path)
#     return run_analysis(cap, log)

# def run_live_session(log=print):
#     cap = cv2.VideoCapture(0)
#     return run_analysis(cap, log)

# def run_analysis(cap, log=print):
#     import cv2
#     import mediapipe as mp
#     import time
#     start_time = time.time()


#     mp_holistic = mp.solutions.holistic
#     holistic = mp_holistic.Holistic(
#         static_image_mode=False,
#         model_complexity=1,
#         smooth_landmarks=True,
#         refine_face_landmarks=True,
#         min_detection_confidence=0.5,
#         min_tracking_confidence=0.5
#     )


#     avgbpm = avgcount = count = eyecount = 0
#     lastblinktime = lastbpmtime = time.time()
#     lastgazetime = time.time()
#     lastslouch = 0
#     hand_violation_logged = False
#     arms_crossed_start = None
#     arms_crossed_printed = False
#     mouth_last_check = nose_last_check = eye_last_check = ear_last_check = neck_last_check = None
#     mouth_start_time = nose_start_time = eye_start_time = ear_start_time = neck_start_time = None
#     mouthtouch_count = nosetouch_count = eyetouch_count = eartouch_count = necktouch_count = 0
    
#     cv2.namedWindow("Live Feedback", cv2.WINDOW_NORMAL)
#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret:
#             log("[ERROR] Couldn't read frame from video.")
#             break

#         rgb_frame = bgr2rgb(frame)
#         results = holistic.process(rgb_frame)

#         if results.face_landmarks:
#             frame = display_facial_landmarks(frame, results.face_landmarks)
#         if results.pose_landmarks:
#             frame = display_pose(frame, results.pose_landmarks)
#         if results.left_hand_landmarks:
#             frame = display_hand(frame, results.left_hand_landmarks)
#         if results.right_hand_landmarks:
#             frame = display_hand(frame, results.right_hand_landmarks)

#         if results.pose_landmarks:
#             slouch, lastslouch = slouch_detector(frame, results.pose_landmarks, lastslouch)
#             if slouch:
#                 log("Sit Straight!")

#             arms_crossed = arms_crossed_detector(results.pose_landmarks)
#             if arms_crossed:
#                 if arms_crossed_start is None:
#                     arms_crossed_start = time.time()
#                 elif not arms_crossed_printed and time.time() - arms_crossed_start >= 5:
#                     log("Arms crossed for 5+ seconds!")
#                     arms_crossed_printed = True
#             else:
#                 arms_crossed_start = None
#                 arms_crossed_printed = False

#             for hand in [results.left_hand_landmarks, results.right_hand_landmarks]:
#                 if hand and check_hand_in_restricted_zone(frame, results.pose_landmarks, hand, log):
#                     if not hand_violation_logged:
#                         log("⚠️ Hand entered restricted zone!")
#                         hand_violation_logged = True


#         if results.face_landmarks:
#             face_landmarks = results.face_landmarks
#             righteyedist = get_eye_distance(frame, face_landmarks, 159, 145)
#             lefteyedist = get_eye_distance(frame, face_landmarks, 386, 374)

#             blinkcheck, lastblinktime = blinking(righteyedist, lefteyedist, lastblinktime)
#             gazeoff, lastgazetime = gaze_detector(frame, face_landmarks, lastgazetime)

#             if blinkcheck:
#                 count += 1
#             if gazeoff:
#                 log("Don't look away!")
#                 eyecount += 1

#             hand_landmarks = results.left_hand_landmarks or results.right_hand_landmarks
#             if hand_landmarks:
                
#                 touched, mouth_last_check, mouth_start_time, mouthtouch_count = update_touch_state(
#                     frame, face_landmarks, hand_landmarks, mouth_last_check, mouth_start_time, mouthtouch_count, contact_func=hand_mouth_contact
#                 )
#                 if touched:
#                     log(f"Hand touched mouth! Count: {mouthtouch_count}")

#                 # Nose
#                 touched, nose_last_check, nose_start_time, nosetouch_count = update_touch_state(
#                     frame, face_landmarks, hand_landmarks, nose_last_check, nose_start_time, nosetouch_count, contact_func=hand_nose_contact
#                 )
#                 if touched:
#                     log(f"Hand touched nose! Count: {nosetouch_count}")

#                 # Eye
#                 touched, eye_last_check, eye_start_time, eyetouch_count = update_touch_state(
#                     frame, face_landmarks, hand_landmarks, eye_last_check, eye_start_time, eyetouch_count, contact_func=hand_eye_contact
#                 )
#                 if touched:
#                     log(f"Hand touched eye! Count: {eyetouch_count}")

#                 # Ear
#                 touched, ear_last_check, ear_start_time, eartouch_count = update_touch_state(
#                     frame, face_landmarks, hand_landmarks, ear_last_check, ear_start_time, eartouch_count, contact_func=hand_ear_contact
#                 )
#                 if touched:
#                     log(f"Hand touched ear! Count: {eartouch_count}")

#                 # Neck
#                 touched, neck_last_check, neck_start_time, necktouch_count = update_touch_state(
#                     frame, face_landmarks, hand_landmarks, neck_last_check, neck_start_time, necktouch_count, contact_func=hand_neck_contact
#                 )
#                 if touched:
#                     log(f"Hand touched neck! Count: {necktouch_count}")


#         if time.time() - lastbpmtime >= 10:
#             bpm, lastbpmtime = blinkperminute(count, lastbpmtime)
#             avgcount += 1
#             avgbpm = ((avgbpm * (avgcount - 1)) + bpm) / avgcount
#             log(f"BPM: {bpm}")
#             count = 0

#         cv2.imshow("Live Feedback", frame)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     cap.release()
#     cv2.destroyAllWindows()
#     holistic.close()
#     end_time = time.time()
#     session_duration = round(end_time - start_time, 2)  

#     log("[INFO] Final Report:")
#     report = {
#         "eye_contact_breaks": eyecount,
#         "total_blinks": count,
#         "mouth_touch_count": mouthtouch_count,
#         "nose_touch_count": nosetouch_count,
#         "eye_touch_count": eyetouch_count,
#         "ear_touch_count": eartouch_count,
#         "neck_touch_count": necktouch_count,
#         "arms_crossed_duration": round(time.time() - arms_crossed_start, 2) if arms_crossed_start else 0,
#         "posture_warnings": "Slouching detected" if lastslouch else "Good posture",
#         "final_bpm": round(avgbpm, 2),
#         "duration_sec": session_duration
#     }
#     log(str(report))
#     return report


from webcam_utils import *
from eye_contact_detector import *
from posture_detector import *
from hand_gesture import *
from leg_gestures import *
import cv2

def run_detection_session(video_path, log=print):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    true_video_duration = frame_count / fps if fps else 0
    return run_analysis(cap, log, true_duration=true_video_duration)

def run_live_session(log=print):
    cap = cv2.VideoCapture(0)
    return run_analysis(cap, log, true_duration=None)

def run_analysis(cap, log=print, true_duration=None):
    import mediapipe as mp
    import time
    start_time = time.time()

    mp_holistic = mp.solutions.holistic
    holistic = mp_holistic.Holistic(
        static_image_mode=False,
        model_complexity=1,
        smooth_landmarks=True,
        refine_face_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    avgbpm = avgcount = count = eyecount = 0
    lastblinktime = lastbpmtime = time.time()
    lastgazetime = time.time()
    lastcrossed_time = time.time()
    slouchcount = 0
    lastslouch = 0
    legcrossedcount=0
    legbouncingcount=0
    hand_on_hip_count = 0
    lastbounce_time = time.time()
    lasthandonhip = time.time()
    arms_crossed_count = 0
    hand_violation_logged = False
    arms_crossed_printed = False
    arms_crossed_start = None
    
    lastarms_crossed_time = time.time()
    mouth_last_check = nose_last_check = eye_last_check = ear_last_check = neck_last_check = None
    mouth_start_time = nose_start_time = eye_start_time = ear_start_time = neck_start_time = None
    mouthtouch_count = nosetouch_count = eyetouch_count = eartouch_count = necktouch_count = 0

    cv2.namedWindow("Live Feedback", cv2.WINDOW_NORMAL)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            log("[ERROR] Couldn't read frame from video.")
            break

        rgb_frame = bgr2rgb(frame)
        results = holistic.process(rgb_frame)

        if results.face_landmarks:
            frame = display_facial_landmarks(frame, results.face_landmarks)
        if results.pose_landmarks:
            frame = display_pose(frame, results.pose_landmarks)
            frame = display_legs(frame, results.pose_landmarks)
        if results.left_hand_landmarks:
            frame = display_hand(frame, results.left_hand_landmarks)
        if results.right_hand_landmarks:
            frame = display_hand(frame, results.right_hand_landmarks)

        if results.pose_landmarks:
            legscrossed, lastcrossed_time = detect_crossed_legs(results.pose_landmarks, lastcrossed_time)
            if legscrossed:
                legcrossedcount += 1
                log("Legs crossed for 3+ seconds!")
            slouch, lastslouch = slouch_detector(frame, results.pose_landmarks, lastslouch)
            if slouch:
                slouchcount += 1    
                log("Sit Straight!")
                
            leg_bounce,lastbounce_time=detect_leg_bouncing(results.pose_landmarks, lastbounce_time)
            if leg_bounce:
                legbouncingcount += 1
                log("Leg bouncing detected!")
            
            handsonhip,lasthandonhip=detect_hands_on_hip(results.pose_landmarks, lasthandonhip)
            if handsonhip:
                hand_on_hip_count += 1
                log("Hand on hip detected!")

            arms_crossed,lastarms_crossed_time = arms_crossed_detector(results.pose_landmarks, lastarms_crossed_time)
            if arms_crossed:
                arms_crossed_count+= 1
                log("Arms crossed for 3+ seconds!")

        

            
            for hand in [results.left_hand_landmarks, results.right_hand_landmarks]:
                if hand and check_hand_in_restricted_zone(frame, results.pose_landmarks, hand, log):
                    if not hand_violation_logged:
                        log("⚠️ Hand entered restricted zone!")
                        hand_violation_logged = True
                        

        
        
        if results.face_landmarks:
            face_landmarks = results.face_landmarks
            righteyedist = get_eye_distance(frame, face_landmarks, 159, 145)
            lefteyedist = get_eye_distance(frame, face_landmarks, 386, 374)

            blinkcheck, lastblinktime = blinking(righteyedist, lefteyedist, lastblinktime)
            gazeoff, lastgazetime = gaze_detector(frame, face_landmarks, lastgazetime)

            if blinkcheck:
                count += 1
            if gazeoff:
                log("Don't look away!")
                eyecount += 1

            hand_landmarks = results.left_hand_landmarks or results.right_hand_landmarks
            if hand_landmarks:
                touched, mouth_last_check, mouth_start_time, mouthtouch_count = update_touch_state(
                    frame, face_landmarks, hand_landmarks, mouth_last_check, mouth_start_time, mouthtouch_count, contact_func=hand_mouth_contact
                )
                if touched:
                    log(f"Hand touched mouth! Count: {mouthtouch_count}")

                touched, nose_last_check, nose_start_time, nosetouch_count = update_touch_state(
                    frame, face_landmarks, hand_landmarks, nose_last_check, nose_start_time, nosetouch_count, contact_func=hand_nose_contact
                )
                if touched:
                    log(f"Hand touched nose! Count: {nosetouch_count}")

                touched, eye_last_check, eye_start_time, eyetouch_count = update_touch_state(
                    frame, face_landmarks, hand_landmarks, eye_last_check, eye_start_time, eyetouch_count, contact_func=hand_eye_contact
                )
                if touched:
                    log(f"Hand touched eye! Count: {eyetouch_count}")

                touched, ear_last_check, ear_start_time, eartouch_count = update_touch_state(
                    frame, face_landmarks, hand_landmarks, ear_last_check, ear_start_time, eartouch_count, contact_func=hand_ear_contact
                )
                if touched:
                    log(f"Hand touched ear! Count: {eartouch_count}")

                touched, neck_last_check, neck_start_time, necktouch_count = update_touch_state(
                    frame, face_landmarks, hand_landmarks, neck_last_check, neck_start_time, necktouch_count, contact_func=hand_neck_contact
                )
                if touched:
                    log(f"Hand touched neck! Count: {necktouch_count}")

        if time.time() - lastbpmtime >= 10:
            bpm, lastbpmtime = blinkperminute(count, lastbpmtime)
            avgcount += 1
            avgbpm = ((avgbpm * (avgcount - 1)) + bpm) / avgcount
            log(f"BPM: {bpm}")
            count = 0

        cv2.imshow("Live Feedback", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    holistic.close()
    end_time = time.time()
    session_duration = round(end_time - start_time, 2)
    video_duration = round(true_duration, 2) if true_duration else session_duration

    log("[INFO] Final Report:")
    report = {
        "eye_contact_breaks": eyecount,
        "total_blinks": count,
        "mouth_touch_count": mouthtouch_count,
        "nose_touch_count": nosetouch_count,
        "eye_touch_count": eyetouch_count,
        "ear_touch_count": eartouch_count,
        "neck_touch_count": necktouch_count,
        "arms_crossed_for_3_sec_count": arms_crossed_count,
        "slouching": slouchcount,
        "leg_crossed_count": legcrossedcount,
        "leg_bouncing_count": legbouncingcount,
        "hand_on_hip_count": hand_on_hip_count,
        "final_bpm": round(avgbpm, 2),
        "duration_sec": video_duration
    }
    # report = {
    #     "eye_contact_breaks": eyecount,
    #     "total_blinks": count,
    #     "mouth_touch_count": mouthtouch_count,
    #     "nose_touch_count": nosetouch_count,
    #     "eye_touch_count": eyetouch_count,
    #     "ear_touch_count": eartouch_count,
    #     "neck_touch_count": necktouch_count,
    #     "arms_crossed_duration": round(time.time() - arms_crossed_start, 2) if arms_crossed_start else 0,
    #     "posture_warnings": "Slouching detected" if lastslouch else "Good posture",
    #     "final_bpm": round(avgbpm, 2),
    #     "duration_sec": session_duration
    # }
    log(str(report))
    return report
