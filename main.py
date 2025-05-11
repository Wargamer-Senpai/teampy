#!/usr/bin/env python3
# The teampy bot, a simple command bot
# Created 2023-03-16
# by DerSafterXD & WargamerSenpai
#
# 
# Not working Features: 
# - set avatar
# - sending images 
# Background: teamspeak uses a diffrent url for uploading the images, then in the documentation
#
# Credits: 
# Gamer08YT helped with the user agent for the teamspeak Matrix Server

import os
import platform
import time
import json

try:
  # import config.py
  import config 
except:
  func_write_to_log("Config file not found, please copy config.py.example to config.py and edit it", "ERROR", "startup")
  print("Config file not found, please copy config.py.example to config.py and edit it")
  sys.exit(255)

from modules.config_manager import * 
# apply overrides once, before you use any config values
func_override_with_env(config)

from modules.admin import * 
from modules.bot_control import * 
from modules.commands import * 
from modules.health import * 
from modules.logger import * 
from modules.matrix import * 
from modules.notify import * 
from modules.stats import * 
from modules.teamspeak_updates import * 
from modules.utils import * 
from modules.version import * 



# Script
main_script_path = os.path.dirname(os.path.abspath(__file__))
os_name = platform.system()
configfile = os.path.join(main_script_path,"config.py")

# API 
## url for syncing, 20000ms -> 20 seconds
sync_base_url = "/_matrix/client/r0/sync?20000"
sync_url = config.matrix_base_url + sync_base_url
# special User Agent for teamspeak matrix, dont touch or else it is broken
user_agent = "Go-http-client/2.0"
matrix_received_message = ""
data = {}
access_token = ""

# etc
check_invite_key = ""
sync_response = {}
sync_headers = {}
matrix_self = ""
matrix_privat_request = ""
user_room_ids = {}


# Rank / Commands
rank_error_message = "It looks like you dont have the permission for that!"
command_disabled_message = "The command is disabled :eyes:"


# teamspeak update checker 
teamspeak_version_check_interval = 120 
teamspeak_version_last_check_time = time.time()
teamspeak_version_saved = "" 
teamspeak_version_request = "" 
teamspeak_version_notify_matrix_rooms = () 
teamspeak_version_notify_file = os.path.join(main_script_path,"data","notify.txt") 

# stats
stat_dict = {}
stats_file = os.path.join(main_script_path,"data", "stats.txt")
stats_description = {
  "messages_send_count": "How many Messages were sent",
  "gifs_count": "How many gifs were sent",
  "startup_count": "How many times the bot started",
  "help_command_count": "help command count", 
  "stats_command_count": "stats command count",
  "btc_command_count": "BTC command count",
  "eth_command_count": "ETH command count",
  "whoami_command_count": "whoami command count",
  "whois_command_count": "whois command count",
  "ping_command_count": "ping command count",
  "roll_command_count": "roll command count",
  "poll_command_count": "poll command count",
  "admin_command_count": "admin command count"
}

# some preset emojis if the poll has no emojis set
poll_emojis = [":+1:",":-1:",":wave:",":ok_hand:",":100:",":pinch:"]


