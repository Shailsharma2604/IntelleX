import sys
import cv2
import mediapipe as mp
import numpy as np
import time
import platform
import subprocess

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QWidget, 
    QSlider, QTextEdit, QHBoxLayout, QPushButton, QMessageBox
)
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer

# Platform-specific volume control imports
try:
    if platform.system() == "Windows":
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    elif platform.system() == "Darwin":  # macOS
        import osascript
    elif platform.system() == "Linux":
        import subprocess
except ImportError:
    print("Warning: Some platform-specific modules could not be imported.")

class GestureAppLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_gesture_recognition()
        self.setup_volume_control()
        self.setup_video_capture()
        
    def setup_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Two-Handed Music Gesture Control")
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget and main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # Camera and controls layout
        camera_controls_layout = QHBoxLayout()
        main_layout.addLayout(camera_controls_layout)
        
        # Camera feed
        self.camera_label = QLabel("Camera Feed")
        self.camera_label.setMinimumSize(640, 480)
        self.camera_label.setStyleSheet("""
            border: 3px solid #3498db; 
            background-color: black; 
            color: white;
            font-size: 20px;
            text-align: center;
        """)
        camera_controls_layout.addWidget(self.camera_label)
        
        # Right-side controls
        right_controls = QVBoxLayout()
        camera_controls_layout.addLayout(right_controls)
        
        # Gesture Log
        right_controls.addWidget(QLabel("Gesture Log:"))
        self.gesture_log = QTextEdit()
        self.gesture_log.setReadOnly(True)
        self.gesture_log.setMaximumHeight(200)
        right_controls.addWidget(self.gesture_log)
        
        # Volume Control Section
        volume_layout = QVBoxLayout()
        right_controls.addLayout(volume_layout)
        volume_layout.addWidget(QLabel("Volume Control:"))
        
        # Volume Slider
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.manual_volume_change)
        volume_layout.addWidget(self.volume_slider)
        
        # Volume Bar
        self.volume_bar = QLabel("Volume: 50%")
        self.volume_bar.setStyleSheet("""
            background-color: #3498db;
            color: white;
            padding: 10px;
            border-radius: 10px;
        """)
        volume_layout.addWidget(self.volume_bar)
        
        # Status Bar
        self.status_bar = QLabel("Ready")
        self.status_bar.setStyleSheet("""
            background-color: #2ecc71;
            color: white;
            padding: 5px;
            border-radius: 5px;
        """)
        main_layout.addWidget(self.status_bar)
        
    def setup_gesture_recognition(self):
        """Initialize gesture recognition parameters"""
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,  # Allow detection of two hands
            min_detection_confidence=0.7,
            min_tracking_confidence=0.6
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Gesture tracking
        self.last_gesture_time = 0
        self.gesture_cooldown = 1000  # 1 second cooldown between gestures
        
        # Music control configurations
        self.music_gestures = {
            "Windows": {
                "play_pause": "start wmplayer",
                "next_track": "cmd /c \"powershell -Command \"$shell = New-Object -ComObject WScript.Shell; $shell.SendKeys('^{RIGHT}')\"\"",
                "prev_track": "cmd /c \"powershell -Command \"$shell = New-Object -ComObject WScript.Shell; $shell.SendKeys('^{LEFT}')\"\"",
            },
            "Darwin": {
                "play_pause": "osascript -e 'tell application \"iTunes\" to playpause'",
                "next_track": "osascript -e 'tell application \"iTunes\" to next track'",
                "prev_track": "osascript -e 'tell application \"iTunes\" to previous track'",
            },
            "Linux": {
                "play_pause": "dbus-send --print-reply --dest=org.mpris.MediaPlayer2.spotify /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.PlayPause",
                "next_track": "dbus-send --print-reply --dest=org.mpris.MediaPlayer2.spotify /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.Next",
                "prev_track": "dbus-send --print-reply --dest=org.mpris.MediaPlayer2.spotify /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.Previous",
            }
        }
        
    def setup_volume_control(self):
        """Setup platform-specific volume control"""
        self.current_volume = 50
        self.os_type = platform.system()
        
        try:
            if self.os_type == "Windows":
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(
                    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                self.volume_controller = interface.QueryInterface(IAudioEndpointVolume)
            else:
                self.volume_controller = None
        except Exception as e:
            self.log_message(f"Volume control setup error: {e}")
            self.volume_controller = None
        
    def setup_video_capture(self):
        """Initialize video capture"""
        self.cap = cv2.VideoCapture(0)
        
        # Attempt to set high-resolution capture
        try:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        except Exception as e:
            self.log_message(f"Camera resolution error: {e}")
        
        # Start capture timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # 30 ms interval
        
    def log_message(self, message):
        """Log messages to gesture log"""
        timestamp = time.strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {message}"
        self.gesture_log.append(full_message)
        
    def manual_volume_change(self):
        """Handle manual volume slider changes"""
        self.current_volume = self.volume_slider.value()
        self.update_volume_display()
        self.set_system_volume(self.current_volume)
        
    def update_volume_display(self):
        """Update volume display and bar"""
        self.volume_bar.setText(f"Volume: {self.current_volume}%")
        self.volume_bar.setStyleSheet(f"""
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                stop:0 #3498db, 
                stop:{self.current_volume/100} #3498db, 
                stop:{self.current_volume/100} #e0e0e0, 
                stop:1 #e0e0e0);
            color: white;
            padding: 10px;
            border-radius: 10px;
        """)
        
    def set_system_volume(self, volume):
        """Set system volume across different platforms"""
        try:
            volume_scalar = volume / 100.0
            
            if self.os_type == "Windows" and self.volume_controller:
                self.volume_controller.SetMasterVolumeLevelScalar(volume_scalar, None)
            elif self.os_type == "Darwin":
                osascript.run(f"set volume output volume {volume}")
            elif self.os_type == "Linux":
                subprocess.call(['amixer', '-D', 'pulse', 'seset', 'Master', f'{volume}%'])
            
            self.status_bar.setText(f"Volume set to {volume}%")
        except Exception as e:
            self.log_message(f"Volume control error: {e}")
            self.status_bar.setText("Volume control failed")
        
    def recognize_gesture(self, hands_landmarks):
        """Advanced gesture recognition for volume and music control"""
        current_time = int(time.time() * 1000)
        
        # Cooldown check
        if current_time - self.last_gesture_time < self.gesture_cooldown:
            return
        
        # Ensure we have correct number of hands
        if len(hands_landmarks) < 1 or len(hands_landmarks) > 2:
            return
        
        # Helper function to calculate 2D distance between two landmarks
        def landmark_distance(hand, landmark1, landmark2):
            pt1 = np.array([hand.landmark[landmark1].x, hand.landmark[landmark1].y])
            pt2 = np.array([hand.landmark[landmark2].x, hand.landmark[landmark2].y])
            return np.linalg.norm(pt1 - pt2)
        
        # Single Hand Volume Control
        if len(hands_landmarks) == 1:
            hand = hands_landmarks[0]
            
            # Volume Control: Vertical Thumb Movement
            thumb_tip = hand.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
            wrist = hand.landmark[self.mp_hands.HandLandmark.WRIST]
            
            # Calculate volume based on thumb's vertical position relative to wrist
            volume = np.interp(
                thumb_tip.y, 
                [wrist.y - 0.3, wrist.y + 0.3],  # Adjust range for sensitivity
                [0, 100]
            )
            volume = max(0, min(volume, 100))
            
            # Update volume if significant change
            if abs(volume - self.current_volume) > 5:
                self.current_volume = volume
                self.volume_slider.setValue(int(volume))
                self.update_volume_display()
                self.set_system_volume(volume)
                self.log_message(f"Volume adjusted to {int(volume)}%")
        
        # Two-Handed Music Control
        elif len(hands_landmarks) == 2:
            left_hand = hands_landmarks[0] if hands_landmarks[0].landmark[self.mp_hands.HandLandmark.WRIST].x < 0.5 else hands_landmarks[1]
            right_hand = hands_landmarks[1] if hands_landmarks[0].landmark[self.mp_hands.HandLandmark.WRIST].x < 0.5 else hands_landmarks[0]
            
            # Play/Pause: Left fist, Right open palm
            def is_fist(hand):
                return all(
                    hand.landmark[tip].y > hand.landmark[base].y 
                    for tip, base in [
                        (self.mp_hands.HandLandmark.THUMB_TIP, self.mp_hands.HandLandmark.THUMB_MCP),
                        (self.mp_hands.HandLandmark.INDEX_FINGER_TIP, self.mp_hands.HandLandmark.INDEX_FINGER_PIP),
                        (self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP, self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP),
                        (self.mp_hands.HandLandmark.RING_FINGER_TIP, self.mp_hands.HandLandmark.RING_FINGER_PIP),
                        (self.mp_hands.HandLandmark.PINKY_TIP, self.mp_hands.HandLandmark.PINKY_PIP)
                    ]
                )
            
            def is_open_palm(hand):
                return all(
                    hand.landmark[tip].y < hand.landmark[base].y 
                    for tip, base in [
                        (self.mp_hands.HandLandmark.THUMB_TIP, self.mp_hands.HandLandmark.THUMB_MCP),
                        (self.mp_hands.HandLandmark.INDEX_FINGER_TIP, self.mp_hands.HandLandmark.INDEX_FINGER_PIP),
                        (self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP, self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP),
                        (self.mp_hands.HandLandmark.RING_FINGER_TIP, self.mp_hands.HandLandmark.RING_FINGER_PIP),
                        (self.mp_hands.HandLandmark.PINKY_TIP, self.mp_hands.HandLandmark.PINKY_PIP)
                    ]
                )
            
            # Detect specific gestures
            if is_fist(left_hand) and is_open_palm(right_hand):
                self.execute_music_control("play_pause")
                self.last_gesture_time = current_time
                self.log_message("Play/Pause Music")
            
            # Next track: Peace sign (V) with left, open palm right
            elif (landmark_distance(left_hand, self.mp_hands.HandLandmark.INDEX_FINGER_TIP, self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP) < 0.05 and
                  is_open_palm(right_hand)):
                self.execute_music_control("next_track")
                self.last_gesture_time = current_time
                self.log_message("Next Track")
            
            # Previous track: Thumb extended with left, open palm right
            elif (left_hand.landmark[self.mp_hands.HandLandmark.THUMB_TIP].y < left_hand.landmark[self.mp_hands.HandLandmark.WRIST].y and
                  is_open_palm(right_hand)):
                self.execute_music_control("prev_track")
                self.last_gesture_time = current_time
                self.log_message("Previous Track")
        
        return None
    
    def execute_music_control(self, control_type):
        """Execute music control command"""
        try:
            command = self.music_gestures.get(self.os_type, {}).get(control_type)
            
            if command:
                self.log_message(f"Music {control_type.replace('_', ' ').title()}")
                self.status_bar.setText(f"Music {control_type.replace('_', ' ').title()}")
                subprocess.Popen(command, shell=True)
            else:
                self.log_message(f"No {control_type} command for {self.os_type}")
        except Exception as e:
            self.log_message(f"Music control error: {e}")
            self.status_bar.setText(f"Failed to {control_type.replace('_', ' ')}")
        
    def update_frame(self):
        """Process video frame and detect gestures"""
        ret, frame = self.cap.read()
        if not ret:
            self.status_bar.setText("Camera capture failed")
            return
        
        # Flip and convert frame
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process hand detection
        results = self.hands.process(rgb_frame)
        
        # Gesture recognition
        if results.multi_hand_landmarks:
            # Draw hand landmarks
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                )
            
            # Recognize gestures if we have one or two hands
            if len(results.multi_hand_landmarks) in [1, 2]:
                self.recognize_gesture(results.multi_hand_landmarks)
        
        # Convert frame to QPixmap
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        
        # Scale image
        pixmap = QPixmap.fromImage(qt_image).scaled(
            self.camera_label.width(), 
            self.camera_label.height(), 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        
        self.camera_label.setPixmap(pixmap)
        
    def closeEvent(self, event):
        """Clean up resources on application close"""
        self.cap.release()
        self.hands.close()
        event.accept()

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    gesture_app = GestureAppLauncher()
    gesture_app.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()