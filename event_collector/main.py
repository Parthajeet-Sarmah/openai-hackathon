import multiprocessing
import subprocess

def run_script(script_name):
    subprocess.run(["python3", script_name])

if __name__ == "__main__":
    collectors = [
        "event-collector/mouse-event-collector.py",
        "event-collector/keyboard-event-collector.py",
        "event-collector/process-event-collector.py"
    ]

    processes = []

    for script in collectors:
        p = multiprocessing.Process(target=run_script, args=(script,))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()
