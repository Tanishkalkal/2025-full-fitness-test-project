import cv2
import mediapipe as mp
import numpy as np

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils


def calculate_angle(a, b, c):
    """Calculate angle between three points"""
    a = np.array([a.x, a.y])
    b = np.array([b.x, b.y])
    c = np.array([c.x, c.y])

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle


def pushup_counter(video_path, output_path="pushup_output.mp4"):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise FileNotFoundError(f"❌ Cannot open {video_path}")

    # Output video writer
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    fps = int(cap.get(cv2.CAP_PROP_FPS) or 20)
    width, height = int(cap.get(3)), int(cap.get(4))
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    pushup_count = 0
    direction = None  # "down" or "up"

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb)

        if results.pose_landmarks:
            lm = results.pose_landmarks.landmark

            # Get landmarks for LEFT arm
            shoulder = lm[mp_pose.PoseLandmark.LEFT_SHOULDER]
            elbow = lm[mp_pose.PoseLandmark.LEFT_ELBOW]
            wrist = lm[mp_pose.PoseLandmark.LEFT_WRIST]

            # Calculate elbow angle
            angle = calculate_angle(shoulder, elbow, wrist)

            # Push-up logic
            if angle < 90:   # Going down
                direction = "down"
            elif angle > 160 and direction == "down":  # Coming up
                pushup_count += 1
                direction = "up"

            # Draw pose
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            # Show counter
            cv2.putText(frame, f"Push-ups: {pushup_count}", (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        out.write(frame)

    cap.release()
    out.release()
    pose.close()

    print("✅ Push-up Detection Done!")
    print("Total Push-ups:", pushup_count)
    # Return count and the actual output path so app can serve it
    return pushup_count, output_path
