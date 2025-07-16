# def rank_user_behavior(results, emotion_stats):
#     comments = []
#     rubric_scores = {}

#     duration_sec = results.get("duration_sec", 60)
#     duration_min = max(duration_sec / 60, 1) 

#     # 1. STANCE
#     if results.get("posture_warnings") == "Slouching detected":
#         stance_score = 1
#         comments.append("Slouching observed — posture detracted from message.")
#     else:
#         stance_score = 5
#         comments.append("Good posture — stable stance throughout.")
#     rubric_scores["stance"] = stance_score

#     # 2. EYE CONTACT
#     eye_breaks = results.get("eye_contact_breaks", 0)
#     eye_break_rate = eye_breaks / duration_min

#     if eye_break_rate > 15:
#         eye_score = 1
#         comments.append("Very limited or distracted eye contact.")
#     elif eye_break_rate > 7:
#         eye_score = 3
#         comments.append("Inconsistent eye contact — frequent looking away.")
#     else:
#         eye_score = 5
#         comments.append("Consistent and appropriate eye contact.")
#     rubric_scores["eye_contact"] = eye_score

#     # === 3. FACIAL EXPRESSION ===
#     happy = emotion_stats.get("happy", 0)
#     sad_fear = emotion_stats.get("sad", 0) + emotion_stats.get("fear", 0)

#     if happy >= 20 and sad_fear < 5:
#         face_score = 5
#         comments.append("Facial expressions were consistent and positive.")
#     elif happy >= 10 or sad_fear >= 5:
#         face_score = 3
#         comments.append("Facial expressions were present but inconsistent.")
#     else:
#         face_score = 1
#         comments.append("Very few or flat facial expressions observed.")
#     rubric_scores["facial_expression"] = face_score

#     # 4. GESTURES 
#     total_touches = sum([
#         results.get('mouth_touch_count', 0),
#         results.get('nose_touch_count', 0),
#         results.get('eye_touch_count', 0),
#         results.get('ear_touch_count', 0),
#         results.get('neck_touch_count', 0)
#     ])
#     touch_rate = total_touches / duration_min

#     if touch_rate > 6:
#         gesture_score = 1
#         comments.append("Distracting or fidgety gestures throughout.")
#     elif 2 <= touch_rate <= 6:
#         gesture_score = 3
#         comments.append("Some purposeful gestures, mixed with nervous ones.")
#     else:
#         gesture_score = 5
#         comments.append("Gestures were purposeful and minimal.")
#     rubric_scores["gestures"] = gesture_score

#     # Final Rank 
#     scores = list(rubric_scores.values())
#     count_1 = scores.count(1)
#     count_3_or_5 = sum(1 for s in scores if s in [3, 5])

#     if count_1 >= 2:
#         rank = "Needs Improvement"
#     elif all(s == 5 for s in scores):
#         rank = "Excellent"
#     elif count_3_or_5 >= 3:
#         rank = "Good"
#     else:
#         rank = "Average"

#     return {
#         "rubric_scores": rubric_scores,
#         "rank": rank,
#         "comments": comments
#     }

def rank_user_behavior(report, facial_expression_score, strictness=1):

    if strictness == 2:
        duration_unit = max(1, report["duration_sec"] / 30)
    elif strictness == 3:
        duration_unit = max(1, report["duration_sec"] / 15)
    elif strictness == 4:
        duration_unit = max(1, report["duration_sec"] / 60)
    else: 
        duration_unit = 1
    norm = lambda count: count / duration_unit

    eye_contact_breaks = norm(report["eye_contact_breaks"])
    total_blinks = norm(report["total_blinks"])
    mouth_touches = norm(report["mouth_touch_count"])
    nose_touches = norm(report["nose_touch_count"])
    eye_touches = norm(report["eye_touch_count"])
    ear_touches = norm(report["ear_touch_count"])
    neck_touches = norm(report["neck_touch_count"])
    arms_crossed = norm(report["arms_crossed_for_3_sec_count"])
    slouching = norm(report["slouching"])
    leg_crossed = norm(report["leg_crossed_count"])
    leg_bouncing = norm(report["leg_bouncing_count"])
    hand_on_hip = norm(report["hand_on_hip_count"])
    bpm = report["final_bpm"]

    # ---- Primary Rubric Scores ----

    # STANCE (based on legs and posture)
    stance_metric = leg_crossed + leg_bouncing + slouching
    stance_score = 5 if stance_metric <= 2 else 3 if stance_metric <= 5 else 1

    # EYE CONTACT
    eye_score = 5 if eye_contact_breaks <= 4 else 3 if eye_contact_breaks <= 10 else 1

    # GESTURES (arms crossed + hands on hip)
    gesture_metric = arms_crossed + hand_on_hip
    gesture_score = 5 if gesture_metric <= 2 else 3 if gesture_metric <= 6 else 1


    # === 3. FACIAL EXPRESSION ===
    happy = facial_expression_score.get("happy", 0)
    sad_fear = facial_expression_score.get("sad", 0) + facial_expression_score.get("fear", 0)

    if happy >= 20 and sad_fear < 5:
        facial_score = 5
    elif happy >= 10 or sad_fear >= 5:
        facial_score = 3
    else:
        facial_score = 1

    # ---- Bonus/Supportive Scores ----

    # FIDGETING (face touches + hand on hip)
    total_fidget = mouth_touches + nose_touches + eye_touches + ear_touches + neck_touches + hand_on_hip
    fidget_score = 5 if total_fidget <= 3 else 3 if total_fidget <= 6 else 1

    # BPM Stress Indicator
    bpm_score = 5 if bpm <= 20 else 3 if bpm <= 30 else 1

    # TOTAL SCORE
    category_scores = {
        "stance": stance_score,
        "eye_contact": eye_score,
        "gestures": gesture_score,
        "facial_expression": facial_score,
        "fidgeting": fidget_score,
        "bpm_control": bpm_score
    }

    total_score = sum(category_scores.values())
    average_score = round(total_score / len(category_scores), 2)

    return {
        "rubric_scores":category_scores,
        "total_score": total_score,
        "average_score": average_score,
        "rating": (
            "Excellent" if average_score >= 4.5 else
            "Good" if average_score >= 3.0 else
            "Needs Improvement"
        ),
        "graded_per": ("1 min" if strictness == 1 else "30 sec" if strictness == 2 else "15 sec"),
    }
