import inspect
import os

from modules.logger import func_write_to_log
from modules.matrix import *
from modules.utils import func_container_check

def func_health_check(main_script_path, matrix_base_url, matrix_username, matrix_password):
  """Perform a health check of the bot by checking the following:
  - if the bot is running inside a container
  - if the config file is present
  - if the matrix server URL is set correctly
  - if the username and password are set correctly
    


  Args:
      main_script_path (str): fullpath to main script
      matrix_base_url (str): the base URL of the Matrix server
      matrix_username (str): username for login
      matrix_password (str): password for login

  Returns:
      str: summary of the health check
  """
  current_function = inspect.currentframe().f_code.co_name
  bot_health_check_config = ""

  func_write_to_log("Checking health", "INFO", current_function)

  if func_container_check():
    bot_health_container = "True"
    func_write_to_log("!! running inside a container !!", "INFO", "startup")
  else:
    bot_health_container = "False"
    func_write_to_log("not running inside a container", "INFO", "startup")

  if os.path.isfile(os.path.join(main_script_path,"config.py")):
    bot_health_check_config = "Config file found"
    func_write_to_log("Config File found", "INFO", current_function)
  else: 
    func_write_to_log("Config file not found", "ERROR", current_function)
    bot_health_check_config = "**Config file not found**"

  if matrix_base_url == "https://chat.teamspeak.com":
    bot_health_check_baseurl = "URL is set correctly"
    func_write_to_log("URL set correctly", "INFO", current_function)
  else:
    bot_health_check_baseurl = "**URL is not correctly**"
    func_write_to_log("URL empty or pointing to wrong matrix homebase", "ERROR", current_function)

  if matrix_username:
    bot_health_check_username = "Username is set"
    func_write_to_log("Username is set", "INFO", current_function)
  else:
    bot_health_check_username = "**Username is empty**"
    func_write_to_log("Username wasnt found, error in config", "ERROR", current_function)

  if matrix_password:
    bot_health_check_password = "Password is set"
    func_write_to_log("Password is set", "INFO", current_function)
  else:
    bot_health_check_password = "**Password is empty**"
    func_write_to_log("Password wasnt found, error in config", "ERROR", current_function)

  return("Summary of Health Check: \nConfig: " + bot_health_check_config \
  + "\nMatrix Server URL: " + bot_health_check_baseurl + "\nUsername: " + bot_health_check_username \
  + "\nPassword: " + bot_health_check_password + "\nContainer: "+bot_health_container)