def func_create_command_handlers(matrix_received_message,matrix_room,event_id,matrix_sender,sync_headers,teamspeak_version_notify_matrix_rooms,configfile,access_token,matrix_self,matrix_room_name):
  """Create a mapping of chat commands to their respective handler functions.

    This function constructs a dictionary where each key is a command string and the corresponding
    value is a dictionary containing the handler function, a statistic counter key, and any additional
    parameters required by the handler. This mapping enables the bot to route incoming messages to the
    appropriate command handler.

  Args:
      matrix_received_message (str): the received message from the chat
      matrix_room (str): the identifier of the Matrix room where the message was received

  Returns:
      dct: a dictionary mapping command identifiers to their handler configurations
  """
  command_handlers = {
    config.command_gif: {
      "command": func_handle_gif,
      "stat": "gifs_count",
      "params": {
        "command_prefix": config.command_prefix, 
        "command_gif": config.command_gif, 
        "giphy_api_key": config.giphy_api_key, 
        "matrix_received_message": matrix_received_message
      }
    },
    config.command_btc: {
      "command": func_handle_crypto,
      "stat": "btc_command_count",
      "params": {
        "crypto_currency": "bitcoin"
      }
    },
    config.command_eth: {
      "command": func_handle_crypto,
      "stat": "eth_command_count",
      "params": {
        "crypto_currency": "ethereum"
      }
    },
    config.command_help: {
      "command": func_handle_help,
      "stat": "help_command_count",
      "params": {
        "commands_overview": config.commands_overview,
        "command_prefix": config.command_prefix,
      }
    },
    config.command_whoami: {
      "command": func_handle_whoami,
      "stat": "whoami_command_count",
      "params": {
        "matrix_base_url": config.matrix_base_url,
        "sync_headers": sync_headers,
        "bot_admin": config.bot_admin,
        "matrix_sender": matrix_sender
      }
    },
    config.command_whois: {
      "command": func_handle_whois,
      "stat": "whois_command_count",
      "params": {
        "matrix_base_url": config.matrix_base_url,
        "sync_headers": sync_headers,
        "matrix_received_message": matrix_received_message,
        "bot_admin": config.bot_admin
      }
    },
    config.command_stats: {
      "command": func_handle_stats,
      "stat": "stats_command_count",
      "params": {
        "stats_visible": config.stats_visible,
        "stat_dict": stat_dict,
        "bot_admin": config.bot_admin,
        "stats_description": stats_description,
        "matrix_sender": matrix_sender
      }
    },
    config.command_ping: {
      "command": func_handle_ping,
      "stat": "ping_command_count",
      "params": {}
    },
    config.command_dice: {
      "command": func_handle_roll,
      "stat": "roll_command_count",
      "params": {}
    },
    config.command_poll: {
      "command": func_handle_poll,
      "stat": "poll_command_count",
        "params": {
        "matrix_received_message": matrix_received_message,
        "poll_emojis": poll_emojis
      }
    },
    # admin commands  
    config.command_admin_help: {
      "command": func_handle_admin_help,
      "stat": "admin_command_count",
      "params": {
        "admin_commands_overview": config.admin_commands_overview,
        "command_prefix": config.command_prefix
      }
    },
    config.command_admin_autojoin: {
      "command": func_handle_admin_autojoin,
      "stat": "admin_command_count",
      "params": {
        "matrix_join_rooms": config.matrix_join_rooms,
        "configfile": configfile
      }
    },
    config.command_admin_reload: {
      "command": func_handle_admin_reload,
      "stat": "admin_command_count",
      "params": {
        "matrix_self": matrix_self,
        "sync_headers": sync_headers
      }
    },
    config.command_admin_moderation_toggle: {
      "command": func_handle_admin_moderation_toggle,
      "stat": "admin_command_count",
      "params": {
        "matrix_base_url": config.matrix_base_url, 
        "matrix_room": matrix_room, 
        "sync_headers": sync_headers,
        "matrix_self": matrix_self,
        "matrix_room_name": matrix_room_name
      }
    },
    config.command_admin_leave: {
      "command": func_handle_admin_leave,
      "stat": "admin_command_count",
      "params": {
        "matrix_base_url": config.matrix_base_url,
        "matrix_room": matrix_room,
        "sync_headers": sync_headers
      }
    },
    config.command_admin_health: {
      "command": func_health_check,
      "stat": "admin_command_count",
      "params": {
        "main_script_path": main_script_path,
        "matrix_base_url": config.matrix_base_url,
        "matrix_username": config.matrix_username,
        "matrix_password": config.matrix_password,
      }
    },
    config.command_admin_stop: {
      "command": func_handle_admin_stop,
      "stat": "admin_command_count",
      "params": {
        "matrix_base_url": config.matrix_base_url,
        "sync_headers": sync_headers,
        "matrix_room": matrix_room,
        "event_id": event_id,
        "stat_dict": stat_dict
      }
    },
    config.command_admin_restart: {
      "command": func_handle_admin_restart,
      "stat": "admin_command_count",
      "params": {
        "matrix_base_url": config.matrix_base_url,
        "sync_headers": sync_headers,
        "matrix_room": matrix_room,
        "event_id": event_id,
        "stat_dict": stat_dict,
        "main_script_path": main_script_path
      }
    },
    config.command_admin_notify: {
      "command": func_handle_admin_notify,
      "stat": "admin_command_count",
      "params": {
        "matrix_room": matrix_room,
        "teamspeak_version_notify_matrix_rooms": teamspeak_version_notify_matrix_rooms,
        "teamspeak_version_notify_file": teamspeak_version_notify_file
      }
    },
    config.command_admin_stats: {
      "command": func_handle_admin_stats,
      "stat": "admin_command_count",
      "params": {
        "stat_dict": stat_dict,
        "stats_description": stats_description
      }
    },
    config.command_admin_list_banned_users: {
      "command": func_handle_admin_list_banned_users,
      "stat": "admin_command_count",
      "params": {
        "matrix_base_url": config.matrix_base_url, 
        "matrix_room": matrix_room, 
        "sync_headers": sync_headers
      }
    },
    config.command_admin_unban_user: {
      "command": func_handle_admin_unban_user,
      "stat": "admin_command_count",
      "params": {
        "matrix_base_url": config.matrix_base_url, 
        "matrix_room": matrix_room, 
        "matrix_received_message": matrix_received_message, 
        "sync_headers": sync_headers
      }
    },
    config.command_admin_version: {
      "command": func_handle_admin_version,
      "stat": "admin_command_count",
      "params": {
        "version": version,
      }
    }
  }
  return command_handlers



