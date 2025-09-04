import multiprocessing
import subprocess

def run_script(script_name):
    subprocess.run(["python3", script_name])

if __name__ == "__main__":
    collectors = [
        "event_collector/mouse_event_collector.py",
        "event_collector/keyboard_event_collector.py",
        "event_collector/process_event_collector.py"
    ]

    processes = []

    for script in collectors:
        p = multiprocessing.Process(target=run_script, args=(script,))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()
