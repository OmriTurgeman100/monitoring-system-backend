import subprocess
from multiprocessing import Process
from threading import Thread

scripts = [
    "script_1.py",
    "script_2.py",
    "script_3.py",
    "script_4.py"
]

def run_script(script_name):
    subprocess.Popen(["python", script_name])

if __name__ == "__main__":
    threads = []
    for script in scripts:
        thread = Thread(target=run_script, args=(script,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()