def func_dispatch_command(matrix_received_message, matrix_sender, matrix_room, event_id, access_token, sync_headers, teamspeak_version_notify_matrix_rooms, configfile, matrix_self, matrix_room_name):
  """Process a message to handle commands for the Matrix bot.
   
    This function examines a received message to determine if it contains a command based on the
    configured command prefix. It validates whether the command is enabled and, for admin commands,
    checks the sender's privileges. Upon a valid command, it executes the corresponding command handler,
    updates usage statistics, and sends appropriate feedback. If the message starts with the command
    prefix but does not match any known command, it handles the situation by delegating to plugins or
    sending a "command not found" message.
  
  Args:
      matrix_received_message (str): the incoming message text
      matrix_sender (str): the identifier of the sender
      matrix_room (str): the room identifier where the message was received
      event_id (str): the event id of the message 

  Returns:
      bool: True if the command was successfully processed, False otherwise
  """
  for command, data in func_create_command_handlers(matrix_received_message,matrix_room,event_id,matrix_sender,sync_headers,teamspeak_version_notify_matrix_rooms,configfile,access_token,matrix_self,matrix_room_name).items():
    if matrix_received_message.startswith(config.command_prefix + command):
      if (command in config.commands_overview and config.commands_overview[command]["command_enabled"]
         ) or (command in config.admin_commands_overview and config.admin_commands_overview[command]["command_enabled"]):
        if matrix_received_message.startswith(config.command_prefix + config.command_base_admin):
          if not matrix_sender in config.bot_admin:
            func_send_message(config.matrix_base_url,sync_headers, matrix_room, rank_error_message, event_id, stat_dict)
            return False 
            
        # Get any additional parameters (default to an empty dict)
        params = data.get("params", {})
        # Call the command function, passing message and any extra parameters
        result = data["command"](**params)
        func_add_stats(data["stat"],stat_dict)
        if result:
          if result != "left room":
            func_send_message(config.matrix_base_url,sync_headers, matrix_room, result, event_id, stat_dict)
            return True 
          else: 
            return True
        else: 
          func_send_message(config.matrix_base_url,sync_headers, matrix_room, "Command didnt respond or returned anything - but i think it was successfull :eyes:", event_id, stat_dict)
          return True
      else:
        func_send_message(config.matrix_base_url,sync_headers, matrix_room, command_disabled_message, event_id, stat_dict)
        return False 

  # If the message starts with the command prefix but doesn't match any command,
  # send a "command not found" message.
  if matrix_received_message.startswith(config.command_prefix):
    if config.plugins_on:
      plugin_output = func_handle_plugins(matrix_sender, config.bot_admin, main_script_path, matrix_received_message, config.command_prefix)
      if plugin_output:
        # plugin_output is a non-empty string → send it back to the room
        func_send_message(config.matrix_base_url,sync_headers,matrix_room, plugin_output, event_id, stat_dict)
        return True
      func_send_message(config.matrix_base_url,sync_headers, matrix_room, f"Command not found :thinking: ({matrix_received_message})\nif you need more info use `{config.command_prefix+config.command_help}`", event_id, stat_dict)
      return False 

  return False  # No command matched and does not match to command prefix


