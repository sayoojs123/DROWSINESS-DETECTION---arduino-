# Importing OpenCV Library for basic image processing functions
import cv2
# Numpy for array-related functions
import numpy as np
# Dlib for deep learning-based Modules and face landmark detection
import dlib
# face_utils for basic operations of conversion
from imutils import face_utils
import serial
import time

# Initialize serial connection to Arduino
s = serial.Serial('/dev/ttyACM0', 9600)  # Adjust the port as needed

# Initializing the camera and taking the instance
cap = cv2.VideoCapture(0)

# Initializing the face detector and landmark detector
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# Status tracking for the current state
sleep = 0
drowsy = 0
active = 0
status = ""
color = (0, 0, 0)
last_status = ""  # Track the last sent status

# Function to compute the Euclidean distance between two points
def compute(ptA, ptB):
    dist = np.linalg.norm(ptA - ptB)
    return dist

# Function to detect eye closure by comparing the distances between eye landmarks
def blinked(a, b, c, d, e, f):
    up = compute(b, d) + compute(c, e)
    down = compute(a, f)
    ratio = up / (2.0 * down)

    # Checking if the eyes are closed
    if (ratio > 0.25):
        return 2  # Eyes open
    elif (ratio > 0.21 and ratio <= 0.25):
        return 1  # Eyes partially closed
    else:
        return 0  # Eyes closed

# Main loop for video processing and blink detection
while True:
    _, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = detector(gray)
    face_frame = frame.copy()  # Copy frame for face landmark drawing

    for face in faces:
        x1 = face.left()
        y1 = face.top()
        x2 = face.right()
        y2 = face.bottom()

        cv2.rectangle(face_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        landmarks = predictor(gray, face)
        landmarks = face_utils.shape_to_np(landmarks)

        # The landmarks 36-47 correspond to the eyes
        left_blink = blinked(landmarks[36], landmarks[37],
                             landmarks[38], landmarks[41], landmarks[40], landmarks[39])
        right_blink = blinked(landmarks[42], landmarks[43],
                              landmarks[44], landmarks[47], landmarks[46], landmarks[45])

        # Check the eye status based on blink detection
        if (left_blink == 0 or right_blink == 0):  # Eyes closed
            sleep += 1
            drowsy = 0
            active = 0
            if (sleep > 6):
                status = "SLEEPING !!!"
                color = (255, 0, 0)

        elif (left_blink == 1 or right_blink == 1):  # Eyes partially closed
            sleep = 0
            active = 0
            drowsy += 1
            if (drowsy > 6):
                status = "Drowsy !"
                color = (0, 0, 255)

        else:  # Eyes open
            drowsy = 0
            sleep = 0
            active += 1
            if (active > 6):
                status = "Active :)"
                color = (0, 255, 0)

        # Send command to Arduino only when status changes
        if status != last_status:
            if status == "SLEEPING !!!":  # Trigger only on "Sleeping" status
                s.write(b'a')  # Send sleep alert to Arduino
            elif status == "Active :)":
                s.write(b'b')  # Send active alert to Arduino
            last_status = status  # Update last status

        # Display the status on the frame
        cv2.putText(frame, status, (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)

        # Draw eye landmarks for visualization
        for n in range(36, 48):  # Only draw around the eyes for efficiency
            (x, y) = landmarks[n]
            cv2.circle(face_frame, (x, y), 1, (255, 255, 255), -1)

    # Display the frames
    cv2.imshow("Frame", frame)
    cv2.imshow("Result of detector", face_frame)

    # Exit the loop if 'ESC' key is pressed
    key = cv2.waitKey(1)
    if key == 27:  # 27 is the 'ESC' key ASCII code
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
