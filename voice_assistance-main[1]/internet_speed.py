import subprocess
import logging
import os

def get_internet_speed():
    try:
        result = subprocess.run(['speedtest-cli', '--simple'], stdout=subprocess.PIPE, text=True, timeout=60)
        return result.stdout.strip() if result.returncode == 0 else "Speedtest failed."
    except Exception as e:
        logging.error(f"Speedtest error: {e}")
        return "Error checking internet speed."