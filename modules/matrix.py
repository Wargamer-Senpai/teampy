import inspect
import requests 
import time
import json

from modules.logger import func_write_to_log
from modules.stats import *

def func_matrix_login(matrix_base_url, matrix_username, matrix_password, user_agent):
  """login into matrix api and retreive the access token

  Args:
      matrix_base_url (str): the base URL of the Matrix server
      matrix_username (str): username for login
      matrix_password (str): password for login
      user_agent (str): user agent for talking to the api

  Returns:
      str: own matrix uui and current session access token
  """
  login_url = matrix_base_url + "/_matrix/client/r0/login"
  login_data = {"type": "m.login.password", "user": matrix_username, "password": matrix_password}
  login_headers = {"User-Agent": user_agent}
  response = requests.post(login_url, json=login_data, headers=login_headers)
  if response.json().get("access_token"):
    access_token = response.json()["access_token"]
    matrix_self = response.json()["user_id"]
    func_write_to_log("Login Successfull, own Matrix ID: " + matrix_self, "INFO", "startup_login")
  else: 
    func_write_to_log("Error Login failed, Username or Password wrong %s" % response.text, "ERROR", "startup_login")
    if "M_LIMIT_EXCEEDED" in response.text:
      func_write_to_log("Error: Too many login attempts, please wait and try again later", "ERROR", "startup_login")
    exit(1)
  
  return matrix_self, access_token

def func_matrix_sync(matrix_base_url,sync_base_url,sync_headers, sync_response):
  """sync current messages with matrix api

  Args:
      matrix_base_url (str): the base URL of the Matrix server
      sync_base_url (str): URL path for the sync endpoint
      sync_headers (dict): HTTP headers used for authentication and synchronization.
      sync_response (dict): The last sync response containing the token for the next batch

  Returns:
      requests.Response: the response from the sync request
  """
  try: 
    next_batch = sync_response["next_batch"]
  except KeyError:
    next_batch = "0"
  sync_url = matrix_base_url + sync_base_url + "&since=" + next_batch

  try:
    response = requests.get(sync_url, headers=sync_headers)
  except:
    # if the sync fails, try it again with delay
    time.sleep(10)
    response = requests.get(sync_url, headers=sync_headers)

  return response

def func_send_message(matrix_base_url, access_token, user_agent, matrix_room, matrix_send_message, event_id, stat_dict):
  """send a message to a room

  Args:
      matrix_base_url (str): the base URL of the Matrix server
      access_token (str): current session access token
      user_agent (str): user agent for talking to the api
      matrix_room (str): id of the room to send the message to
      matrix_send_message (str): message to send
      event_id (str): the event id of the message 
  
  Returns:
      int: status code of request 
  """
  current_function = inspect.currentframe().f_code.co_name
  if matrix_send_message:
    message_url = matrix_base_url + "/_matrix/client/r0/rooms/" + matrix_room + "/send/m.room.message"
    message_data = {"msgtype": "m.text", "body": matrix_send_message}
    message_headers = {"Authorization": "Bearer " + access_token, "User-Agent": user_agent}
    response = requests.post(message_url, json=message_data, headers=message_headers)
    matrix_send_message=""
    if response.status_code == 200:
      func_write_to_log("Message sent successfully! (room "+matrix_room+")", "INFO", current_function)
      func_add_stats("messages_send_count",stat_dict)
    else:
      func_write_to_log("Error sending message to Matrix: %s" % response.text, "ERROR", current_function)
      time.sleep(2)

    # set message to read, only works in privat chat
    try:
      payload = {"m.fully_read": event_id, "m.read": event_id}
      response = requests.post(matrix_base_url + "/_matrix/client/r0/rooms/" + matrix_room + "/read_markers", headers=message_headers, json=payload)
      if response.status_code == 200:
        func_write_to_log("Message successfully set to read!", "INFO", current_function)
      else:
        func_write_to_log("Error setting message to Read: %s" % response.text, "ERROR", current_function)
        time.sleep(2)
    except NameError:
      payload = {}
    
    return response.status_code



