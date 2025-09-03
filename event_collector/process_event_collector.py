import json
import time
import psutil
import hashlib
import getpass

LOG_FILE = "user_process_events.jsonl"
POLL_INTERVAL = 1  # Adjust as needed

# Common system users to exclude (extend based on your OS)
SYSTEM_USERS = {"root", "systemd-network", "syslog", "messagebus", "dbus", "nobody"}

def is_user_process(proc):
    try:
        username = proc.username()
        if username and username not in SYSTEM_USERS:
            # include only the current logged-in user's processes:
            current_user = getpass.getuser()
            return username == current_user
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False
    return False

def process_metadata(proc):
    try:
        if not is_user_process(proc):
            return None
        with proc.oneshot():
            info = {
                "pid": proc.pid,
                "ppid": proc.ppid(),
                "name": proc.name(),
                "exe": proc.exe(),
                "cmdline": proc.cmdline(),
                "status": proc.status(),
                "username": proc.username(),
                "create_time": proc.create_time(),
                "memory_info": proc.memory_info()._asdict(),
                "cpu_times": proc.cpu_times()._asdict(),
                "cpu_percent": proc.cpu_percent(interval=None),
                "num_threads": proc.num_threads(),
                "cwd": proc.cwd() if hasattr(proc, "cwd") else None,
                "environ_hash": hashlib.sha256(
                    json.dumps(proc.environ() if hasattr(proc, "environ") else {}).encode()
                ).hexdigest(),
            }
    except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
        return None
    except Exception:
        return None
    return info

def log_event(event_type, proc_info):
    entry = {
        "timestamp": time.time(),
        "event": event_type,
        "process": proc_info
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(entry)

def main():
    print("User Process Event Collector started.")
    known_pids = set()
    process_snapshots = {}

    while True:
        current_pids = set(psutil.pids())
        new_pids = current_pids - known_pids
        for pid in new_pids:
            try:
                proc = psutil.Process(pid)
                meta = process_metadata(proc)
                if meta:
                    process_snapshots[pid] = meta
                    log_event("process_start", meta)
            except Exception:
                continue

        ended_pids = known_pids - current_pids
        for pid in ended_pids:
            meta = process_snapshots.pop(pid, {"pid": pid})
            log_event("process_terminate", meta)

        known_pids = current_pids
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
