import logging
import datetime
import os
import config

def rotate_logs(log_file, backups=7):
  """
  Rotate log files by renaming existing backups and deleting the oldest.

  Args:
    log_file (str): Path to the main log file.
    backups (int): Number of backup files to keep.
  """
  # Remove the oldest backup if it exists
  oldest = f"{log_file}.{backups}"
  if os.path.exists(oldest):
    os.remove(oldest)

  # Shift backups: .6 -> .7, .5 -> .6, ..., .1 -> .2
  for i in range(backups - 1, 0, -1):
    src = f"{log_file}.{i}"
    dst = f"{log_file}.{i+1}"
    if os.path.exists(src):
      os.rename(src, dst)

  # Rename current log to .1
  if os.path.exists(log_file):
    os.rename(log_file, f"{log_file}.1")


def func_write_to_log(log_message, log_level, log_function, log_file=os.path.join(os.path.abspath(__file__),"..","..","logs","bot.log"), max_size_mb=5, backups=7):
  """writes log messages to a file and prints them to the console if debug mode is enabled

  Args:
      log_message (str): message to be logged
      log_level (str): log level of the message, possible values: CRITICAL, ERROR, WARNING, INFO, DEBUG
      log_function (str): name of the function that is logging the message
      log_file (str, optional): the log file, defaults to os.path.join(os.path.abspath(__file__),"..","..","logs","bot.log").
  """
  # Rotate logs only if size exceeds threshold
  if os.path.exists(log_file) and os.path.getsize(log_file) >= max_size_mb * 1024 * 1024:
    rotate_logs(log_file, backups)

  # fallback if conf_log_level has been wrongly configured
  config_log_level = config.log_level
  if not config_log_level in ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]:
    config_log_level = "WARNING"

  # prepare logging file
  # log file format: output_YYYY-MM-DD_HH-MM-SS.log
  logging.basicConfig(filename=log_file, level=config_log_level, format='%(asctime)s - %(levelname)s - %(message)s')
  log_message = log_function + " - " + log_message 
  
  # print to cli if started in debug mode
  if config.debug_mode == True:
    print(func_time_now() + " - " + log_level + " - " + log_message)

  if log_level == "CRITICAL":
    logging.critical(log_message)
  elif log_level == "ERROR": 
    logging.error(log_message)
  elif log_level == "WARNING":
    logging.warning(log_message)
  elif log_level == "INFO":
    logging.info(log_message)
  else:
    logging.debug(log_message)

def func_time_now():
  """returns the current time

  Returns:
      str: current time
  """
  return str(datetime.datetime.now())