def func_check_invite(matrix_base_url, sync_headers, sync_base_url, matrix_join_rooms, sync_url, sync_response):
  """check if the bot is invited to a new room and join it

  Args:
      matrix_base_url (str): the base URL of the Matrix server
      sync_headers (dict): HTTP headers used for authentication and synchronization.
      sync_base_url (str): URL path for the sync endpoint
      matrix_join_rooms (bool): defines if the boot is allowed to join new groups
  """
  current_function = inspect.currentframe().f_code.co_name
  
  matrix_privat_request = ""
  check_current_rooms = str(sync_response.get("rooms"))
  if check_current_rooms != "None" and matrix_join_rooms == True:
    check_invite_key = str(sync_response["rooms"].get("invite")) 
    if check_invite_key != "None": 
      matrix_new_room = sync_response["rooms"]["invite"]
      matrix_new_room = list(matrix_new_room.keys())[0]

      #pretty print
      #print(json.dumps(sync_response["rooms"]["invite"],sort_keys=True, indent=4))
      for room in sync_response["rooms"]["invite"]:
        check_for_privat = str(sync_response["rooms"]["invite"][room]["invite_state"]["events"][3]["content"].get("is_direct")) 
        if check_for_privat != "None":
          matrix_privat_request += room +" "

      # send post request, to join the room
      for room in sync_response["rooms"]["invite"]:
        if room in matrix_privat_request:
          params = {"membership": "join"}
          response = requests.post(matrix_base_url + "/_matrix/client/r0/join/"+matrix_new_room, headers=sync_headers, params=params)
          if response.status_code == 200:
            func_write_to_log("successfully joined direct chat", "INFO", current_function)
          else:
            func_write_to_log("couldnt join direct chat ("+matrix_new_room+") %s" % response.text, "ERROR", current_function)
        else:
          response = requests.post(matrix_base_url + "/_matrix/client/r0/join/"+matrix_new_room, headers=sync_headers)
          
          if response.status_code == 200:
            name_url = matrix_base_url + "/_matrix/client/r0/rooms/"+matrix_new_room+"/state"
            response = requests.get(name_url, headers=sync_headers)
            response_room_name = response.json()[6]
            
            check_room_name = str(response_room_name.get("rooms"))

            if check_room_name != "None":
              room_name = response_room_name["content"]["name"]
            else:
              room_name = "privat room"
            func_write_to_log("successfully joined room (Name: "+room_name+")", "INFO", current_function)
          else:
            func_write_to_log("couldnt join room ("+matrix_new_room+") %s" % response.text, "ERROR", current_function)

      time.sleep(1)
      sync_url = matrix_base_url + sync_base_url + "&since=" + sync_response["next_batch"]
      response = requests.get(sync_url, headers=sync_headers)
      sync_response = json.loads(response.text)
      next_batch = sync_response["next_batch"]
      return next_batch


def func_set_status(matrix_base_url, matrix_self, sync_headers, status_text, config_presence_state):
  """set status message of bot

  Args:
      matrix_base_url (str): the base URL of the Matrix server
      matrix_self (str): the bots Matrix ID.
      sync_headers (dict): HTTP headers used for authentication and synchronization.
      status_text (str): text to display in status
      config_presence_state (str): presence
  """
  current_function = inspect.currentframe().f_code.co_name

  if status_text and config_presence_state:
    status_data = {"presence": config_presence_state, "status_msg": status_text}
    response = requests.put(matrix_base_url + "/_matrix/client/r0/presence/"+matrix_self+"/status", headers=sync_headers, json=status_data)
  if response.status_code == 200:
    func_write_to_log("Status message updated successfully.", "INFO", current_function)
  else:
    func_write_to_log("Failed to update status message. %s" % response.text, "ERROR", current_function)


def func_find_roomid(matrix_base_url, access_token, user_agent, user_identifiers):
  """get priv roomid with identifier 
  Problem: theres a 50/50 chance if the user is alone with the bot inside a group chat, 
           that the script gets confused and thinks the group chat is the privat chat, 
           instead of the real privat chat
  -> currently not used, but maybe in the future
           
  Args:
      matrix_base_url (str): the base URL of the Matrix server
      access_token (str): current session access token
      user_agent (str): user agent for talking to the api
      user_identifiers (list): a list of user identifiers to locate in private rooms.

  Returns:
      dict: a dictionary mapping each user identifier to its corresponding private room ID
  """
  user_room_ids = {}
  
  response = requests.get(matrix_base_url+"/_matrix/client/r0/joined_rooms",
             headers={"Authorization": f"Bearer {access_token}","User-Agent": user_agent})
  room_list = response.json().get("joined_rooms", [])
  for user_identifier in user_identifiers:
    for matrix_room in room_list:
      response = requests.get(matrix_base_url+"/_matrix/client/r0/rooms/"+matrix_room+"/members",
                 headers={"Authorization": f"Bearer {access_token}","User-Agent": user_agent})
      if response.status_code == 200:
        member_list = response.json().get("chunk", [])
        
        # Check if the room contains any of the specified users
        for member in member_list:
          if len(member_list) == 2 and member.get("state_key") in user_identifier:
            # Get room information
            response = requests.get(matrix_base_url+"/_matrix/client/r0/rooms/"+matrix_room+"/state",
                                    headers={"Authorization": f"Bearer {access_token}","User-Agent": user_agent})
            user_room_ids[user_identifier] = matrix_room
            break
      else:
        func_write_to_log("Error retrieving member list for room "+matrix_room+": " +response.status_code, "ERROR", "func_find_roomid")


  return user_room_ids


