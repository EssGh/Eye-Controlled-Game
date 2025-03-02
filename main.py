import cv2
import mediapipe as mp
import numpy as np

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]
LEFT_IRIS = [468, 469, 470, 471, 472]
RIGHT_IRIS = [473, 474, 475, 476, 477]

BLINK_THRESHOLD = 0.25


def calculate_ear(landmarks, eye_indices):
    eye = np.array([landmarks[i] for i in eye_indices])

    vertical1 = np.linalg.norm(eye[1] - eye[5])
    vertical2 = np.linalg.norm(eye[2] - eye[4])
    vertical = vertical1 + vertical2
    horizontal = 2.0 * np.linalg.norm(eye[0] - eye[3])

    ear = vertical / horizontal
    return ear


def get_iris_center(landmarks, iris_indices, frame_width, frame_height):
    iris = np.array([(landmarks[i].x * frame_width, landmarks[i].y * frame_height) for i in iris_indices])
    center = np.mean(iris, axis=0).astype(int)
    return tuple(center)


def get_gaze_direction(iris_center, eye_rect, threshold=0.15):
    x, y, w, h = eye_rect
    eye_center = (x + w // 2, y + h // 2)
    dx = iris_center[0] - eye_center[0]
    dy = iris_center[1] - eye_center[1]

    nx = dx / w
    ny = dy / h

    direction = ""
    if nx < -threshold:
        direction += "Left "
    elif nx > threshold:
        direction += "Right "

    if ny < -threshold:
        direction += "Up"
    elif ny > threshold:
        direction += "Down"

    return direction.strip() if direction else "Center"

cap = cv2.VideoCapture(0)
while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        face_landmarks = results.multi_face_landmarks[0]
        frame_height, frame_width = frame.shape[:2]

        landmarks = [(int(lm.x * frame_width), int(lm.y * frame_height)) for lm in face_landmarks.landmark]
        left_ear = calculate_ear(landmarks, LEFT_EYE)
        right_ear = calculate_ear(landmarks, RIGHT_EYE)

        if left_ear < BLINK_THRESHOLD and right_ear < BLINK_THRESHOLD:
            status, color = "Both Eyes Closed", (0, 0, 255)
        elif left_ear < BLINK_THRESHOLD:
            status, color = "Left Eye Closed", (0, 255, 0)
        elif right_ear < BLINK_THRESHOLD:
            status, color = "Right Eye Closed", (0, 255, 0)
        else:
            status, color = "Eyes Open", (255, 255, 255)

        cv2.putText(frame, status, (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        for eye_indices, iris_indices in zip([LEFT_EYE, RIGHT_EYE], [LEFT_IRIS, RIGHT_IRIS]):
            eye_points = np.array([landmarks[i] for i in eye_indices], np.int32)
            x, y, w, h = cv2.boundingRect(eye_points)

            iris_center = get_iris_center(face_landmarks.landmark, iris_indices, frame_width, frame_height)
            cv2.circle(frame, iris_center, 3, (0, 255, 0), -1)

            gaze_direction = get_gaze_direction(iris_center, (x, y, w, h))

            cv2.putText(frame, gaze_direction, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            #cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 1)

        for idx in LEFT_EYE + RIGHT_EYE:
            cv2.circle(frame, landmarks[idx], 1, (0, 255, 255), -1)

    cv2.imshow('Eye and Pupil Tracking', frame)
    if cv2.waitKey(5) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()