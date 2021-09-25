import cv2
import mediapipe as mp
import socket
import numpy as np
import mido
import time
from mido import MidiFile

port = mido.open_output()

UDP_IP = "127.0.0.1"
UDP_PORT = 5065

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  #send packages


mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

# For static images:
IMAGE_FILES = []
BG_COLOR = (192, 192, 192)  # gray
with mp_pose.Pose( #with = try catch, put in context, automatically handles
        static_image_mode=True,
        model_complexity=2,
        enable_segmentation=True,
        min_detection_confidence=0.5) as pose:
    for idx, file in enumerate(IMAGE_FILES):
        image = cv2.imread(file)
        image_height, image_width, _ = image.shape
        # Convert the BGR image to RGB before processing.
        results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        if not results.pose_landmarks:
            continue
        print(
            f'Nose coordinates: ('
            f'{results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE].x * image_width}, '
            f'{results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE].y * image_height})'
        )

        annotated_image = image.copy()
        # Draw segmentation on the image.
        # To improve segmentation around boundaries, consider applying a joint
        # bilateral filter to "results.segmentation_mask" with "image".
        condition = np.stack((results.segmentation_mask,) * 3, axis=-1) > 0.1
        bg_image = np.zeros(image.shape, dtype=np.uint8)
        bg_image[:] = BG_COLOR
        annotated_image = np.where(condition, annotated_image, bg_image)
        # Draw pose landmarks on the image.
        mp_drawing.draw_landmarks(
            annotated_image,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
        cv2.imwrite('/tmp/annotated_image' + str(idx) + '.png', annotated_image)
        # Plot pose world landmarks.
        mp_drawing.plot_landmarks(
            results.pose_world_landmarks, mp_pose.POSE_CONNECTIONS)

left_already_down = False
right_already_down = False
count_kicks = 0
# For webcam input:
cap = cv2.VideoCapture(0)
with mp_pose.Pose(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            # If loading a video, use 'break' instead of 'continue'.
            continue

        # Flip the image horizontally for a later selfie-view display, and convert
        # the BGR image to RGB.
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        results = pose.process(image)

        if results.pose_landmarks:
            pose_landmarks = results.pose_landmarks.ListFields()[0][1]
            left_hand = pose_landmarks[20]
            right_hand = pose_landmarks[19]

            unity_json = str({
                'left_hand_x': left_hand.x,
                'left_hand_y': left_hand.y,
                'right_hand_x': right_hand.x,
                'right_hand_y': right_hand.y,
            })

            sock.sendto(
                (unity_json).encode(),
                (UDP_IP, UDP_PORT)
            )

            # print(unity_json)

            if left_hand.y < 0.5 and left_hand.x < 0.5:
                # print('left hand guitar ready!')
                left_hand_ready = True
            else:
                left_hand_ready = False
                # print('left hand down')

            if right_hand.y > 0.75 and (not right_already_down) and left_hand_ready:
                count_kicks += 1
                print(f'{count_kicks} guitar kick!')
                right_already_down = True
                mid = MidiFile('music.mid', clip=True)
                msg = mido.Message('note_on', note=60, time=0.2)
                port.send(msg)
                time.sleep(msg.time)
                port.send(mido.Message('note_off', note=60))

            if right_hand.y <= 0.75:
                right_already_down = False


            # print("_" * 10, "Jump Action Triggered!", "_" * 10)

        # Draw the pose annotation on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        mp_drawing.draw_landmarks(
            image,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
        cv2.imshow('MediaPipe Pose', image)
        if cv2.waitKey(5) & 0xFF == 27:
            break
cap.release()
