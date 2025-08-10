
import cv2
import mediapipe as mp
import time
import math


def coords(lm,shape):
    return mp.solutions.drawing_utils._normalized_to_pixel_coordinates(lm.x, lm.y, shape[1], shape[0])

# def display_pose(rgb_frame, results):
#     if not results or not results.landmark:
#         return rgb_frame

#     h, w, _ = rgb_frame.shape
#     lm = results.landmark

#     lx, ly = int(lm[11].x * w), int(lm[11].y * h)
#     rx, ry = int(lm[12].x * w), int(lm[12].y * h)

#     cv2.circle(rgb_frame, (lx, ly), 8, (255, 0, 0), -1)
#     cv2.circle(rgb_frame, (rx, ry), 8, (255, 0, 0), -1)
#     cv2.line(rgb_frame, (lx, ly), (rx, ry), (0, 255, 0), 2)
#     for idx in [13,14,15,16]:
#         p=coords(lm[idx], rgb_frame.shape)
#         if p:
#             cv2.circle(rgb_frame, p, 6, (255, 0, 0), -1)
            
#     ls = lm[11]
#     rs = lm[12]
#     lh = lm[23]
#     rh = lm[24]
    
#     x1 = int((min(ls.x, rs.x) + 0.05) * w)
#     x2 = int((max(ls.x, rs.x) - 0.05) * w)
#     y1 = int(min(ls.y, rs.y) * h) + 10
#     y2 = int(max(lh.y, rh.y) * h) - 10

#     cv2.rectangle(rgb_frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

#     return rgb_frame


