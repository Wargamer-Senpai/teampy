import inspect
import subprocess
import sys
import platform
import os

from modules.logger import func_write_to_log

def func_bot_stop():
  """stop the bot
  """
  current_function = inspect.currentframe().f_code.co_name
  func_write_to_log("stopping bot...", "INFO", current_function)
  exit(0)

def func_bot_restart(main_script_path):
  """restart the bot
  """
  current_function = inspect.currentframe().f_code.co_name
  os_name = platform.system()
  func_write_to_log("restarting bot... on " + os_name , "INFO", current_function)
  # splitted linux and windows if function shouldnt work
  if os_name == "Linux":
    python_executable = sys.executable
    script_file = os.path.join(main_script_path, "./modules/restart.py")
    os.system(python_executable + " " + script_file + " " + os_name )
    exit(0)
  if os_name == "Windows":
    python_executable = sys.executable
    script_file = main_script_path +".\\modules\\restart.py" 
    subprocess.call([python_executable, script_file, os_name])
    exit(0)
  else:
    func_write_to_log("Couldnt detect OS for proper restart", "CRITICAL", current_function)
    exit(255)