import importlib
import inspect
import re 
import os
import json
import yaml

import config
from modules.logger import func_write_to_log


def func_toggle_autojoin(matrix_join_rooms,configfile):
  """toggle if the bot should auto accept and join rooms

  Args:
      matrix_join_rooms (bool): current state
      configfile (str): config file location
  """
  current_function = inspect.currentframe().f_code.co_name
  
  # invert Boolean
  matrix_join_rooms_new = not matrix_join_rooms
  func_write_to_log("toggling auto Join to " + str(matrix_join_rooms_new), "INFO", current_function)

  # open file and
  with open(configfile, "r") as f:
    content = f.readlines()

  # search line with variable
  for i, line in enumerate(content):
    if line.startswith("matrix_join_rooms"):
      content[i] = "matrix_join_rooms = "+str(matrix_join_rooms_new)+"\n"
      break

  # overwrite found line
  with open(configfile, "w") as f:
    f.writelines(content)

  importlib.reload(config)
  func_override_with_env(config)



def func_override_with_env(cfg_mod):
  """This function overrides the attributes of a given config object with environment variables.
  For each attribute in cfg_mod:
    1. Look up an ENV var matching its name (uppercased).
    2. Strip out newlines/tabs and trim.
    3. Cast back to its original type (bool, list, dict, scalar).
    4. Recursively resolve any string keys or values that name variables in cfg_mod.
    5. Overwrite the attribute if found.

  Args:
      cfg_mod (module): The config module to override with environment variables.
  """
  def resolve_vars(obj):
    # If it's a bare‐word string that matches something in cfg_mod, substitute it.
    if isinstance(obj, str) and hasattr(cfg_mod, obj):
      return getattr(cfg_mod, obj)

    # Recurse into dicts
    if isinstance(obj, dict):
      return { resolve_vars(k): resolve_vars(v) for k, v in obj.items() }

    # Recurse into lists
    if isinstance(obj, list):
      return [resolve_vars(item) for item in obj]

    # Otherwise leave it alone
    return obj

  for name, val in vars(cfg_mod).items():
    env_name = name.upper()
    func_write_to_log(f"Checking {env_name} for env var", "DEBUG", "override_with_env")
    raw = os.getenv(env_name)
    if raw is None:
      continue

    # Strip newlines/tabs and trim
    env = re.sub(r'[\r\n\t]', '', raw).strip()
    orig_type = type(val)

    try:
      if orig_type is bool:
        new_val = env.lower() in ("1", "true", "yes", "y", "on")

      elif orig_type is list:
        # JSON-first, then CSV
        try:
          parsed = json.loads(env)
          if isinstance(parsed, list):
            new_val = parsed
          else:
            raise ValueError
        except Exception:
          new_val = [item.strip() for item in env.split(",") if item.strip()]

      elif orig_type is dict:
        # Try YAML (accepts both JSON and {bare: word} syntax)
        try:
          parsed = yaml.safe_load(env)
          if isinstance(parsed, dict):
            new_val = parsed
          else:
            raise ValueError
        except Exception:
          new_val = env

      else:
        # int, float, str, etc.
        new_val = orig_type(env)

    except Exception:
      new_val = env  # fallback

    # **NEW**: resolve any variable‐name strings inside lists/dicts
    if isinstance(new_val, (list, dict)):
      new_val = resolve_vars(new_val)

    func_write_to_log(f"Overriding {name} with {new_val!r}", "DEBUG", "override_with_env")
    setattr(cfg_mod, name, new_val)