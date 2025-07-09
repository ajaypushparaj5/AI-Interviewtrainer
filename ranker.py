def rank_user_behavior(results, emotion_stats):
    comments = []
    rubric_scores = {}

    duration_sec = results.get("duration_sec", 60)
    duration_min = max(duration_sec / 60, 1) 

    # 1. STANCE
    if results.get("posture_warnings") == "Slouching detected":
        stance_score = 1
        comments.append("Slouching observed — posture detracted from message.")
    else:
        stance_score = 5
        comments.append("Good posture — stable stance throughout.")
    rubric_scores["stance"] = stance_score

    # 2. EYE CONTACT
    eye_breaks = results.get("eye_contact_breaks", 0)
    eye_break_rate = eye_breaks / duration_min

    if eye_break_rate > 15:
        eye_score = 1
        comments.append("Very limited or distracted eye contact.")
    elif eye_break_rate > 7:
        eye_score = 3
        comments.append("Inconsistent eye contact — frequent looking away.")
    else:
        eye_score = 5
        comments.append("Consistent and appropriate eye contact.")
    rubric_scores["eye_contact"] = eye_score

    # === 3. FACIAL EXPRESSION ===
    happy = emotion_stats.get("happy", 0)
    sad_fear = emotion_stats.get("sad", 0) + emotion_stats.get("fear", 0)

    if happy >= 20 and sad_fear < 5:
        face_score = 5
        comments.append("Facial expressions were consistent and positive.")
    elif happy >= 10 or sad_fear >= 5:
        face_score = 3
        comments.append("Facial expressions were present but inconsistent.")
    else:
        face_score = 1
        comments.append("Very few or flat facial expressions observed.")
    rubric_scores["facial_expression"] = face_score

    # 4. GESTURES 
    total_touches = sum([
        results.get('mouth_touch_count', 0),
        results.get('nose_touch_count', 0),
        results.get('eye_touch_count', 0),
        results.get('ear_touch_count', 0),
        results.get('neck_touch_count', 0)
    ])
    touch_rate = total_touches / duration_min

    if touch_rate > 6:
        gesture_score = 1
        comments.append("Distracting or fidgety gestures throughout.")
    elif 2 <= touch_rate <= 6:
        gesture_score = 3
        comments.append("Some purposeful gestures, mixed with nervous ones.")
    else:
        gesture_score = 5
        comments.append("Gestures were purposeful and minimal.")
    rubric_scores["gestures"] = gesture_score

    # Final Rank 
    scores = list(rubric_scores.values())
    count_1 = scores.count(1)
    count_3_or_5 = sum(1 for s in scores if s in [3, 5])

    if count_1 >= 2:
        rank = "Needs Improvement"
    elif all(s == 5 for s in scores):
        rank = "Excellent"
    elif count_3_or_5 >= 3:
        rank = "Good"
    else:
        rank = "Average"

    return {
        "rubric_scores": rubric_scores,
        "rank": rank,
        "comments": comments
    }
