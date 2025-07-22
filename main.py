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
from collections import deque

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
    blink_times = []
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
    lastarms_crossed_time = time.time()
    sway={
        'left_leg_x': deque(maxlen=10),
        'right_leg_x': deque(maxlen=10), 
        'last_sway_time': 0,
        'frame_count': 0
    }
    eyehistory = deque(maxlen=10)
    mouth_last_check = nose_last_check = eye_last_check = ear_last_check = neck_last_check = None
    mouth_start_time = nose_start_time = eye_start_time = ear_start_time = neck_start_time = None
    mouthtouch_count = nosetouch_count = eyetouch_count = eartouch_count = necktouch_count = 0

    cv2.namedWindow("Live Feedback", cv2.WINDOW_NORMAL)
    while cap.isOpened():
        current_time = time.time()
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
                
            motion_detected, sway = detect_leg_motion(
            results.pose_landmarks, 
            sway
            )
            if motion_detected:
                legbouncingcount += 1
                log("Leg bouncing detected!")
            
            # handsonhip,lasthandonhip=detect_hands_on_hip(results.pose_landmarks, lasthandonhip)
            # if handsonhip:
            hand_on_hip_count = 0

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

            blinkcheck, lastblinktime = blinking(righteyedist, lefteyedist, lastblinktime, eyehistory)
            if blinkcheck:
                blink_times.append(current_time)
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

        # if time.time() - lastbpmtime >= 10:
        #     bpm, lastbpmtime = blinkperminute(count, lastbpmtime)
        #     avgcount += 1
        #     avgbpm = ((avgbpm * (avgcount - 1)) + bpm) / avgcount
        #     log(f"BPM: {bpm}")
        #     count = 0
            
        if time.time() - lastbpmtime >= 10:
            recent_blinks = [t for t in blink_times if current_time - t <= 60.0] 
            bpm = len(recent_blinks)
            avgcount += 1
            avgbpm = ((avgbpm * (avgcount - 1)) + bpm) / avgcount
            log(f"BPM: {bpm}")
            lastbpmtime = time.time()

        cv2.imshow("Live Feedback", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    holistic.close()
    end_time = time.time()
    session_duration = round(end_time - start_time, 2)
    print(f"[INFO] Session Duration: {session_duration} seconds")
    video_duration = round(true_duration, 2) if true_duration else session_duration

    log("[INFO] Final Report:")
    report = {
        'eye_contact_breaks' : round(abs((eyecount)*video_duration/session_duration)) if session_duration > 0 else 0,
        'total_blinks': len(blink_times),
        'mouth_touch_count' : round((mouthtouch_count)*video_duration/session_duration) if session_duration > 0 else 0,
        'nose_touch_count' : round((nosetouch_count)*video_duration/session_duration) if session_duration > 0 else 0,
        'eye_touch_count' : round((eyetouch_count)*video_duration/session_duration) if session_duration > 0 else 0,
        'ear_touch_count' : round((eartouch_count)*video_duration/session_duration) if session_duration > 0 else 0,
        'neck_touch_count' : round((necktouch_count)*video_duration/session_duration) if session_duration > 0 else 0,
        'arms_crossed_for_3_sec_count': round((arms_crossed_count)*video_duration/session_duration) if session_duration > 0 else 0,
        'slouching': round(abs((slouchcount)*video_duration/session_duration)) if session_duration > 0 else 0,
        'leg_crossed_count': round((legcrossedcount)*video_duration/session_duration) if session_duration > 0 else 0,
        'leg_bouncing_count': round((legbouncingcount)*video_duration/session_duration) if session_duration > 0 else 0,
        'hand_on_hip_count': round((hand_on_hip_count)*video_duration/session_duration) if session_duration > 0 else 0,
        'final_bpm': round(avgbpm, 2),
        'duration_sec': video_duration,
        'session_duration': session_duration
    
    }
    
    
    
    # report = {
    #     "eye_contact_breaks": eyecount,
    #     "total_blinks": count,
    #     "mouth_touch_count": mouthtouch_count,
    #     "nose_touch_count": nosetouch_count,
    #     "eye_touch_count": eyetouch_count,
    #     "ear_touch_count": eartouch_count,
    #     "neck_touch_count": necktouch_count,
    #     "arms_crossed_for_3_sec_count": arms_crossed_count,
    #     "slouching": slouchcount,
    #     "leg_crossed_count": legcrossedcount,
    #     "leg_bouncing_count": legbouncingcount,
    #     "hand_on_hip_count": hand_on_hip_count,
    #     "final_bpm": round(avgbpm, 2),
    #     "duration_sec": video_duration
    # }
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




# def run_detection_session(video_path, log=print):
#     cap = cv2.VideoCapture(video_path)
#     fps = cap.get(cv2.CAP_PROP_FPS)
#     frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
#     true_video_duration = frame_count / fps if fps else 0
#     return run_analysis(cap, log, true_duration=true_video_duration)

# def run_live_session(log=print):
#     cap = cv2.VideoCapture(0)
#     return run_analysis(cap, log, true_duration=None)

# def run_analysis(cap, log=print, true_duration=None):
#     import mediapipe as mp
#     import time
#     from collections import deque
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

#     # Time-based tracking for events
#     blink_times = []
#     avgbpm = 0
#     avgcount = 0
#     eyecount = 0  # count of gaze-off episodes
#     slouchcount = 0  # count of slouch episodes  
#     legcrossedcount = 0  # count of leg-crossed episodes
#     legbouncingcount = 0  # count of leg-bouncing episodes
#     hand_on_hip_count = 0
#     arms_crossed_count = 0  # count of arms-crossed episodes
#     mouthtouch_count = nosetouch_count = eyetouch_count = eartouch_count = necktouch_count = 0
    
#     # Time-based state tracking
#     lastblinktime = lastbpmtime = time.time()
#     lastgazetime = time.time()
#     lastcrossed_time = time.time()
#     lastslouch = 0
#     lastbounce_time = time.time()
#     lasthandonhip = time.time()
#     hand_violation_logged = False
#     lastarms_crossed_time = time.time()
    
#     # State management for continuous behaviors
#     slouch_state = {'active': False, 'start_time': None}
#     crossed_legs_state = {'active': False, 'start_time': None}
#     arms_crossed_state = {'active': False, 'start_time': None}
#     gaze_off_state = {'active': False, 'start_time': None}
#     leg_bouncing_state = {'last_detection': 0}
    
#     # Hand touch states
#     touch_states = {
#         'mouth': {'active': False, 'start_time': None, 'last_log_time': 0},
#         'nose': {'active': False, 'start_time': None, 'last_log_time': 0},
#         'eye': {'active': False, 'start_time': None, 'last_log_time': 0},
#         'ear': {'active': False, 'start_time': None, 'last_log_time': 0},
#         'neck': {'active': False, 'start_time': None, 'last_log_time': 0}
#     }
    
#     # Motion and eye tracking (keep original structure)
#     sway = {
#         'left_leg_x': deque(maxlen=10),
#         'right_leg_x': deque(maxlen=10), 
#         'last_sway_time': 0,
#         'frame_count': 0
#     }
#     eyehistory = deque(maxlen=10)
    
#     # Touch detection variables (keeping original names)
#     mouth_last_check = nose_last_check = eye_last_check = ear_last_check = neck_last_check = None
#     mouth_start_time = nose_start_time = eye_start_time = ear_start_time = neck_start_time = None

#     # Minimum durations (seconds)
#     MIN_SLOUCH_DURATION = 2.0
#     MIN_CROSSED_LEGS_DURATION = 3.0
#     MIN_ARMS_CROSSED_DURATION = 3.0
#     MIN_GAZE_OFF_DURATION = 2.0
#     MIN_TOUCH_DURATION = 0.5
#     MIN_BOUNCE_INTERVAL = 2.0

#     cv2.namedWindow("Live Feedback", cv2.WINDOW_NORMAL)
#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret:
#             log("[ERROR] Couldn't read frame from video.")
#             break

#         current_time = time.time()
#         rgb_frame = bgr2rgb(frame)
#         results = holistic.process(rgb_frame)

#         if results.face_landmarks:
#             frame = display_facial_landmarks(frame, results.face_landmarks)
#         if results.pose_landmarks:
#             frame = display_pose(frame, results.pose_landmarks)
#             frame = display_legs(frame, results.pose_landmarks)
#         if results.left_hand_landmarks:
#             frame = display_hand(frame, results.left_hand_landmarks)
#         if results.right_hand_landmarks:
#             frame = display_hand(frame, results.right_hand_landmarks)

#         if results.pose_landmarks:
#             # Legs crossed detection with time-based counting
#             legscrossed, lastcrossed_time = detect_crossed_legs(results.pose_landmarks, lastcrossed_time)
#             if legscrossed and not crossed_legs_state['active']:
#                 crossed_legs_state['active'] = True
#                 crossed_legs_state['start_time'] = current_time
#             elif not legscrossed and crossed_legs_state['active']:
#                 duration = current_time - crossed_legs_state['start_time']
#                 if duration >= MIN_CROSSED_LEGS_DURATION:
#                     legcrossedcount += 1
#                     log("Legs crossed for 3+ seconds!")
#                 crossed_legs_state['active'] = False
#                 crossed_legs_state['start_time'] = None

#             # Slouch detection with time-based counting
#             slouch, lastslouch = slouch_detector(frame, results.pose_landmarks, lastslouch)
#             if slouch and not slouch_state['active']:
#                 slouch_state['active'] = True
#                 slouch_state['start_time'] = current_time
#             elif not slouch and slouch_state['active']:
#                 duration = current_time - slouch_state['start_time']
#                 if duration >= MIN_SLOUCH_DURATION:
#                     slouchcount += 1    
#                     log("Sit Straight!")
#                 slouch_state['active'] = False
#                 slouch_state['start_time'] = None
                
#             # Leg bouncing with time-gated detection
#             motion_detected, sway = detect_leg_motion(results.pose_landmarks, sway)
#             if motion_detected and current_time - leg_bouncing_state['last_detection'] >= MIN_BOUNCE_INTERVAL:
#                 legbouncingcount += 1
#                 leg_bouncing_state['last_detection'] = current_time
#                 log("Leg bouncing detected!")
            
#             # Keep hands on hip disabled (original code)
#             hand_on_hip_count = 0

#             # Arms crossed detection with time-based counting
#             arms_crossed, lastarms_crossed_time = arms_crossed_detector(results.pose_landmarks, lastarms_crossed_time)
#             if arms_crossed and not arms_crossed_state['active']:
#                 arms_crossed_state['active'] = True
#                 arms_crossed_state['start_time'] = current_time
#             elif not arms_crossed and arms_crossed_state['active']:
#                 duration = current_time - arms_crossed_state['start_time']
#                 if duration >= MIN_ARMS_CROSSED_DURATION:
#                     arms_crossed_count += 1
#                     log("Arms crossed for 3+ seconds!")
#                 arms_crossed_state['active'] = False
#                 arms_crossed_state['start_time'] = None

#             # Hand in restricted zone (keep original logic)
#             for hand in [results.left_hand_landmarks, results.right_hand_landmarks]:
#                 if hand and check_hand_in_restricted_zone(frame, results.pose_landmarks, hand, log):
#                     if not hand_violation_logged:
#                         log("⚠️ Hand entered restricted zone!")
#                         hand_violation_logged = True

#         if results.face_landmarks:
#             face_landmarks = results.face_landmarks
#             righteyedist = get_eye_distance(frame, face_landmarks, 159, 145)
#             lefteyedist = get_eye_distance(frame, face_landmarks, 386, 374)

#             # Blink detection - store timestamps instead of just counting
#             blinkcheck, lastblinktime = blinking(righteyedist, lefteyedist, lastblinktime, eyehistory)
#             if blinkcheck:
#                 blink_times.append(current_time)

#             # Gaze detection with time-based counting
#             gazeoff, lastgazetime = gaze_detector(frame, face_landmarks, lastgazetime)
#             if gazeoff and not gaze_off_state['active']:
#                 gaze_off_state['active'] = True
#                 gaze_off_state['start_time'] = current_time
#             elif not gazeoff and gaze_off_state['active']:
#                 duration = current_time - gaze_off_state['start_time']
#                 if duration >= MIN_GAZE_OFF_DURATION:
#                     eyecount += 1
#                     log("Don't look away!")
#                 gaze_off_state['active'] = False
#                 gaze_off_state['start_time'] = None

#             # Hand touch detection with time-based counting
#             hand_landmarks = results.left_hand_landmarks or results.right_hand_landmarks
#             if hand_landmarks:
#                 # Mouth touch
#                 touching = hand_mouth_contact(frame, face_landmarks, hand_landmarks)
#                 if touching and not touch_states['mouth']['active']:
#                     touch_states['mouth']['active'] = True
#                     touch_states['mouth']['start_time'] = current_time
#                 elif not touching and touch_states['mouth']['active']:
#                     duration = current_time - touch_states['mouth']['start_time']
#                     if duration >= MIN_TOUCH_DURATION and current_time - touch_states['mouth']['last_log_time'] > 1.0:
#                         mouthtouch_count += 1
#                         touch_states['mouth']['last_log_time'] = current_time
#                         log(f"Hand touched mouth! Count: {mouthtouch_count}")
#                     touch_states['mouth']['active'] = False
#                     touch_states['mouth']['start_time'] = None

#                 # Nose touch
#                 touching = hand_nose_contact(frame, face_landmarks, hand_landmarks)
#                 if touching and not touch_states['nose']['active']:
#                     touch_states['nose']['active'] = True
#                     touch_states['nose']['start_time'] = current_time
#                 elif not touching and touch_states['nose']['active']:
#                     duration = current_time - touch_states['nose']['start_time']
#                     if duration >= MIN_TOUCH_DURATION and current_time - touch_states['nose']['last_log_time'] > 1.0:
#                         nosetouch_count += 1
#                         touch_states['nose']['last_log_time'] = current_time
#                         log(f"Hand touched nose! Count: {nosetouch_count}")
#                     touch_states['nose']['active'] = False
#                     touch_states['nose']['start_time'] = None

#                 # Eye touch
#                 touching = hand_eye_contact(frame, face_landmarks, hand_landmarks)
#                 if touching and not touch_states['eye']['active']:
#                     touch_states['eye']['active'] = True
#                     touch_states['eye']['start_time'] = current_time
#                 elif not touching and touch_states['eye']['active']:
#                     duration = current_time - touch_states['eye']['start_time']
#                     if duration >= MIN_TOUCH_DURATION and current_time - touch_states['eye']['last_log_time'] > 1.0:
#                         eyetouch_count += 1
#                         touch_states['eye']['last_log_time'] = current_time
#                         log(f"Hand touched eye! Count: {eyetouch_count}")
#                     touch_states['eye']['active'] = False
#                     touch_states['eye']['start_time'] = None

#                 # Ear touch
#                 touching = hand_ear_contact(frame, face_landmarks, hand_landmarks)
#                 if touching and not touch_states['ear']['active']:
#                     touch_states['ear']['active'] = True
#                     touch_states['ear']['start_time'] = current_time
#                 elif not touching and touch_states['ear']['active']:
#                     duration = current_time - touch_states['ear']['start_time']
#                     if duration >= MIN_TOUCH_DURATION and current_time - touch_states['ear']['last_log_time'] > 1.0:
#                         eartouch_count += 1
#                         touch_states['ear']['last_log_time'] = current_time
#                         log(f"Hand touched ear! Count: {eartouch_count}")
#                     touch_states['ear']['active'] = False
#                     touch_states['ear']['start_time'] = None

#                 # Neck touch
#                 touching = hand_neck_contact(frame, face_landmarks, hand_landmarks)
#                 if touching and not touch_states['neck']['active']:
#                     touch_states['neck']['active'] = True
#                     touch_states['neck']['start_time'] = current_time
#                 elif not touching and touch_states['neck']['active']:
#                     duration = current_time - touch_states['neck']['start_time']
#                     if duration >= MIN_TOUCH_DURATION and current_time - touch_states['neck']['last_log_time'] > 1.0:
#                         necktouch_count += 1
#                         touch_states['neck']['last_log_time'] = current_time
#                         log(f"Hand touched neck! Count: {necktouch_count}")
#                     touch_states['neck']['active'] = False
#                     touch_states['neck']['start_time'] = None

#         # BPM calculation every 10 seconds using time-based blinks
#         if time.time() - lastbpmtime >= 10:
#             # Calculate BPM from recent blinks
#             recent_blinks = [t for t in blink_times if current_time - t <= 60.0]  # Last minute
#             bpm = len(recent_blinks)
#             avgcount += 1
#             avgbpm = ((avgbpm * (avgcount - 1)) + bpm) / avgcount
#             log(f"BPM: {bpm}")
#             lastbpmtime = time.time()

#         cv2.imshow("Live Feedback", frame)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     # Finalize any ongoing states before ending
#     current_time = time.time()
    
#     # Check if any continuous behaviors are still active and meet minimum duration
#     if slouch_state['active']:
#         duration = current_time - slouch_state['start_time']
#         if duration >= MIN_SLOUCH_DURATION:
#             slouchcount += 1
            
#     if crossed_legs_state['active']:
#         duration = current_time - crossed_legs_state['start_time']
#         if duration >= MIN_CROSSED_LEGS_DURATION:
#             legcrossedcount += 1
            
#     if arms_crossed_state['active']:
#         duration = current_time - arms_crossed_state['start_time']
#         if duration >= MIN_ARMS_CROSSED_DURATION:
#             arms_crossed_count += 1
            
#     if gaze_off_state['active']:
#         duration = current_time - gaze_off_state['start_time']
#         if duration >= MIN_GAZE_OFF_DURATION:
#             eyecount += 1

#     cap.release()
#     cv2.destroyAllWindows()
#     holistic.close()
#     end_time = time.time()
#     session_duration = round(end_time - start_time, 2)
#     video_duration = round(true_duration, 2) if true_duration else session_duration

#     log("[INFO] Final Report:")
#     report = {
#         "eye_contact_breaks": eyecount,
#         "total_blinks": len(blink_times),
#         "mouth_touch_count": mouthtouch_count,
#         "nose_touch_count": nosetouch_count,
#         "eye_touch_count": eyetouch_count,
#         "ear_touch_count": eartouch_count,
#         "neck_touch_count": necktouch_count,
#         "arms_crossed_for_3_sec_count": arms_crossed_count,
#         "slouching": slouchcount,
#         "leg_crossed_count": legcrossedcount,
#         "leg_bouncing_count": legbouncingcount,
#         "hand_on_hip_count": hand_on_hip_count,
#         "final_bpm": round(avgbpm, 2),
#         "duration_sec": video_duration
#     }
#     log(str(report))
#     return report