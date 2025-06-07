import cv2
import time
import os


def capture_photo():
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        return "Could not access the camera."
    
    try:
        # Countdown before capturing
        for i in range(3, 0, -1):
            print(f"Capturing in {i}...")
            time.sleep(1)

        ret, frame = camera.read()
        if ret:
            filename = "photo.jpg"
            cv2.imwrite(filename, frame)
            return f"Photo saved as {filename}."
        else:
            return "Failed to capture photo."
    finally:
        camera.release()