def func_startup_check(stats_file,teamspeak_version_notify_matrix_rooms,teamspeak_version_notify_file):
  """Perform startup checks and initializations for the bot

  Returns:
      tuple: A tuple containing:
          - sync_response (dict): the JSON response from the initial sync request
          - sync_headers (dict): the HTTP headers used for the sync request
  """
  if func_container_check():
    func_write_to_log("!! running inside a container !!", "INFO", "startup_container_check")
  else:
    func_write_to_log("not running inside a container", "INFO", "startup_container_check")
    
  if not config.matrix_username or not config.matrix_password:
    func_write_to_log("finish configuration step first! (username and/or password empty)", "ERROR", "startup")
    exit(1)

  matrix_self, access_token = func_matrix_login(config.matrix_base_url, config.matrix_username, config.matrix_password, user_agent)

  func_write_to_log("starting bot....", "INFO", "startup")
  if os_name == "Windows": 
    func_write_to_log("Detected Windows", "DEBUG", "startup")
  elif os_name == "Linux":
    func_write_to_log("Detected Linux", "DEBUG", "startup")
  else:
    func_write_to_log("Couldnt detect OS ("+os_name+"), script wont work well!", "CRITICAL", "startup")

  # check if stats file exists
  if not os.path.exists(stats_file):
    # if not create it with preset
    with open(stats_file, "w") as f:
      f.write("messages_send_count=0\n"
              "gifs_count=0\n"
              "startup_count=0\n"
              "help_command_count=0\n"
              "btc_command_count=0\n"
              "eth_command_count=0\n"
              "whoami_command_count=0\n"
              "whois_command_count=0\n"
              "ping_command_count=0\n"
              "roll_command_count=0\n"
              "poll_command_count=0\n"
              )
      
  try: 
    with open(stats_file, "r") as f:
      for line in f:
        key, value = line.strip().split("=")
        stat_dict[key] = int(value)
  except ValueError:
    func_write_to_log(f"Error reading stats file ({stats_file}), please delete it and restart the bot", "ERROR", "startup")
    exit(255)

  # initial sync of messages and events
  sync_headers = {"Authorization": "Bearer " + access_token, "User-Agent": user_agent}
  next_batch = None
  #make initial request (so he ignores old chats)
  response = requests.get(sync_url, headers=sync_headers)
  sync_response = json.loads(response.text)

  func_check_invite(config.matrix_base_url, sync_headers, sync_base_url, config.matrix_join_rooms, sync_url, sync_response)
  func_set_status(config.matrix_base_url,matrix_self,sync_headers,config.status_text,config.presence_state)
  func_add_stats("startup_count",stat_dict)
  func_check_client_update(config.matrix_base_url,sync_headers, teamspeak_version_notify_matrix_rooms, config.matrix_update_message, teamspeak_version_saved, teamspeak_version_notify_file, 0,stat_dict)
  teamspeak_version_notify_matrix_rooms = func_update_notify_rooms_get(teamspeak_version_notify_file) 
  func_write_to_log(f"current rooms to notify: {teamspeak_version_notify_matrix_rooms}", "INFO", "startup_finished")
  func_write_to_log("Startup complete...", "INFO", "startup_finished")
  func_write_stats_to_file(stat_dict, stats_file)

  return sync_response, sync_headers, access_token, matrix_self, teamspeak_version_notify_matrix_rooms