def func_get_room_mods_and_admins(matrix_base_url, matrix_room, access_token, user_agent):
  """Get the moderators and admins of a room.	

  Args:
      matrix_base_url (str): the base URL of the Matrix server
      matrix_room (str): the ID of the room to check
      access_token (str): current session access token
      user_agent (str): user agent for talking to the api

  Returns:
      list, list: list of admins and moderators in the room
  """
  url = f"{matrix_base_url}/_matrix/client/r0/rooms/{matrix_room}/state/m.room.power_levels"
  headers = {"Authorization": f"Bearer {access_token}", "User-Agent": user_agent}
  response = requests.get(url, headers=headers)
  if response.status_code != 200:
    func_write_to_log(f"Failed to get power levels for {matrix_room}: {response.text}", "ERROR", "get_room_mods_and_admins")
    return [], []

  data = response.json()
  users = data.get("users", {})
  admin_list = [user for user, level in users.items() if level >= 100]
  mod_list = [user for user, level in users.items() if 50 <= level < 100]
  return admin_list, mod_list


def func_is_private_chat(matrix_base_url, matrix_self, access_token, user_agent, matrix_room):
  """Check if the room is a private chat.

  Args:
      matrix_base_url (str): the base URL of the Matrix server
      matrix_self (str): the bot's identifier 
      access_token (str): current session access token
      user_agent (str): user agent for talking to the api
      matrix_room (str): the ID of the room to check

  Returns:
      bool: True if the room is a private chat, False otherwise
  """
  room_name = func_get_room_name(matrix_base_url, matrix_room, access_token, user_agent)
  if room_name == False:
    return True
  else:
    return False



def func_get_room_name(matrix_base_url, matrix_room, access_token, user_agent):
  """Get the name of a room by its ID.

  Args:
      matrix_base_url (str): the base URL of the Matrix server
      matrix_room (str): the ID of the room to check
      access_token (str): current session access token
      user_agent (str): user agent for talking to the api
  
  Returns:
      str: the name of the room, or None if not found
  """
  url = f"{matrix_base_url}/_matrix/client/r0/rooms/{matrix_room}/state/m.room.name"
  headers = {"Authorization": f"Bearer {access_token}", "User-Agent": user_agent}
  response = requests.get(url, headers=headers)

  if response.status_code == 200:
    return response.json().get("name", "").strip()
  elif response.status_code == 404:
    return False  # priavt room
  else:
    func_write_to_log(f"Failed to get room name: {response.text}", "ERROR", "get_room_name")
    return None


def func_delete_message(matrix_base_url, room_id, event_id, access_token, user_agent, reason=""):
  """Redacts (deletes) a message from a room.

  Args:
      matrix_base_url (str): The Matrix server base URL.
      room_id (str): The room from which to delete the message.
      event_id (str): The ID of the event (message) to delete.
      access_token (str): The bot's access token.
      user_agent (str): Custom user-agent string.
      reason (str): Optional reason for deletion.

  Returns:
      bool: True if deletion succeeded, False otherwise.
  """
  url = f"{matrix_base_url}/_matrix/client/r0/rooms/{room_id}/redact/{event_id}"
  headers = {
    "Authorization": f"Bearer {access_token}",
    "User-Agent": user_agent
  }
  payload = {"reason": reason} if reason else {}
  response = requests.post(url, headers=headers, json=payload)

  if response.status_code == 200:
    func_write_to_log(f"Deleted message {event_id} in room {room_id}", "INFO", "func_delete_message")
    return True
  else:
    func_write_to_log(f"Failed to delete message {event_id}: {response.status_code} - {response.text}", "ERROR", "func_delete_message")
    return False

# def func_set_avatar():
#   """set avatar 
#   ! not possible ! -> teamspeak uses a different endpoint for uploading images/profile pictures 
#   """
#   if config.avatar_url:
#     current_function = inspect.currentframe().f_code.co_name
#    
#     avatar_data = {"avatar_url": config.avatar_url} 
#     response = requests.put(matrix_base_url + "/_matrix/client/r0/profile/"+matrix_self+"/avatar_url", headers=sync_headers, json=avatar_data)
#     if response.status_code == 200:
#       response = requests.get(matrix_base_url + "/_matrix/client/r0/profile/"+matrix_self+"/avatar_url", headers=sync_headers)
#       new_avatar_url = response.json()
#       func_write_to_log("Bot avatar changed successfully. ("+ new_avatar_url +")", "INFO", current_function)
#     else:
#       func_write_to_log("Failed to change bot avatar. %s" % response.text, "ERROR", current_function)