import logging
import datetime
import os
import config

def func_write_to_log(log_message, log_level, log_function, log_file=os.path.join(os.path.abspath(__file__),"..","..","logs","bot.log")):
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