def func_main(teamspeak_version_last_check_time, stats_file, teamspeak_version_notify_matrix_rooms, teamspeak_version_notify_file, configfile):
  """Main loop to continuously synchronize and process Matrix events.

    This function initializes synchronization with the Matrix server by calling func_startup_check() to
    retrieve the initial sync response and headers. It then enters an infinite loop that:
      - Ensures the container remains active (if an container) via a watchdog check
      - Periodically verifies for Teamspeak client updates.
      - Synchronizes with the Matrix API to retrieve new events and messages.
      - Processes incoming message events by logging details and dispatching commands.
      - Checks for room invitations and handles them accordingly.
  """
  sync_response, sync_headers, access_token, matrix_self, teamspeak_version_notify_matrix_rooms = func_startup_check(stats_file,teamspeak_version_notify_matrix_rooms,teamspeak_version_notify_file)

  while True:
    time.sleep(1)
    # make sure that the watchdog doesnt kill the container
    if func_container_check():
      func_touch_file("check_container")

    # check for new update of ts client
    elapsed_time = time.time() - teamspeak_version_last_check_time
    if elapsed_time >= teamspeak_version_check_interval: 
      teamspeak_version_last_check_time = time.time()
      func_check_client_update(config.matrix_base_url,sync_headers, teamspeak_version_notify_matrix_rooms, config.matrix_update_message, teamspeak_version_saved, teamspeak_version_notify_file, 0,stat_dict)


    response = func_matrix_sync(config.matrix_base_url, sync_base_url, sync_headers, sync_response)

    # check if the response was successful
    if response.status_code == 200:
      # parse the response JSON to extract any new events
      sync_response = json.loads(response.text)

      check_current_rooms = str(sync_response.get("rooms"))
      if check_current_rooms != "None":
        check_active_rooms = str(sync_response["rooms"].get("join"))
        if check_active_rooms != "None":
          # check if in any room is something new, if not just wait and retry
          if "rooms" in sync_response and sync_response["rooms"] is not None:
            # check if there are any new messages in the room
            for matrix_room in sync_response["rooms"]["join"]:
              # Loop through all new events in the room
              for event in sync_response["rooms"]["join"][matrix_room]["timeline"]["events"]:
                # check if the event is a message
                if event["type"] == "m.room.message" and event["sender"] != matrix_self:
                  # Print the message body, need to changed to loggin into a file
                  matrix_sender = event["sender"]
                  matrix_sender_name = func_get_username(config.matrix_base_url,matrix_sender,sync_headers)
                  matrix_event_id = event["event_id"]
                  matrix_received_message = event["content"]["body"]
                  matrix_room_name = func_get_room_name(config.matrix_base_url, matrix_room,sync_headers)
                  matrix_room_join_rule = func_get_room_join_rule(config.matrix_base_url, matrix_room, sync_headers)
                  room_mods, room_admins = func_get_room_mods_and_admins(config.matrix_base_url, matrix_room,sync_headers)
                  func_write_to_log(matrix_sender  + ": " + matrix_received_message +" (room: "+ matrix_room +")", "INFO", "main_loop")
                  func_write_to_log(json.dumps(event,sort_keys=True, indent=4), "DEBUG", "main_loop")
                  
                  # checks and handles the received message
                  command_succesfull = func_dispatch_command(matrix_received_message, matrix_sender, matrix_room, matrix_event_id, access_token, sync_headers, teamspeak_version_notify_matrix_rooms, configfile, matrix_self, matrix_room_name)
                  func_write_stats_to_file(stat_dict, stats_file)
                  teamspeak_version_notify_matrix_rooms = func_update_notify_rooms_get(teamspeak_version_notify_file) 
                  if func_is_moderation_enabled(matrix_room):
                    violation, reason = func_check_violation(main_script_path, matrix_received_message, matrix_sender, room_admins, room_mods)
                    if violation:
                      message, warn_count = func_warn_user(matrix_room, matrix_sender, reason)
                      func_delete_message(config.matrix_base_url, matrix_room, matrix_event_id,sync_headers, reason)
                      func_send_message(config.matrix_base_url,sync_headers, matrix_room, message, matrix_event_id, stat_dict)
                      if warn_count >= config.warn_limit:
                        if matrix_room_join_rule == "public": 
                          if func_ban_user(config.matrix_base_url, matrix_room, matrix_sender,sync_headers, reason):
                            func_write_to_log(f"User {matrix_sender} has been banned for violating the rules too often (reason: {reason})", "INFO", "main_loop")
                            func_send_message(config.matrix_base_url,sync_headers, matrix_room, f"User {matrix_sender_name} have been banned for violating the rules too often", matrix_event_id, stat_dict)
                          else: 
                            func_write_to_log(f"Failed to ban user {matrix_sender} for violating the rules too often (reason: {reason})", "ERROR", "main_loop")
                            func_send_message(config.matrix_base_url,sync_headers, matrix_room, f"Failed to ban user {matrix_sender_name} for violating the rules too often (reason: {reason})", matrix_event_id, stat_dict)

                        else: 
                          # the reasons for a kick only in privat chats, is that teamspeak currently has no ban ui seaction in privat rooms
                          # so if you ban someone in a privat room, he can just rejoin and not be invated again and i would need to build a function to unban somebody that nobody sees in the ui
                          if func_kick_user(config.matrix_base_url, matrix_room, matrix_sender,sync_headers, reason):  
                            func_write_to_log(f"User {matrix_sender} has been kicked for violating the rules too often", "INFO", "main_loop")
                            func_send_message(config.matrix_base_url,sync_headers, matrix_room, f"User {matrix_sender_name} have been kicked for violating the rules too often", matrix_event_id, stat_dict)
                          else:
                            func_write_to_log(f"Failed to kick user {matrix_sender} for violating the rules too often (reason: {reason})", "ERROR", "main_loop")
                            func_send_message(config.matrix_base_url,sync_headers, matrix_room, f"Failed to kick user {matrix_sender_name} for violating the rules too often (reason: {reason})", matrix_event_id, stat_dict)

      else:
        time.sleep(5)
        response = func_matrix_sync(config.matrix_base_url, sync_base_url, sync_headers, sync_response)
     
      # check if he got invited into a new room 
      next_batch = func_check_invite(config.matrix_base_url, sync_headers, sync_base_url, config.matrix_join_rooms, sync_url, sync_response)
      if next_batch:
        sync_response["next_batch"] = next_batch
    else:
      func_write_to_log("Error getting messages from Matrix: %s" % response.text, "DEBUG", "main_loop")
      exit(255)



if __name__ == "__main__":
  """Entry point: when the script is executed directly, start the main loop.
  """
  func_main(teamspeak_version_last_check_time, stats_file, teamspeak_version_notify_matrix_rooms, teamspeak_version_notify_file, configfile)