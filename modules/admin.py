from distutils.version import LooseVersion

from modules.matrix import *
from modules.config_manager import *
from modules.health import *
from modules.bot_control import *
from modules.notify import *

import config

def func_handle_admin_help(admin_commands_overview,command_prefix):
  """Handle the help command and send a list of available commands to the admin

  Args:
      admin_commands_overview (dict): dictionary with command names and their descriptions
      command_prefix (str): command prefix for the bot commands

  Returns:
      str: formatted message with the list of available commands
  """

  matrix_prepare_message = "Here is __special__ help, dont worry!\n"
  for key in admin_commands_overview:
    if admin_commands_overview[key]["command_enabled"] == True:
      matrix_prepare_message += "**" + command_prefix + key + ":** " + admin_commands_overview[key]["description"] + "\n"
  return(matrix_prepare_message)


def func_handle_admin_autojoin(matrix_join_rooms,configfile):
  """Toggles the auto join feature for the bot. If the bot is set to auto join rooms, it will automatically join them when it starts up. If not, it will only join rooms that are specified in the command.

  Args:
      matrix_join_rooms (bool): True if the bot should auto join rooms, False otherwise.

  Returns:
      str: a message indicating the new state of the auto join feature
  """
  func_toggle_autojoin(matrix_join_rooms,configfile)
  return("Toggled auto join to " + str(config.matrix_join_rooms))


def func_handle_admin_reload(matrix_self,sync_headers):
  """Reload the config file and update the bot's settings accordingly.
  Args:
      matrix_self (object): the bot instance
      sync_headers (dict): the HTTP headers used for the sync request

  Returns:
      str: a message indicating that the config has been reloaded
  """
  importlib.reload(config)
  func_override_with_env(config)
  func_set_status(config.matrix_base_url, matrix_self, sync_headers, config.status_text, config.presence_state)
  return("Reloaded Config")


def func_handle_admin_leave(matrix_base_url,matrix_room,sync_headers):
  """Leave a room in the Matrix network.

  Args:
      matrix_base_url (str): the base URL of the Matrix server
      matrix_room (str): the ID of the room to leave
      sync_headers (dict): the HTTP headers used for the sync request
  """
  response = requests.post(matrix_base_url + "/_matrix/client/r0/rooms/" + matrix_room + "/leave", headers=sync_headers)

  if response.status_code == 200:
    func_write_to_log("Successfully left room " + matrix_room, "INFO", "main_loop")
  else:
    func_write_to_log("Failed to leave room %s" % response.text, "ERROR", "main_loop")
  return "left room"


def func_handle_admin_stop(matrix_base_url, access_token, user_agent, matrix_room, event_id, stat_dict):
  """Stop the bot and send a goodbye message.
  
  Args:
      matrix_base_url (str): the base URL of the Matrix server
      access_token (str): current session access token
      user_agent (str): user agent for talking to the api
      matrix_room (str): the ID of the room to send the message to
      event_id (str): the event ID of the message to reply to

  """
  func_send_message(matrix_base_url, access_token, user_agent, matrix_room, "Good By :wave:", event_id, stat_dict)
  func_write_to_log("stopping bot", "INFO", "func_handle_admin_stop")
  func_bot_stop()


def func_handle_admin_restart(matrix_base_url, access_token, user_agent, matrix_room, event_id, stat_dict,main_script_path):
  """Restart the bot and send a goodbye message.
  
  Args:
      matrix_base_url (str): the base URL of the Matrix server
      access_token (str): current session access token
      user_agent (str): user agent for talking to the api
      matrix_room (str): the ID of the room to send the message to
      event_id (str): the event ID of the message to reply to

  """
  func_send_message(matrix_base_url, access_token, user_agent, matrix_room, "See you soon :wave:", event_id, stat_dict)
  func_write_to_log("Restarting bot", "INFO", "func_handle_admin_restart")
  func_bot_restart(main_script_path)


def func_handle_admin_notify(matrix_room, teamspeak_version_notify_matrix_rooms, teamspeak_version_notify_file):
  """Toggles the notification feature for a specific room. If the room is already in the notification list, it will be removed. If not, it will be added.

  Args:
      matrix_room (str): the ID of the room to toggle notification for
      teamspeak_version_notify_matrix_rooms (list): list of rooms that are currently set to notify
      teamspeak_version_notify_file (str): path to the file containing the list of rooms to notify
  """
  if matrix_room in teamspeak_version_notify_matrix_rooms:
    return func_update_notify_room_remove(matrix_room, teamspeak_version_notify_file, teamspeak_version_notify_matrix_rooms)
  else:
    return func_update_notify_room_add(matrix_room, teamspeak_version_notify_file, teamspeak_version_notify_matrix_rooms)


def func_handle_admin_stats(stat_dict, stats_description):
  """Handle the stats command and send the stats to the chat

  Args:
      stat_dict (dict): dictionary with stats
      stats_description (dict): dictionary with descriptions of the stats

  Returns:
      str: formatted message with the stats
  """
  matrix_prepare_message = "Here are the stats I gathered so far:\n"
  for key in stat_dict:
    matrix_prepare_message += "\n"+stats_description[key]+": **" + str(stat_dict[key]) + "**"
  return(matrix_prepare_message)


def func_handle_admin_version(version):
  """Check the current version of the bot and compare it with the latest version available on GitHub. If a new version is available, send a message to the chat.

  Args:
      version (str): the current version of the bot

  Returns:
      str: a message indicating the current version and whether a new version is available
  """
  repo_api_url = "https://api.github.com/repos/Wargamer-Senpai/teampy/releases/latest"
  github_response = requests.get(repo_api_url)
  github_response_json = github_response.json()
  check_github = str(github_response_json.get("tag_name"))

  if check_github != "None":
    github_version = github_response_json["tag_name"]

    if github_response.status_code == 200:
      # Extrahiere das Release-Tag aus der JSON-Antwort
      func_write_to_log("Latest release tag is "+ github_version, "INFO", "main_loop")
    else:
      func_write_to_log("Error trying to fetch tag name from repo.", "ERROR", "main_loop")

    if LooseVersion(version) > LooseVersion(github_version):
      compare_version = "looks like your using an unreleased version :eyes:"
    elif LooseVersion(version) < LooseVersion(github_version):
      compare_version = "New Version on [GitHub](https://github.com/Wargamer-Senpai/teampy/releases/latest) available :eyes:"
    else:
      compare_version = ":sparkles: Your using the latest release :sparkles:"
  else:
    compare_version = "__Error while trying to fetch info from GitHub__"

  return("Current Version of teampy **" + version + "**"+ \
    "\n"+compare_version)
