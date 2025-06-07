# timer.py
import threading
import time

def set_timer(seconds):
    def timer_thread():
        time.sleep(seconds)
        print("⏰ Timer ended!")
    threading.Thread(target=timer_thread).start()
    return f"Timer set for {seconds} seconds."

def set_alarm(seconds):
    return set_timer(seconds)  # Same logic for now
