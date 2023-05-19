# gets triggered by the main script
import sys
import subprocess
import time
import os


arg1 = sys.argv[1]

time.sleep(3)
if arg1 == "Linux": 
    # get current execution directory 
    script_path = os.path.dirname(os.path.abspath(__file__))
    python_executable = sys.executable
    script_file = os.path.join(script_path, "../main.py")
elif arg1 == "Windows":
    # get current execution directory 
    script_path = os.path.dirname(os.path.abspath(__file__))
    python_executable = sys.executable
    script_file = os.path.join(script_path, "..\\main.py")

subprocess.call([python_executable, script_file])