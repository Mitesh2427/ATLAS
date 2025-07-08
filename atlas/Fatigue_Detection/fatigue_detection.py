# Integrated Fatigue Detection System
# (Speech-free, drowsiness-removed, fatigue-only scoring + counters + mouth-open logic)

import cv2
import time
import numpy as np
from utils import get_landmarks, eye_aspect_ratio, mouth_aspect_ratio
import mediapipe as mp

# Constants
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
UPDATE_INTERVAL = 10  # seconds
MOUTH_OPEN_THRESHOLD = 0.45
MOUTH_OPEN_TIME_MIN = 1.0
MOUTH_OPEN_TIME_MAX = 1.2

def calibrate_user(seconds=20):
    """Calibrate thresholds based on the individual user's baseline metrics."""
    ear_values = []
    mar_values = []
    head_movements = []
    blink_count = 0
    last_ear = None
    last_nose = None
    
    print("Calibration phase. Please look naturally at the screen...")
    calibration_start = time.time()
    
    while time.time() - calibration_start < seconds:
        ret, frame = cap.read()
        if not ret:
            continue
            
        frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        landmarks = get_landmarks(rgb_frame)
        if landmarks:
            ear = eye_aspect_ratio(landmarks, FRAME_WIDTH, FRAME_HEIGHT)
            mar = mouth_aspect_ratio(landmarks, FRAME_WIDTH, FRAME_HEIGHT)
            
            # Record metrics
            ear_values.append(ear)
            mar_values.append(mar)
            
            # Detect blinks for calibration
            if last_ear is not None:
                if last_ear > 0.25 and ear < 0.25:
                    blink_count += 1
            last_ear = ear
            
            # Track head movement
            nose = landmarks.landmark[1]
            nose_pos = (nose.x, nose.y)
            if last_nose is not None:
                dx = abs(nose_pos[0] - last_nose[0])
                dy = abs(nose_pos[1] - last_nose[1])
                head_movements.append(max(dx, dy))
            last_nose = nose_pos
            
        # Display calibration countdown
        cv2.putText(frame, f"Calibrating: {int(seconds - (time.time() - calibration_start))}s", 
                   (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(frame, "Please look naturally at the screen", 
                   (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow("Calibration", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    
    # Calculate personalized thresholds
    ear_threshold = 0.21  # Default
    mar_threshold = 0.7   # Default
    normal_blink_rate = 15  # Default blinks per minute
    normal_head_movement = 0.01  # Default
    
    if ear_values:
        # Sort and filter outliers
        ear_values.sort()
        filtered_ear = ear_values[int(len(ear_values) * 0.1):int(len(ear_values) * 0.9)]
        normal_ear = sum(filtered_ear) / len(filtered_ear)
        ear_threshold = normal_ear * 0.7  # 70% of normal as threshold
    
    if mar_values:
        # Sort and filter outliers
        mar_values.sort()
        filtered_mar = mar_values[int(len(mar_values) * 0.1):int(len(mar_values) * 0.9)]
        normal_mar = sum(filtered_mar) / len(filtered_mar)
        mar_threshold = normal_mar * 1.5  # 150% of normal as yawn threshold
    
    if head_movements:
        head_movements.sort()
        filtered_head = head_movements[0:int(len(head_movements) * 0.9)]  # Ignore top 10%
        normal_head_movement = sum(filtered_head) / len(filtered_head)
    
    if seconds > 10:  # Only if calibration was long enough
        normal_blink_rate = (blink_count / seconds) * 60
    
    print(f"Calibration complete:")
    print(f"- EAR threshold: {ear_threshold:.3f}")
    print(f"- MAR threshold: {mar_threshold:.3f}")
    print(f"- Normal blink rate: {normal_blink_rate:.1f} blinks/min")
    print(f"- Normal head movement: {normal_head_movement:.5f}")
    
    return ear_threshold, mar_threshold, normal_blink_rate, normal_head_movement

# Initialize capture
cap = cv2.VideoCapture(0)

# Initialize Mediapipe hands for face touching
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5)

# Run calibration (same as your existing calibrate_user function)
EAR_THRESHOLD, MAR_THRESHOLD, NORMAL_BLINK_RATE, NORMAL_HEAD_MOVEMENT = calibrate_user()
BLINK_FATIGUE_THRESHOLD = min(35, NORMAL_BLINK_RATE * 1.6)
HEAD_FATIGUE_THRESHOLD = NORMAL_HEAD_MOVEMENT * 2.0
FACE_TOUCH_FATIGUE_THRESHOLD = 5

# Runtime variables
blink_counter = 0
head_move_counter = 0
face_touch_counter = 0
fatigue_blink_counter = 0
fatigue_head_counter = 0
fatigue_face_counter = 0
fatigue_yawn_counter = 0
fatigue_mouth_open_counter = 0

last_ear, last_nose = None, None
mouth_open_start = None

# Rolling history
blink_history = []
head_history = []
face_touch_history = []
ear_history, mar_history = [], []

start_time = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    current_time = time.time()
    frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    landmarks = get_landmarks(rgb)
    if not landmarks:
        cv2.putText(frame, "No Face Detected", (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        cv2.imshow("Fatigue Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        continue

    # EAR & MAR
    ear = eye_aspect_ratio(landmarks, FRAME_WIDTH, FRAME_HEIGHT)
    mar = mouth_aspect_ratio(landmarks, FRAME_WIDTH, FRAME_HEIGHT)

    ear_history.append(ear)
    mar_history.append(mar)
    if len(ear_history) > 5:
        ear_history.pop(0)
        mar_history.pop(0)

    smoothed_ear = sum(ear_history) / len(ear_history)
    smoothed_mar = sum(mar_history) / len(mar_history)

    # Mouth open duration
    if smoothed_mar > MOUTH_OPEN_THRESHOLD:
        if mouth_open_start is None:
            mouth_open_start = current_time
        mouth_open_duration = current_time - mouth_open_start
        if MOUTH_OPEN_TIME_MIN <= mouth_open_duration <= MOUTH_OPEN_TIME_MAX:
            fatigue_mouth_open_counter += 1
            mouth_open_start = None  # Reset after counting
    else:
        mouth_open_start = None

    # Blink detection
    if last_ear and last_ear > EAR_THRESHOLD and ear < EAR_THRESHOLD:
        blink_counter += 1
        fatigue_blink_counter += 1
    last_ear = ear

    # Head movement
    nose = landmarks.landmark[1]
    dx, dy = 0, 0
    if last_nose:
        dx = abs(nose.x - last_nose[0])
        dy = abs(nose.y - last_nose[1])
        if max(dx, dy) > NORMAL_HEAD_MOVEMENT * 1.5:
            head_move_counter += 1
            fatigue_head_counter += 1
    last_nose = (nose.x, nose.y)

    # Face touch detection using Mediapipe Hands
    hand_results = hands.process(rgb)
    face_touched = False
    if hand_results.multi_hand_landmarks:
        for hand_landmarks in hand_results.multi_hand_landmarks:
            for point in hand_landmarks.landmark:
                hand_x, hand_y = int(point.x * FRAME_WIDTH), int(point.y * FRAME_HEIGHT)
                if FRAME_WIDTH//3 < hand_x < FRAME_WIDTH*2//3 and FRAME_HEIGHT//4 < hand_y < FRAME_HEIGHT*3//4:
                    face_touched = True
                    break
            if face_touched:
                break

    if face_touched:
        face_touch_counter += 1
        fatigue_face_counter += 1
        cv2.putText(frame, "FACE TOUCH", (FRAME_WIDTH - 180, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (230, 100, 200), 2)

    # Yawning detection
    if mar > MAR_THRESHOLD:
        fatigue_yawn_counter += 1

    # Update every 10s
    elapsed = current_time - start_time
    if elapsed > UPDATE_INTERVAL:
        blink_rate = blink_counter / (elapsed / 60.0)
        head_rate = head_move_counter / (elapsed / 60.0)
        face_touch_rate = face_touch_counter / (elapsed / 60.0)

        blink_history.append(blink_rate)
        head_history.append(head_rate)
        face_touch_history.append(face_touch_rate)

        if len(blink_history) > 3:
            blink_history.pop(0)
            head_history.pop(0)
            face_touch_history.pop(0)

        blink_counter = head_move_counter = face_touch_counter = 0
        start_time = current_time

    # === Fatigue Scoring System ===
    fatigue_score = 0
    fatigue_score += 1 if fatigue_blink_counter >= 5 else 0
    fatigue_score += 1 if fatigue_head_counter >= 5 else 0
    fatigue_score += 1 if fatigue_face_counter >= 5 else 0
    fatigue_score += 1 if fatigue_yawn_counter >= 5 else 0
    fatigue_score += 1 if fatigue_mouth_open_counter >= 5 else 0

    fatigue_level = min(5, fatigue_score)
    label = f"Fatigue Level: {fatigue_level}/5"
    if fatigue_level == 5:
        label += " - FATIGUED"

    # === Display ===
    cv2.putText(frame, label, (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                (0, 0, 255) if fatigue_level >= 4 else (0, 165, 255), 2)
    cv2.putText(frame, f"EAR: {smoothed_ear:.2f}", (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 180), 2)
    cv2.putText(frame, f"MAR: {smoothed_mar:.2f}", (30, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 180), 2)
    cv2.putText(frame, f"Mouth Opens: {fatigue_mouth_open_counter}", (30, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 200, 255), 2)
    cv2.putText(frame, f"Yawns: {fatigue_yawn_counter}", (30, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 100, 255), 2)
    cv2.putText(frame, f"Fatigue Blinks: {fatigue_blink_counter}", (30, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 204, 0), 2)
    cv2.putText(frame, f"Head Moves: {fatigue_head_counter}", (30, 210), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 100, 180), 2)
    cv2.putText(frame, f"Face Touches: {fatigue_face_counter}", (30, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (230, 100, 200), 2)

    cv2.imshow("Fatigue Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
hands.close()