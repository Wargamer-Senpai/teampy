import json
import os
import re
from datetime import datetime

# File to persist warnings and status
mod_data_file = os.path.join("data", "moderation_data.json")

# Internal data structure
moderation_data = {
  "enabled_rooms": [],
  "warnings": {}  # Format: {room_id: {room_id: {user_id: {"count": int, "reasons": [str]}}}
}

# Ensure data folder exists
if not os.path.exists("data"):
  os.makedirs("data")

# Load from file if exists
if os.path.isfile(mod_data_file):
  with open(mod_data_file, "r") as f:
    try:
      moderation_data = json.load(f)
    except json.JSONDecodeError:
      moderation_data = {"enabled_rooms": [], "warnings": {}}

# Save data to disk
def func_save_moderation_data():
  with open(mod_data_file, "w") as f:
    json.dump(moderation_data, f)


def func_enable_moderation(room_id):
  """Enable moderation for a specific room.

  Args:
      room_id (str): The ID of the room to enable moderation for
  """
  if room_id not in moderation_data["enabled_rooms"]:
    moderation_data["enabled_rooms"].append(room_id)
    func_save_moderation_data()

def func_disable_moderation(room_id):
  """Disable moderation for a specific room.

  Args:
      room_id (str): The ID of the room to enable moderation for
  """
  if room_id in moderation_data["enabled_rooms"]:
    moderation_data["enabled_rooms"].remove(room_id)
    func_save_moderation_data()


def func_is_moderation_enabled(room_id):
  """Check if moderation is enabled for a specific room.

  Args:
      room_id (str): The ID of the room to enable moderation for.

  Returns:
      bool: True if moderation is enabled, False otherwise.
  """
  return room_id in moderation_data["enabled_rooms"]


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

  return False, ""


def func_warn_user(room_id, user_id, reason):
  """Warn a user in a specific room.

  Args:
      room_id (str): The ID of the room where the user is located
      user_id (str): The ID of the user to warn
      reason (str): The reason for the warning

  Returns:
      int: The number of warnings the user has received in that room
  """
  room_warns = moderation_data["warnings"].setdefault(room_id, {})
  user_data = room_warns.setdefault(user_id, {"count": 0, "reasons": []})
  user_data["count"] += 1
  user_data["reasons"].append(f"{datetime.utcnow().isoformat()} - {reason}")
  func_save_moderation_data()
  return user_data["count"]

def func_reset_warnings(room_id, user_id):
  """Reset warnings for a user in a specific room.

  Args:
      room_id (str): The ID of the room where the user is located
      user_id (str): The ID of the user to reset warnings for
  """
  if room_id in moderation_data["warnings"]:
    moderation_data["warnings"][room_id].pop(user_id, None)
    func_save_moderation_data()


def func_get_warning_count(room_id, user_id):
  """Get the warning count for a user in a specific room.

  Args:
      room_id (str): The ID of the room where the user is located
      user_id (str): The ID of the user to reset warnings for

  Returns:
      str: A response message, with the number of warnings the user has received in that room
  """
  user_data = moderation_data["warnings"].get(room_id, {}).get(user_id)
  if user_data:
    reasons = "\n".join(user_data["reasons"])
    return f"Warnings: {user_data['count']}\nReasons:\n{reasons}"
  else:
    return "No warnings found."
