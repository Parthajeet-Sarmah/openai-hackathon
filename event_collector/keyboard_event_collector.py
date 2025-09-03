import json
import time
from pynput import keyboard

LOG_FILE = "keyboard_events.jsonl"

def log_event(event_type, key):
    entry = {
        "timestamp": time.time(),
        "event": event_type,
        "key": str(key)
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(entry)

def on_press(key):
    log_event("press", key)

def on_release(key):
    log_event("release", key)

with keyboard.Listener(
    on_press=on_press,
    on_release=on_release
) as listener:
    print("Keyboard Event Collector started.")
    listener.join()
