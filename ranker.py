
def rank_user_behavior(report, facial_expression_score, strictness=1, abnormal_thresholds=None):
    if abnormal_thresholds is None:
        abnormal_thresholds = {
            "eye_contact_breaks": 4,
            "total_blinks": 20,
            "mouth_touch_count": 1,
            "nose_touch_count": 1,
            "eye_touch_count": 1,
            "ear_touch_count": 1,
            "neck_touch_count": 1,
            "arms_crossed_for_3_sec_count": 2,
            "slouching": 1,
            "leg_crossed_count": 2,
            "leg_bouncing_count": 8,
            "hand_on_hip_count": 2,
            "hands_outside_gesture_box_count": 3,
            "hands_clenched_count": 2,
            "hands_behind_back_count": 2,
            "hands_in_pockets_count": 3,
            "final_bpm": 20,
        }

    # Normalize per duration
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
    mouth_touches = norm(report["mouth_touch_count"])
    nose_touches = norm(report["nose_touch_count"])
    eye_touches = norm(report["eye_touch_count"])
    ear_touches = norm(report["ear_touch_count"])
    neck_touches = norm(report["neck_touch_count"])
    leg_bouncing = norm(report["leg_bouncing_count"])
    hands_outside_gesture_box = norm(report.get("hands_outside_gesture_box_count", 0))

    
    
    # Stance.
    
    stancemetric=leg_bouncing
    stance_score = (1 if stancemetric >= 8  else
                    3 if stancemetric >= 3 and stancemetric < 8 else
                    5 if stancemetric < 3 else 0)
    
    # Eye Contact
    
    eye_score = (5 if eye_contact_breaks >= 9 else
                 3 if eye_contact_breaks >= 5 and eye_contact_breaks < 9 else
                 1 if eye_contact_breaks < 5 else 0)

    #Gestures
    fitget_metric = mouth_touches + nose_touches + eye_touches + ear_touches + neck_touches
    gesture_score=   (5 if hands_outside_gesture_box >=15 else
                    3 if hands_outside_gesture_box >= 10 and hands_outside_gesture_box < 15 else
                    1 if hands_outside_gesture_box < 10 or fitget_metric > 10  else 0)
    
    # Facial Expression
    
    happy = facial_expression_score.get("happy", 0)
    sad_fear = facial_expression_score.get("sad", 0) + facial_expression_score.get("fear", 0)

    facial_score = (
        5 if happy >= 20 and sad_fear < 5 else
        3 if happy >= 10 or sad_fear >= 5 else
        1 if happy < 10 else 0
    )


     # TOTAL SCORE
    category_scores = {
        "stance": stance_score,
        "eye_contact": eye_score,
        "gestures": gesture_score,
        "facial_expression": facial_score,
    }

    total_score = sum(category_scores.values())
    average_score = round(total_score / len(category_scores), 2)

    return {
        "rubric_scores": category_scores,
        "total_score": total_score,
        "average_score": average_score,
        "rating": (
            "Excellent" if average_score >= 4.5 else
            "Good" if average_score >= 3.0 else
            "Needs Improvement"
        ),
        "graded_per": (
            "1 min" if strictness == 1 else
            "30 sec" if strictness == 2 else
            "15 sec"
        ),
    }
    
    
    
    # STANCE
    # stance_metric = leg_crossed + leg_bouncing + slouching
    # stance_score = (
    #     5 if stance_metric <= abnormal_thresholds["slouching"] else
    #     3 if stance_metric <= abnormal_thresholds["slouching"] * 2 else
    #     1
    # )

    # # EYE CONTACT
    # eye_score = (
    #     5 if eye_contact_breaks <= abnormal_thresholds["eye_contact_breaks"] else
    #     3 if eye_contact_breaks <= abnormal_thresholds["eye_contact_breaks"] * 2.5 else
    #     1
    # )

    # # GESTURES
    # gesture_metric = arms_crossed + hand_on_hip
    # gesture_score = (
    #     5 if gesture_metric <= abnormal_thresholds["arms_crossed_for_3_sec_count"] else
    #     3 if gesture_metric <= abnormal_thresholds["arms_crossed_for_3_sec_count"] * 2 else
    #     1
    # )

    # # FACIAL EXPRESSION
    # happy = facial_expression_score.get("happy", 0)
    # sad_fear = facial_expression_score.get("sad", 0) + facial_expression_score.get("fear", 0)

    # facial_score = (
    #     5 if happy >= 20 and sad_fear < 5 else
    #     3 if happy >= 10 or sad_fear >= 5 else
    #     1
    # )

    # # FIDGETING
    # total_fidget = mouth_touches + nose_touches + eye_touches + ear_touches + neck_touches + hand_on_hip
    # fidget_score = (
    #     5 if total_fidget <= abnormal_thresholds["mouth_touch_count"] * 2 else
    #     3 if total_fidget <= abnormal_thresholds["mouth_touch_count"] * 3 else
    #     1
    # )

    # # BPM CONTROL
    # bpm_score = (
    #     5 if bpm <= abnormal_thresholds["final_bpm"] else
    #     3 if bpm <= abnormal_thresholds["final_bpm"] + 10 else
    #     1
    # )

    # # TOTAL SCORE
    # category_scores = {
    #     "stance": stance_score,
    #     "eye_contact": eye_score,
    #     "gestures": gesture_score,
    #     "facial_expression": facial_score,
    #     "fidgeting": fidget_score,
    #     "bpm_control": bpm_score
    # }

    # total_score = sum(category_scores.values())
    # average_score = round(total_score / len(category_scores), 2)

    # return {
    #     "rubric_scores": category_scores,
    #     "total_score": total_score,
    #     "average_score": average_score,
    #     "rating": (
    #         "Excellent" if average_score >= 4.5 else
    #         "Good" if average_score >= 3.0 else
    #         "Needs Improvement"
    #     ),
    #     "graded_per": (
    #         "1 min" if strictness == 1 else
    #         "30 sec" if strictness == 2 else
    #         "15 sec"
    #     ),
    # }
