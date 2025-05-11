import json
import os
import re
from datetime import datetime

from modules.logger import func_write_to_log

# File to persist warnings and status
mod_data_file = os.path.join("data", "moderation_data.json")

# Ensure data folder exists
if not os.path.exists("data"):
  os.makedirs("data")

def func_load_moderation_data():
  """Load moderation data from disk.

  Returns:
      dict: The moderation data loaded from disk
  """
  if os.path.isfile(mod_data_file):
    with open(mod_data_file, "r") as f:
      try:
        return json.load(f)
      except json.JSONDecodeError:
        return {"enabled_rooms": [], "warnings": {}}
  return {"enabled_rooms": [], "warnings": {}}


# Save data to disk
def func_save_moderation_data(data):
  """Save moderation data to disk.

  Args:
      data (dict): The moderation data to save
  """
  func_write_to_log("Saving moderation data to disk", "DEBUG", "func_save_moderation_data")
  with open(mod_data_file, "w") as f:
    json.dump(data, f)
  print(json.dumps(data,sort_keys=True, indent=4))


def func_enable_moderation(matrix_room):
  """Enable moderation for a specific room.

  Args:
      matrix_room (str): The ID of the room to enable moderation for
  """
  moderation_data = func_load_moderation_data()
  if matrix_room not in moderation_data["enabled_rooms"]:
    moderation_data["enabled_rooms"].append(matrix_room)
    func_save_moderation_data(moderation_data)

def func_disable_moderation(matrix_room):
  """Disable moderation for a specific room.

  Args:
      matrix_room (str): The ID of the room to enable moderation for
  """
  moderation_data = func_load_moderation_data()
  if matrix_room in moderation_data["enabled_rooms"]:
    moderation_data["enabled_rooms"].remove(matrix_room)
    # pretty print
    print(json.dumps(moderation_data,sort_keys=True, indent=4))
    func_save_moderation_data(moderation_data)


def func_is_moderation_enabled(matrix_room):
  """Check if moderation is enabled for a specific room.

  Args:
      matrix_room (str): The ID of the room to enable moderation for.

  Returns:
      bool: True if moderation is enabled, False otherwise.
  """
  moderation_data = func_load_moderation_data()
  return matrix_room in moderation_data["enabled_rooms"]


def func_check_violation(message, sender, admin_list, mod_list):
  """Check if a message violates moderation rules.

  Args:
      message (str): The message to check
      sender (str): The ID of the user who sent the message
      admin_list (list): List of admin user IDs
      mod_list (list): List of moderator user IDs

  Returns:
      bool: True if the message violates moderation rules, False otherwise.
  """
  banned_words = ["badword1", "badword2", "spam"]
  for word in banned_words:
    if re.search(rf"\\b{re.escape(word)}\\b", message, re.IGNORECASE):
      return True, f"Used banned word: {word}"

  if "<@_|everyone>" in message and sender not in admin_list and sender not in mod_list:
    return True, "Unauthorized `@everyone` usage"

  return False, None


def func_warn_user(matrix_room, user_id, reason):
  """Warn a user in a specific room.

  Args:
      matrix_room (str): The ID of the room where the user is located
      user_id (str): The ID of the user to warn
      reason (str): The reason for the warning

  Returns:
      strn,int: A response message and the number of warnings the user has received in that room
  """
  moderation_data = func_load_moderation_data()
  room_warns = moderation_data["warnings"].setdefault(matrix_room, {})
  user_data = room_warns.setdefault(user_id, {"count": 0, "reasons": []})
  user_data["count"] += 1
  user_data["reasons"].append(f"{datetime.now(datetime.timezone.utc).isoformat()} - {reason}")
  func_save_moderation_data(moderation_data)
  return f"Deleted message, reason: {reason}. (Warn count: {user_data['count']})", user_data['count']

def func_reset_warnings(matrix_room, user_id):
  """Reset warnings for a user in a specific room.

  Args:
      matrix_room (str): The ID of the room where the user is located
      user_id (str): The ID of the user to reset warnings for
  """
  moderation_data = func_load_moderation_data()
  if matrix_room in moderation_data["warnings"]:
    moderation_data["warnings"][matrix_room].pop(user_id, None)
    func_save_moderation_data(moderation_data)


def func_get_warning_count(matrix_room, user_id):
  """Get the warning count for a user in a specific room.

  Args:
      matrix_room (str): The ID of the room where the user is located
      user_id (str): The ID of the user to reset warnings for

  Returns:
      str: A response message, with the number of warnings the user has received in that room
  """
  moderation_data = func_load_moderation_data()
  user_data = moderation_data["warnings"].get(matrix_room, {}).get(user_id)
  if user_data:
    reasons = "\n".join(user_data["reasons"])
    return f"Warnings: {user_data['count']}\nReasons:\n{reasons}"
  else:
    return "No warnings found."