def display_pose(rgb_frame, results):
    if not results or not results.landmark:
        return rgb_frame

    h, w, _ = rgb_frame.shape
    lm = results.landmark

    # Draw shoulder points and line
    lx, ly = int(lm[11].x * w), int(lm[11].y * h)
    rx, ry = int(lm[12].x * w), int(lm[12].y * h)

    cv2.circle(rgb_frame, (lx, ly), 8, (255, 0, 0), -1)
    cv2.circle(rgb_frame, (rx, ry), 8, (255, 0, 0), -1)
    cv2.line(rgb_frame, (lx, ly), (rx, ry), (0, 255, 0), 2)
    
    # Draw arm joints (elbows and wrists)
    for idx in [13, 14, 15, 16]:
        p = coords(lm[idx], rgb_frame.shape)
        if p:
            cv2.circle(rgb_frame, p, 6, (255, 0, 0), -1)
    
    # Original torso rectangle (red)
    ls = lm[11]  # Left shoulder
    rs = lm[12]  # Right shoulder
    lh = lm[23]  # Left hip
    rh = lm[24]  # Right hip
    
    x1 = int((min(ls.x, rs.x) + 0.05) * w)
    x2 = int((max(ls.x, rs.x) - 0.05) * w)
    y1 = int(min(ls.y, rs.y) * h) + 10
    y2 = int(max(lh.y, rh.y) * h) - 10

    cv2.rectangle(rgb_frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
    
    # Add gesture box
    shoulder_width = abs(rs.x - ls.x)
    torso_height = abs(ls.y - lh.y)
    
    # Gesture box thresholds 
    horizontal_threshold = 0.15
    vertical_threshold = 0.1
    
    # Calculate gesture box boundaries
    gesture_left = int((ls.x - (horizontal_threshold * shoulder_width)) * w)
    gesture_right = int((rs.x + (horizontal_threshold * shoulder_width)) * w)
    gesture_top = int((ls.y - (vertical_threshold * torso_height)) * h)
    gesture_bottom = int((lh.y + (vertical_threshold * torso_height)) * h)
    
    # Draw gesture box 
    cv2.rectangle(rgb_frame, (gesture_left, gesture_top), (gesture_right, gesture_bottom), (255, 255, 0), 2)
    
    return rgb_frame


def slouch_detector(rgb_frame, results, lastslouch):
    if not results:
        return False, lastslouch

    h, _, _ = rgb_frame.shape
    landmarks = results.landmark

    left_shoulder = landmarks[11]
    right_shoulder = landmarks[12]

    ly = int(left_shoulder.y * h)
    ry = int(right_shoulder.y * h)

    current = time.time()


    if current - lastslouch >= 4:
        if abs(ly - ry) > 20:  
            lastslouch = current
            return True, lastslouch

    return False, lastslouch

    
# def arms_crossed_detector(results, lastcrossed, angle_threshold=25):

#     if not results or not hasattr(results, 'landmark'):
#         return False, lastcrossed
    
#     current_time = time.time()
#     lm = results.landmark
    
#     left_elbow = lm[13]
#     right_elbow = lm[14]
#     left_wrist = lm[15]
#     right_wrist = lm[16]
    
#     def is_horizontal(p1, p2, threshold_deg):
#         dx = abs(p2.x - p1.x)
#         dy = abs(p2.y - p1.y)
#         if dx == 0:  
#             return False
#         angle = math.degrees(math.atan(dy / dx))
#         return angle <= threshold_deg
    
#     left_horizontal = is_horizontal(left_elbow, left_wrist, angle_threshold)
#     right_horizontal = is_horizontal(right_elbow, right_wrist, angle_threshold)
    
#     wrist_inside = abs(left_wrist.x - right_wrist.x) < abs(left_elbow.x - right_elbow.x) 
     
#     if (left_horizontal or right_horizontal) and wrist_inside:
#         if current_time - lastcrossed > 1:
#             lastcrossed = current_time
#             return True, lastcrossed
    
#     return False, lastcrossed    
    
def arms_crossed_detector(results, crossed_start_time, angle_threshold=25):
    if not results or not hasattr(results, 'landmark'):
        return False, 0  # Reset if no pose
    
    current_time = time.time()
    lm = results.landmark
    
    left_elbow = lm[13]
    right_elbow = lm[14]
    left_wrist = lm[15]
    right_wrist = lm[16]
    
    def is_horizontal(p1, p2, threshold_deg):
        dx = abs(p2.x - p1.x)
        dy = abs(p2.y - p1.y)
        if dx == 0:  
            return False
        angle = math.degrees(math.atan(dy / dx))
        return angle <= threshold_deg
    
    # Check if currently crossed
    left_horizontal = is_horizontal(left_elbow, left_wrist, angle_threshold)
    right_horizontal = is_horizontal(right_elbow, right_wrist, angle_threshold)
    wrist_inside = abs(left_wrist.x - right_wrist.x) < abs(left_elbow.x - right_elbow.x) 
    
    currently_crossed = (left_horizontal or right_horizontal) and wrist_inside
    
    if currently_crossed:
        if crossed_start_time == 0:
            # Just started crossing
            return False, current_time
        elif current_time - crossed_start_time >= 3.0:
            # Been crossing for 3+ seconds
            return True, 0  # Reset after detection
        else:
            # Still crossing but not 3 seconds yet
            return False, crossed_start_time
    else:
        # Not crossing - reset
        return False, 0
    


# def hands_outside_gesture_box(results, last_outside, 
#                             horizontal_threshold=0.15, 
#                             vertical_threshold=0.1, 
#                             duration_threshold=0.8):
#     """
#     Detects if hands are outside the gesture box (shoulder to hip area).
    
#     Args:
#         results: MediaPipe pose detection results
#         last_outside: timestamp of last detection
#         horizontal_threshold: extra margin beyond shoulders (0.15 = 15% of shoulder width)
#         vertical_threshold: extra margin beyond shoulder-hip height (0.1 = 10% of torso height)
#         duration_threshold: minimum time hands must be outside before triggering
    
#     Returns:
#         tuple: (is_outside_detected, updated_last_outside_time)
#     """
    
#     if not results or not hasattr(results, 'landmark'):
#         return False, last_outside
    
#     current_time = time.time()
#     lm = results.landmark
    
#     # Get key body landmarks
#     left_shoulder = lm[11]   # Left shoulder
#     right_shoulder = lm[12]  # Right shoulder
#     left_hip = lm[23]        # Left hip
#     right_hip = lm[24]       # Right hip
#     left_wrist = lm[15]      # Left wrist
#     right_wrist = lm[16]     # Right wrist
    
#     # Calculate gesture box boundaries with lenient thresholds
#     shoulder_width = abs(right_shoulder.x - left_shoulder.x)
#     torso_height = abs(left_shoulder.y - left_hip.y)  # Using left side as reference
    
#     # Box boundaries (with lenient margins)
#     left_boundary = left_shoulder.x - (horizontal_threshold * shoulder_width)
#     right_boundary = right_shoulder.x + (horizontal_threshold * shoulder_width)
#     top_boundary = left_shoulder.y - (vertical_threshold * torso_height)  # Above shoulders
#     bottom_boundary = left_hip.y + (vertical_threshold * torso_height)    # Below hips
    
#     # Check if hands are outside the gesture box
#     left_hand_outside = (left_wrist.x < left_boundary or 
#                         left_wrist.x > right_boundary or
#                         left_wrist.y < top_boundary or 
#                         left_wrist.y > bottom_boundary)
    
#     right_hand_outside = (right_wrist.x < left_boundary or 
#                          right_wrist.x > right_boundary or
#                          right_wrist.y < top_boundary or 
#                          right_wrist.y > bottom_boundary)
    
#     # Trigger detection if either hand is significantly outside
#     hands_outside = left_hand_outside or right_hand_outside
    
#     if hands_outside:
#         if current_time - last_outside > duration_threshold:
#             last_outside = current_time
#             return True, last_outside
    
#     return False, last_outside

# def hands_outside_gesture_box(results, outside_frames, total_frames, 
#                              horizontal_threshold=0.40, 
#                              vertical_threshold=0.1):
#     """
#     Detects if hands are outside the gesture box (shoulder to hip area) and tracks percentage.
    
#     Args:
#         results: MediaPipe pose detection results
#         outside_frames: Current count of frames with hands outside
#         total_frames: Total frames processed
#         horizontal_threshold: extra margin beyond shoulders (0.15 = 15% of shoulder width)
#         vertical_threshold: extra margin beyond shoulder-hip height (0.1 = 10% of torso height)
    
#     Returns:
#         tuple: (outside_frames, total_frames, outside_percentage, currently_outside)
#     """
#     total_frames += 1
    
#     if not results or not hasattr(results, 'landmark'):
#         outside_percentage = (outside_frames / total_frames) * 100
#         return outside_frames, total_frames, outside_percentage, False
    
#     lm = results.landmark
    
#     # Get key body landmarks
#     left_shoulder = lm[11]   # Left shoulder
#     right_shoulder = lm[12]  # Right shoulder
#     left_hip = lm[23]        # Left hip
#     right_hip = lm[24]       # Right hip
#     left_wrist = lm[15]      # Left wrist
#     right_wrist = lm[16]     # Right wrist
    
#     # Calculate gesture box boundaries
#     shoulder_width = abs(right_shoulder.x - left_shoulder.x)
#     torso_height = abs(left_shoulder.y - left_hip.y)
    
#     # Box boundaries (with margins)
#     left_boundary = left_shoulder.x - (horizontal_threshold * shoulder_width)
#     right_boundary = right_shoulder.x + (horizontal_threshold * shoulder_width)
#     top_boundary = left_shoulder.y - (vertical_threshold * torso_height)
#     bottom_boundary = left_hip.y + (vertical_threshold * torso_height)
    
#     # Check if hands are outside the gesture box
#     left_hand_outside = (left_wrist.x < left_boundary or 
#                         left_wrist.x > right_boundary or
#                         left_wrist.y < top_boundary or 
#                         left_wrist.y > bottom_boundary)
    
#     right_hand_outside = (right_wrist.x < left_boundary or 
#                          right_wrist.x > right_boundary or
#                          right_wrist.y < top_boundary or 
#                          right_wrist.y > bottom_boundary)
    
#     # Check if either hand is outside
#     hands_currently_outside = left_hand_outside or right_hand_outside
    
#     # Increment counter if hands are outside
#     if hands_currently_outside:
#         outside_frames += 1
    
#     outside_percentage = (outside_frames / total_frames) * 100
    
#     return outside_frames, total_frames, outside_percentage, hands_currently_outside


def hands_outside_gesture_box(results, outside_frames, total_frames, 
                              horizontal_threshold=0.40, 
                              vertical_threshold=0.1):
    """
    Detects if hands are outside the gesture box (shoulder to hip area) and tracks percentage.
    
    Args:
        results: MediaPipe pose detection results
        outside_frames: Current count of frames with hands outside
        total_frames: Total frames processed
        horizontal_threshold: extra margin beyond shoulders (0.15 = 15% of shoulder width)
        vertical_threshold: extra margin beyond shoulder-hip height (0.1 = 10% of torso height)
    
    Returns:
        tuple: (outside_frames, total_frames, outside_percentage, currently_outside, gesture_box_coords)
               gesture_box_coords: (left_x, top_y, right_x, bottom_y) for drawing
    """
    
    # Increment total frames at the very beginning of the function
    total_frames += 1
    
    # Initialize currently_outside to False and gesture_box_coords to None
    currently_outside = False

    if not results or not hasattr(results, 'landmark'): # Check for pose_landmarks attribute
        # If no landmarks detected, calculate percentage based on previous counts
        outside_percentage = (outside_frames / total_frames) * 100 if total_frames > 0 else 0
        return outside_frames, total_frames, outside_percentage, currently_outside
    
    lm = results.landmark # Access landmarks through pose_landmarks
    
    # Get key body landmarks. MediaPipe landmarks are normalized [0, 1].
    # We need to convert them to pixel coordinates later for drawing.
    left_shoulder = lm[11]   # Left shoulder
    right_shoulder = lm[12]  # Right shoulder
    left_hip = lm[23]        # Left hip
    right_hip = lm[24]       # Right hip
    left_wrist = lm[15]      # Left wrist
    right_wrist = lm[16]     # Right wrist
    
    # Calculate gesture box boundaries (normalized coordinates)
    shoulder_width = abs(right_shoulder.x - left_shoulder.x)
    torso_height = abs(left_shoulder.y - left_hip.y)
    
    # Box boundaries (with margins)
    # Ensure min/max for boundary calculations to prevent inverted boxes
    left_boundary = min(left_shoulder.x, right_shoulder.x) - (horizontal_threshold * shoulder_width)
    right_boundary = max(left_shoulder.x, right_shoulder.x) + (horizontal_threshold * shoulder_width)
    top_boundary = min(left_shoulder.y, right_shoulder.y) - (vertical_threshold * torso_height)
    bottom_boundary = max(left_hip.y, right_hip.y) + (vertical_threshold * torso_height)

    # Store normalized gesture box coordinates for later drawing
    
    # Check if hands are outside the gesture box
    left_hand_outside = (left_wrist.x < left_boundary or 
                         left_wrist.x > right_boundary or
                         left_wrist.y < top_boundary or 
                         left_wrist.y > bottom_boundary)
    
    right_hand_outside = (right_wrist.x < left_boundary or 
                          right_wrist.x > right_boundary or
                          right_wrist.y < top_boundary or 
                          right_wrist.y > bottom_boundary)
    
    # Check if either hand is outside
    hands_currently_outside = left_hand_outside or right_hand_outside
    
    # Increment counter if hands are outside
    if hands_currently_outside:
        outside_frames += 1
    
    outside_percentage = (outside_frames / total_frames) * 100
    
    return outside_frames, total_frames, outside_percentage, hands_currently_outside




def detect_upperbody_swaying(pose_landmarks, sway_frames, total_frames, movement_threshold=0.01):
    total_frames += 1

    if not pose_landmarks:
        return sway_frames, total_frames, (sway_frames / total_frames) * 100
    
    lm = pose_landmarks.landmark
    left_shoulder = lm[11]
    right_shoulder = lm[12]
    nose = lm[0]

    spine_center_x = (left_shoulder.x + right_shoulder.x) / 2
    spine_center_y = (left_shoulder.y + right_shoulder.y) / 2

    if not hasattr(detect_upperbody_swaying, 'positions'):
        detect_upperbody_swaying.positions = []

    current_position = (spine_center_x, spine_center_y, nose.x)
    detect_upperbody_swaying.positions.append(current_position)

    if len(detect_upperbody_swaying.positions) > 10:
        detect_upperbody_swaying.positions.pop(0)

    is_swaying = False
    if len(detect_upperbody_swaying.positions) >= 5:
        positions = detect_upperbody_swaying.positions
        spine_x_positions = [pos[0] for pos in positions]
        head_x_positions = [pos[2] for pos in positions]
        spine_movement = max(spine_x_positions) - min(spine_x_positions)
        head_movement = max(head_x_positions) - min(head_x_positions)
        is_swaying = spine_movement > movement_threshold or head_movement > movement_threshold

    if is_swaying:
        sway_frames += 1

    sway_percentage = (sway_frames / total_frames) * 100
    return sway_frames, total_frames, sway_percentage

def hands_clenched_detector(results, last_clenched, distance_threshold=0.1):
    current_time=time.time()
    if not results:
        return False, last_clenched

    lm = results.landmark

    left_wrist = lm[15]
    right_wrist = lm[16]

    wrist_distance = math.sqrt(
        (left_wrist.x - right_wrist.x) ** 2 +
        (left_wrist.y - right_wrist.y) ** 2
    )

    if wrist_distance < distance_threshold:
        if last_clenched == 0:
            return False, current_time
        elif current_time - last_clenched >= 3:
            return True, 0
        else:
            return False, last_clenched
    else:
        return False, 0

    


def hands_behind_back_detector(results, last_behind, visibility_threshold=0.3):

    if not results or not hasattr(results, 'landmark'):
        return False, last_behind
    
    current_time = time.time()
    lm = results.landmark
    
    left_wrist = lm[15]
    right_wrist = lm[16]
    left_elbow = lm[13]
    right_elbow = lm[14]
    
    # Check if hands have low visibility (indicating they're obscured/behind body)
    hands_hidden = (left_wrist.visibility < visibility_threshold and 
                   right_wrist.visibility < visibility_threshold)
    
    # Elbows should be more visible and positioned behind shoulders
    left_shoulder = lm[11]
    right_shoulder = lm[12]
    
    elbows_behind = (left_elbow.x < left_shoulder.x and 
                    right_elbow.x > right_shoulder.x)
    
    # Arms should be angled backward
    left_arm_back = left_elbow.x < left_shoulder.x
    right_arm_back = right_elbow.x > right_shoulder.x
    
    if hands_hidden and elbows_behind and left_arm_back and right_arm_back:
        if current_time - last_behind > 1:
            last_behind = current_time
            return True, last_behind
    
    return False, last_behind


def hands_in_pockets_detector(results, last_pockets, y_threshold_ratio=0.7, visibility_threshold=0.4):

    if not results or not hasattr(results, 'landmark'):
        return False, last_pockets
    
    current_time = time.time()
    lm = results.landmark
    
    left_wrist = lm[15]
    right_wrist = lm[16]
    left_hip = lm[23]
    right_hip = lm[24]
    left_shoulder = lm[11]
    right_shoulder = lm[12]
    
    # Calculate hip level for pocket positioning
    hip_level = (left_hip.y + right_hip.y) / 2
    shoulder_level = (left_shoulder.y + right_shoulder.y) / 2
    torso_height = hip_level - shoulder_level
    
    # Hands should be at or below hip level
    left_hand_low = left_wrist.y >= (shoulder_level + torso_height * y_threshold_ratio)
    right_hand_low = right_wrist.y >= (shoulder_level + torso_height * y_threshold_ratio)
    
    # Hands should be close to body sides (within hip width)
    left_hand_side = abs(left_wrist.x - left_hip.x) < abs(left_hip.x - right_hip.x) * 0.5
    right_hand_side = abs(right_wrist.x - right_hip.x) < abs(left_hip.x - right_hip.x) * 0.5
    
    # Low visibility indicates hands might be partially obscured by pockets
    hands_partially_hidden = (left_wrist.visibility < visibility_threshold or 
                             right_wrist.visibility < visibility_threshold)
    
    # At least one hand should meet pocket criteria
    left_in_pocket = left_hand_low and left_hand_side
    right_in_pocket = right_hand_low and right_hand_side
    
    if (left_in_pocket or right_in_pocket) and hands_partially_hidden:
        if current_time - last_pockets > 1:
            last_pockets = current_time
            return True, last_pockets
    
    return False, last_pockets