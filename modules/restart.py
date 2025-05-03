#!/usr/bin/env python3
import sys
import subprocess
import time
import os

# Determine OS from first arg
arg1 = sys.argv[1]

time.sleep(3)

# Base directory of this script
script_path = os.path.dirname(os.path.abspath(__file__))

# Path to the main bot script
if arg1 == "Linux":
  script_file = os.path.join(script_path, "../main.py")
elif arg1 == "Windows":
  script_file = os.path.join(script_path, "..\\main.py")
else:
  raise ValueError(f"Unsupported OS: {arg1}")

# Where to write the PID
PID_FILE = os.path.abspath(os.path.join(script_path, "../bot.pid"))

# Launch the bot and capture its PID
python_executable = sys.executable
proc = subprocess.Popen([python_executable, script_file])

# Write the PID out so the watchdog can pick it up
with open(PID_FILE, "w") as f:
  f.write(str(proc.pid))