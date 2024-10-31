import subprocess
from multiprocessing import Process

scripts = [
    "script_one.py",
    "script_two.py",
    "script_three.py"
]

def run_script(script_name):
    subprocess.Popen(["python", script_name])

if __name__ == "__main__":
    processes = []
    for script in scripts:
        process = Process(target=run_script, args=(script,))
        process.start()
        processes.append(process)

    for process in processes:
        process.join()
