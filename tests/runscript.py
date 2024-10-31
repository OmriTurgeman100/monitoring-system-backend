import subprocess
from threading import Thread

scripts = [
    "script_one.py",
    "script_two.py",
]

def run_script(script_name):
    subprocess.Popen("python ", script_name)

for item 