import cv2
import time
import os



def record_video(duration):
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        return "Could not access the camera."
    
    try:
        # Countdown before recording
        for i in range(3, 0, -1):
            print(f"Recording will start in {i}...")
            time.sleep(1)

        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        filename = "video.avi"
        out = cv2.VideoWriter(filename, fourcc, 20.0, (640, 480))

        start_time = time.time()
        while time.time() - start_time < duration:
            ret, frame = camera.read()
            if ret:
                out.write(frame)
            else:
                break

        return f"Video recorded for {duration} seconds and saved as {filename}."
    finally:
        camera.release()
        out.release()
