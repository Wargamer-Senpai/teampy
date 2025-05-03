import inspect

from modules.logger import func_write_to_log

def func_add_stats(key,stat_dict):
  current_function = inspect.currentframe().f_code.co_name
  if key in stat_dict:
    func_write_to_log(f"updated {key} by one" , "DEBUG", current_function)
    stat_dict[key] += 1
  else:
    func_write_to_log(f"key {key} not in array, so setting 1" , "DEBUG", current_function)
    stat_dict[key] = 1

def func_write_stats_to_file(stat_dict, stats_file):
  current_function = inspect.currentframe().f_code.co_name
  func_write_to_log("writing stats to file", "DEBUG", current_function)
  with open(stats_file, "w") as f:
    for key, value in stat_dict.items():
      f.write(f"{key}={value}\n")