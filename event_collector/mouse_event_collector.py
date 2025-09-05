import json
import time
from pynput import mouse

LOG_FILE = "mouse_events.jsonl"

last_move_time = 0

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
    global last_move_time
    current_time = time.time()

    if current_time - last_move_time >= 1.0:
        log_event("move", x, y)
        last_move_time = current_time

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
