import inspect
import os

from modules.logger import func_write_to_log
from modules.matrix import *

def func_update_notify_room_add(matrix_room,teamspeak_version_notify_file,teamspeak_version_notify_matrix_rooms):
  """add a room to get notify when an update is available

  Args:
      matrix_room (str): room id to add
      teamspeak_version_notify_file (str): path to file with rooms to notify
      teamspeak_version_notify_matrix_rooms (list): list of rooms to notify
      
  Returns:
      str: message that got added or was already 
  """
  current_function = inspect.currentframe().f_code.co_name

  if not matrix_room in teamspeak_version_notify_matrix_rooms:
    func_write_to_log("added " + matrix_room + " to notify group", "INFO", current_function)
    teamspeak_version_notify_matrix_rooms = teamspeak_version_notify_matrix_rooms + (matrix_room,)
    file_content = " ".join(teamspeak_version_notify_matrix_rooms)
    with open(teamspeak_version_notify_file, "w") as file:
      # Write the string representation of the tuple to the file
      file.write(file_content)

    return "added to notify group :100:"

  else: 
    func_write_to_log(matrix_room + " already in notify group", "INFO", current_function)
    return "already in notify groupd :eyes:"


def func_notify_update(matrix_base_url,access_token, user_agent, teamspeak_version_notify_matrix_rooms, matrix_update_message, teamspeak_version_saved, teamspeak_version_notify_file, event_id, stat_dict):
  """notify the rooms that an new update is available

  Args:
      matrix_base_url (str): the base URL of the Matrix server
      access_token (str): current session access token
      user_agent (str): user agent for talking to the api
      teamspeak_version_notify_matrix_rooms (list): list of rooms to notify
      matrix_update_message (str): contains the message of when an update is available
      teamspeak_version_saved (str): the version that was found
      teamspeak_version_notify_file (str): path to file with rooms to notify
      event_id (str): the event id of the message 
  """
  current_function = inspect.currentframe().f_code.co_name
  if teamspeak_version_notify_matrix_rooms:
    for matrix_room in teamspeak_version_notify_matrix_rooms:
      response = func_send_message(matrix_base_url, access_token, user_agent, matrix_room, matrix_update_message+ teamspeak_version_saved, event_id, stat_dict)

      if not response == 200:
        func_write_to_log("couldnt notify room: " + matrix_room + ", probably not member of the room anymore.  %s" % response.text, "ERROR", current_function)
        if response.text["errcode"] == "M_FORBIDDEN":
          func_write_to_log("removing room (" + matrix_room + ") from notifing", "INFO", current_function)
          func_update_notify_room_remove(matrix_room, teamspeak_version_notify_file, teamspeak_version_notify_matrix_rooms)


def func_update_notify_room_remove(matrix_room, teamspeak_version_notify_file, teamspeak_version_notify_matrix_rooms):
  """remove a room from notification when teamspeak has new update

  Args:
      matrix_room (str): id of room to remove
      teamspeak_version_notify_file (str): path to file with rooms to notify
      teamspeak_version_notify_matrix_rooms (list): list of rooms to notify

  Returns:
      str: message that room got removed
  """
  current_function = inspect.currentframe().f_code.co_name
  teamspeak_version_notify_matrix_rooms = tuple(value for value in teamspeak_version_notify_matrix_rooms if value != matrix_room)
  file_content = " ".join(teamspeak_version_notify_matrix_rooms)
  with open(teamspeak_version_notify_file, "w") as file:
    # Write the string representation of the tuple to the file
    file.write(file_content)
  func_write_to_log("removed " + matrix_room + "from notify group", "INFO", current_function)
  return "removed from notify group :salute:"


def func_update_notify_rooms_get(teamspeak_version_notify_file):
  """get current rooms that are in the file for notification 

  Args:
      teamspeak_version_notify_file (str): path to file with rooms to notify

  Returns:
      tuple: list of room ids 
  """
  
  # open file in read only mode, if exist
  if os.path.exists(teamspeak_version_notify_file):
    with open(teamspeak_version_notify_file, "r") as file:
      # read first line
      first_line = file.readline().strip()
      # split values with spaces
      values = first_line.split()
      # convert to tuple
      teamspeak_version_notify_matrix_rooms = tuple(values)
    return teamspeak_version_notify_matrix_rooms
  else:
    func_write_to_log("file with notify rooms not found, creating new one", "INFO", "func_update_notify_rooms_get")
    # create empty file
    with open(teamspeak_version_notify_file, "w") as file:
      file.write("")
    return tuple()
    