import json
import time
from pynput import mouse

LOG_FILE = "mouse_events.jsonl"

def log_event(event_type, x, y, button=None, pressed=None):
    entry = {
        "timestamp": time.time(),
        "event": event_type,
        "position": {"x": x, "y": y},
        "button": str(button) if button else None,
        "pressed": pressed
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(entry)

def on_move(x, y):
    log_event("move", x, y)

def on_click(x, y, button, pressed):
    log_event("click", x, y, button, pressed)

def on_scroll(x, y, dx, dy):
    entry = {
        "timestamp": time.time(),
        "event": "scroll",
        "position": {"x": x, "y": y},
        "scroll": {"dx": dx, "dy": dy}
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(entry)

with mouse.Listener(
    on_move=on_move,
    on_click=on_click,
    on_scroll=on_scroll
) as listener:
    print("Mouse Event Collector started.")
    listener.join()
