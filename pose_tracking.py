import cv2
import mediapipe as mp
import socket
import numpy as np


UDP_IP = "127.0.0.1"
UDP_PORT = 5065

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

# hand_down_overlay = cv2.imread('hand_down.png', cv2.IMREAD_UNCHANGED)

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

            unity_data_string = f'left_hand {left_hand.x} left_hand_y {left_hand.y} right_hand_x {right_hand.x} right_hand_y {right_hand.y}'
            # unity_json = str({
            #     'left_hand_x': left_hand.x,
            #     'left_hand_y': left_hand.y,
            #     'right_hand_x': right_hand.x,
            #     'right_hand_y': right_hand.y,
            # })

            sock.sendto(
                (unity_data_string).encode(),
                (UDP_IP, UDP_PORT)
            )

            print(unity_data_string)
            # print("_" * 10, "Jump Action Triggered!", "_" * 10)

        # Draw the pose annotation on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        mp_drawing.draw_landmarks(
            image,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())

        # print(hand_down_overlay.shape)
        # added_image = logo_overlay(image, hand_down_overlay, scale=0.5, y=-100, x=-100)
        # added_image = image * (1 - hand_down_overlay[:, :, 3:]) + hand_down_overlay[:, :, 3:]
        # added_image = cv2.addWeighted(image, 1., hand_down_overlay, 1., 0)
        cv2.imshow('MediaPipe Pose', image)
        if cv2.waitKey(5) & 0xFF == 27:
            break
cap.release()
