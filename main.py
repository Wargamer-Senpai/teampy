#!/usr/bin/env python3
# The teampy bot, a simple command bot
# Created 2023-03-16
# by DerSafterXD & WargamerSenpai
#
# 
# 
# 
# 
# 
# Not working Features: 
# - set avatar
# - sending images 
# Background: teamspeak uses a diffrent url for uploading the images, then in the documentation
#
# Credits: 
# ChatGPT helped creating the code
# Gamer08YT helped with the user agent for the teamspeak Matrix Server

#
# imports
#
import requests
import json
import time
import random
import subprocess
import platform
import os
import sys
import importlib
from distutils.version import LooseVersion
import logging
import datetime
import inspect

# import config.py
import config 
# import bad_words.py
from modules.bad_words import * 
# import version.py file
from modules.version import * 


#####################
#                   #
# script variables  #
#                   #
#####################

# special User Agent for teamspeak matrix, dont touch or else it is broken
user_agent = "Go-http-client/2.0"


# url for syncing
sync_url = "/_matrix/client/r0/sync?3000"
# tmp variable for preparing the message for sending
matrix_prepare_message = ""
# data from api
data = {}
# check new invite 
check_invite_key = ""
# anwser from matrix sync
sync_response = {}
# http header for sync
sync_headers = {}
# matrix id from bot itself
matrix_self = ""
# access token from matrix, requested on every startup
access_token = ""
# get os windows/linux
os_name = platform.system()
# saves rooms that are privat chat, when invite received
matrix_privat_request = ""
# get current execution directory 
script_path = os.path.dirname(os.path.abspath(__file__))
# error message if user doesnt have permission
rank_error_message = "It looks like you dont have the permission for that!"
# info message if a command is disabled
command_disabled_message = "The command is disabled :eyes:"
# interval the ts version gets checked, in seconds
interval = 120
# start time for time check
start_time = time.time()
# variables for ts5 client version
ts_version_saved = ""
ts_version_request = ""
# rooms to notify on new update
matrix_notify_rooms = ()
# get current script path
main_script_path = os.path.dirname(os.path.abspath(__file__))
# the file where all stats are saved to
stats_file = os.path.join(main_script_path,"modules", "stats.txt")

# description for stats
stats_description = {
  "messages_send_count": "How many Messages were sent",
  "gifs_count": "How many gifs were sent",
  "startup_count": "How many times the bot started",
  "help_command_count": "help command count", 
  "btc_command_count": "BTC command count",
  "eth_command_count": "ETH command count",
  "whoami_command_count": "whoami command count",
  "whois_command_count": "whois command count",
  "ping_command_count": "ping command count",
  "roll_command_count": "roll command count",
  "poll_command_count": "poll command count"
}
# some preset emojis if the poll has no emojis set
poll_emojis = [":+1:",":-1:",":wave:",":ok_hand:",":100:",":pinch:"]
# set log file 
log_file = os.path.join(main_script_path, "logs","output_" + datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
# set debug mode
debug_mode = False
# file for saving the chats, that get notified
notify_file = os.path.join("modules","notify.txt")


###############
#             #
#  functions  #
#             #
###############

#######################
# return current time #
#######################
def func_time_now():
  return str(datetime.datetime.now())


#####################
# write to log file #
#####################
def func_write_to_log(log_message, log_level, log_function):
  # fallback if conf_log_level has been wrongly configured
  if not config.log_level in ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]:
    config.log_level = "INFO"


  # prepare logging file
  # log file format: output_YYYY-MM-DD_HH-MM-SS.log
  logging.basicConfig(filename=log_file, level=config.log_level, format='%(asctime)s - %(levelname)s - %(message)s')
  log_message = log_function + " - " + log_message 
  
  # print to cli if started in debug mode
  if debug_mode == True:
    print(func_time_now() + " - " + log_level + " - " + log_function + " - " + log_message)

  if log_level == "CRITICAL":
    logging.critical(log_message)
  elif log_level == "ERROR": 
    logging.error(log_message)
  elif log_level == "WARNING":
    logging.warn(log_message)
  elif log_level == "INFO":
    logging.info(log_message)
  else:
    logging.debug(log_message)


########################
# send message to room #
########################
def func_send_message(matrix_send_message):
  current_function = inspect.currentframe().f_code.co_name
  global matrix_sender
  global matrix_prepare_message
  global script_path
  if matrix_send_message:
    message_url = config.matrix_base_url + "/_matrix/client/r0/rooms/" + room_id + "/send/m.room.message"
    message_data = {"msgtype": "m.text", "body": matrix_send_message}
    message_headers = {"Authorization": "Bearer " + access_token, "User-Agent": user_agent}
    response = requests.post(message_url, json=message_data, headers=message_headers)
    matrix_send_message=""
    if response.status_code == 200:
      func_write_to_log("Message sent successfully! (room "+room_id+")", "INFO", current_function)
      func_add_stats("messages_send_count")
    else:
      func_write_to_log("Error sending message to Matrix: %s" % response.text, "ERROR", current_function)
      time.sleep(2)

    # set message to read, only works in privat chat
    payload = {"m.fully_read": event["event_id"], "m.read": event["event_id"]}
    response = requests.post(config.matrix_base_url + "/_matrix/client/r0/rooms/" + room_id + "/read_markers", headers=message_headers, json=payload)
    
    if response.status_code == 200:
      func_write_to_log("Message successfully set to read!", "INFO", current_function)
    else:
      func_write_to_log("Error setting message to Read: %s" % response.text, "ERROR", current_function)
      time.sleep(2)

    # write new stats to file
    with open(stats_file, "w") as f:
        for key, value in stat_dict.items():
            f.write(str(key) + "=" + str(value) + "\n")

    time.sleep(1)

    matrix_sender = "" #clear sender of message
    matrix_prepare_message = ""


####################################
# check if new invite is available #
####################################
def func_check_invite():
    current_function = inspect.currentframe().f_code.co_name
    
    global sync_response
    global sync_url
    global next_batch
    matrix_privat_request = ""
    check_current_rooms = str(sync_response.get("rooms"))
    if check_current_rooms != "None" and config.matrix_join_rooms == True:
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
            response = requests.post(config.matrix_base_url + "/_matrix/client/r0/join/"+matrix_new_room, headers=sync_headers, params=params)
            if response.status_code == 200:
              func_write_to_log("successfully joined direct chat", "INFO", current_function)
            else:
              func_write_to_log("couldnt join direct chat ("+matrix_new_room+") %s" % response.text, "ERROR", current_function)
          else:
            response = requests.post(config.matrix_base_url + "/_matrix/client/r0/join/"+matrix_new_room, headers=sync_headers)
            
            if response.status_code == 200:
              name_url = config.matrix_base_url + "/_matrix/client/r0/rooms/"+matrix_new_room+"/state"
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
        response = requests.get(sync_url, headers=sync_headers)
        next_batch = sync_response["next_batch"]
        sync_url = config.matrix_base_url + "/_matrix/client/r0/sync?since=" + next_batch
        response = requests.get(sync_url, headers=sync_headers)
        next_batch = sync_response["next_batch"]


###################################################
# set avatar, currently not known where to upload #
###################################################
def func_set_avatar():
  if config.avatar_url:
    current_function = inspect.currentframe().f_code.co_name
    
    avatar_data = {"avatar_url": config.avatar_url} 
    response = requests.put(config.matrix_base_url + "/_matrix/client/r0/profile/"+matrix_self+"/avatar_url", headers=sync_headers, json=avatar_data)
    if response.status_code == 200:
      response = requests.get(config.matrix_base_url + "/_matrix/client/r0/profile/"+matrix_self+"/avatar_url", headers=sync_headers)
      new_avatar_url = response.json()
      func_write_to_log("Bot avatar changed successfully. ("+ new_avatar_url +")", "INFO", current_function)
    else:
      func_write_to_log("Failed to change bot avatar. %s" % response.text, "ERROR", current_function)


###################################
# set status message and presence #
###################################
def func_set_status():
    current_function = inspect.currentframe().f_code.co_name
    
    if config.status_text and config.presence_state:
      status_data = {"presence": config.presence_state, "status_msg": config.status_text}
      response = requests.put(config.matrix_base_url + "/_matrix/client/r0/presence/"+matrix_self+"/status", headers=sync_headers, json=status_data)
    if response.status_code == 200:
      func_write_to_log("Status message updated successfully.", "INFO", current_function)
    else:
      func_write_to_log("Failed to update status message. %s" % response.text, "ERROR", current_function)


###########################
# send gif with giphy api #
###########################
def func_send_gif():
  if config.giphy_api_key:
    message_index = matrix_received_message.find(" ")
    #get search string, if available
    giphy_search_string = matrix_received_message[message_index+1:] 

    if not config.command_prefix + config.command_gif ==  giphy_search_string:
      random_gif = random.randint(0, 30)
      url = "https://api.giphy.com/v1/gifs/search?api_key="+config.giphy_api_key+"&q="+giphy_search_string+"&limit=1&offset="+str(random_gif)+"&rating=g&lang=en"
    else:
      url = "https://api.giphy.com/v1/gifs/random?api_key="+config.giphy_api_key+"&tag=&rating=r"

    response = requests.get(url)
    data = response.json()

    if not config.command_prefix + config.command_gif ==  giphy_search_string:
      if len(data["data"]) > 0:
        func_send_message(data['data'][0]['images']['original']['url'])
      else:
        func_send_message("couldnt find your search string (404)")
    else:
      func_send_message(data['data']['images']['original']['url'])
  else:
    func_send_message("i have a problem, the api key is missing in the config, please contact the admin :anxious:")


#################################
# check for update of teamspeak #
#################################
def func_check_client_update():
  global ts_version_saved
  global ts_version_request
  current_function = inspect.currentframe().f_code.co_name
  request_version_header = {"Authorization": "Basic dGVhbXNwZWFrNTpMRlo2Wl5rdkdyblh+YW4sJEwjNGd4TDMnYTcvYVtbJl83PmF0fUEzQVJSR1k=", "User-Agent": "teamspeak.downloader/1.0"}
  request_version_url= "http://update.teamspeak.com/windows/x64/latest/info.json"
  version_response = requests.get(request_version_url, headers=request_version_header, auth=("teamspeak5", "LFZ6Z^kvGrnX~an,$L#4gxL3'a7/a[[&_7>at}A3ARRGY"))
  ts_version_request = version_response.json()["version_string"]
  func_write_to_log("Version Check for Client: " + str(ts_version_request), "INFO", current_function)
  if ts_version_request:
    if ts_version_saved:
      if ts_version_saved != ts_version_request:
        ts_version_saved = ts_version_request
        func_notify_update()

    else:
      ts_version_saved = ts_version_request


########################################################     
# send a message to the chats that want to be notified #
########################################################
def func_notify_update():
  current_function = inspect.currentframe().f_code.co_name
  if matrix_notify_rooms:
    for room_id in matrix_notify_rooms:
      message_url = config.matrix_base_url + "/_matrix/client/r0/rooms/" + room_id + "/send/m.room.message"
      message_data = {"msgtype": "m.text", "body": config.matrix_update_message + ts_version_saved}
      message_headers = {"Authorization": "Bearer " + access_token, "User-Agent": user_agent}
      response = requests.post(message_url, json=message_data, headers=message_headers)
      if not response.status_code == 200:
        func_write_to_log("couldnt notify room: " + room_id + ", probably not member of the room anymore.  %s" % response.text, "ERROR", current_function)
        if response.text["errcode"] == "M_FORBIDDEN":
          func_write_to_log("removing room (" + room_id + ") from notifing", "INFO", current_function)
          func_notify_room_remove(room_id)


####################################################
# add a room to notify group if a update was found #
####################################################
def func_notify_room_add(room_id):
  global matrix_notify_rooms
  current_function = inspect.currentframe().f_code.co_name

  if not room_id in matrix_notify_rooms:
    func_write_to_log("added " + room_id + " to notify group", "INFO", current_function)
    matrix_notify_rooms = matrix_notify_rooms + (room_id,)
    file_content = " ".join(matrix_notify_rooms)
    with open(notify_file, "w") as file:
      # Write the string representation of the tuple to the file
      file.write(file_content)

    func_send_message("added to notify group :100:")

  else: 
    func_write_to_log(room_id + " already in notify group", "INFO", current_function)
    func_send_message("alredy in notify groupd :eyes:")
    

#####################################################
# remove a room from notifing if a update was found #
#####################################################
def func_notify_room_remove(room_id):
  global matrix_notify_rooms
  current_function = inspect.currentframe().f_code.co_name
  matrix_notify_rooms = tuple(value for value in matrix_notify_rooms if value != room_id)
  file_content = " ".join(matrix_notify_rooms)
  with open(notify_file, "w") as file:
    # Write the string representation of the tuple to the file
    file.write(file_content)
  func_write_to_log("removed " + room_id + "from notify group", "INFO", current_function)
  func_send_message("removed from notify group :salute:")


################################
# get notify rooms out of file #
################################
def func_notify_rooms_get():
  global matrix_notify_rooms
  
  # open file in read only mode, if exist
  if os.path.exists(notify_file):
    with open(notify_file, "r") as file:
      # read first line
      first_line = file.readline().strip()
      # split values with spaces
      values = first_line.split()
      # convert to tuple
      matrix_notify_rooms = tuple(values)


####################
# toggle auto join #
####################
def func_toggle_autojoin():
  current_function = inspect.currentframe().f_code.co_name
  
  # invert Boolean
  matrix_join_rooms_new = not config.matrix_join_rooms
  func_write_to_log("toggling auto Join to " + str(matrix_join_rooms_new), "INFO", current_function)

  # open file and
  with open("config.py", "r") as f:
      content = f.readlines()

  # search line with variable
  for i, line in enumerate(content):
      if line.startswith("matrix_join_rooms"):
          content[i] = "matrix_join_rooms = "+str(matrix_join_rooms_new)+"\n"
          break

  # overwrite found line
  with open("config.py", "w") as f:
      f.writelines(content)
  importlib.reload(config)


#######################
# health check of bot #
#######################
def func_health_check():
  current_function = inspect.currentframe().f_code.co_name
  bot_health_check_config = ""

  func_write_to_log("Checking health", "INFO", current_function)

  if func_container_check():
    bot_health_container = "True"
    func_write_to_log("!! running inside a container !!", "INFO", "startup")
  else:
    bot_health_container = "False"
    func_write_to_log("not running inside a container", "INFO", "startup")

  if os.path.isfile(os.path.join(main_script_path,"config.py")):
    bot_health_check_config = "Config file found"
    func_write_to_log("Config File found", "INFO", current_function)
  else: 
    func_write_to_log("Config file not found", "ERROR", current_function)
    bot_health_check_config = "**Config file not found**"

  if os.path.isfile(os.path.join(main_script_path,"modules","bad_words.py")):
    bot_health_check_badwords = "File was found" 
  else:
    bot_health_check_badwords = "**File was not found**" 

  if config.matrix_base_url == "https://chat.teamspeak.com":
    bot_health_check_baseurl = "URL is set correct"
    func_write_to_log("URL set correctly", "INFO", current_function)
  else:
    bot_health_check_baseurl = "**URL is not correct**"
    func_write_to_log("URL empty or pointing to wrong matrix homebase", "ERROR", current_function)

  if config.matrix_username:
    bot_health_check_username = "Username is set"
    func_write_to_log("Username is set", "INFO", current_function)
  else:
    bot_health_check_username = "**Username is empty**"
    func_write_to_log("Username wasnt found, error in config", "ERROR", current_function)

  if config.matrix_password:
    bot_health_check_password = "Password is set"
    func_write_to_log("Password is set", "INFO", current_function)
  else:
    bot_health_check_password = "**Password is empty**"
    func_write_to_log("Password wasnt found, error in config", "ERROR", current_function)

  func_send_message("Summary of Health Check: \nConfig: " + bot_health_check_config \
  + "\nMatrix Server URL: " + bot_health_check_baseurl + "\nUsername: " + bot_health_check_username \
  + "\nPassword: " + bot_health_check_password + "\nBad Words File: " + bot_health_check_badwords + "\nContainer: "+bot_health_container)
 

#################################################
# add stat to stats.txt, or create missing stat #
#################################################
def func_add_stats(key):
  if key in stat_dict:
    stat_dict[key] += 1
  else:
    stat_dict[key] = 1


################
# stop the bot #
################
def func_bot_stop():
  current_function = inspect.currentframe().f_code.co_name
  func_write_to_log("stopping bot...", "INFO", current_function)
  exit(0)


###################
# restart the bot #
###################
def func_bot_restart():
  current_function = inspect.currentframe().f_code.co_name
  
  func_write_to_log("restarting bot...", "INFO", current_function)
  # splitted linux and windows if function shouldnt work
  if os_name == "Linux":
    python_executable = sys.executable
    script_file = os.path.join(main_script_path, "./modules/restart.py")
    os.system(python_executable + " " + script_file + " " + os_name )
  if os_name == "Windows":
    python_executable = sys.executable
    script_file = main_script_path +".\\modules\\restart.py" 
    subprocess.call([python_executable, script_file, os_name])

  else:
    func_write_to_log("Couldnt detect OS for proper restart", "CRITICAL", current_function)
    exit(255)


##############################################
# check if bot is running inside a container #
##############################################
def func_container_check():
  return os.path.exists('/proc/1/cgroup')





############################
#                          #
#  starting of the script  #
#                          #
############################
if func_container_check():
  # if running inside a container
  func_write_to_log("!! running inside a container !!", "INFO", "startup_container_check")
  source_config = "/opt/teampy/config.py"
  target_config = "/opt/teampy/configs/config.py"
  if not os.path.exists(target_config):
    with open(source_config, 'rb') as src_file:
        with open(target_config, 'wb') as dest_file:
            dest_file.write(src_file.read())
    func_write_to_log("config.py copied successfully!", "INFO", "startup_container_check")
  # import config file from persistent folder
  import configs.config 
  # change folders for files that needs to be persistent
  notify_file = os.path.join("configs","notify.txt")
  stats_file = os.path.join(main_script_path,"configs", "stats.txt")
  
else:
  func_write_to_log("not running inside a container", "INFO", "startup_container_check")


if not config.matrix_username or not config.matrix_password:
  func_write_to_log("finish configuration step first!", "ERROR", "startup")
  exit()

func_write_to_log("starting bot....", "INFO", "startup")

if os_name == "Windows": 
  func_write_to_log("Detected Windows", "DEBUG", "startup")
elif os_name == "Linux":
  func_write_to_log("Detected Linux", "DEBUG", "startup")
else:
  func_write_to_log("Coulndt detect OS ("+os_name+"), script wont work well!", "CRITICAL", "startup")

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
        
with open(stats_file, "r") as f:
    stat_dict = {}
    for line in f:
        key, value = line.strip().split("=")
        stat_dict[key] = int(value)

# login to Matrix and get access token and own user id
login_url = config.matrix_base_url + "/_matrix/client/r0/login"
login_data = {"type": "m.login.password", "user": config.matrix_username, "password": config.matrix_password}
login_headers = {"User-Agent": user_agent}
response = requests.post(login_url, json=login_data, headers=login_headers)
if response.json().get("access_token"):
  access_token = response.json()["access_token"]
  matrix_self = response.json()["user_id"]
  func_write_to_log("Login Successfull, own Matrix ID: " + matrix_self, "INFO", "startup_login")
else: 
  func_write_to_log("Error Login failed, Username or Password wrong %s" % response.text, "ERROR", "startup_login")
  exit(1)

# prepare first sync
sync_url = config.matrix_base_url + "/_matrix/client/r0/sync?3000"
sync_headers = {"Authorization": "Bearer " + access_token, "User-Agent": user_agent}
next_batch = None

#make initial request (so he ignores old chats)
response = requests.get(sync_url, headers=sync_headers)
sync_response = json.loads(response.text)







# not working 
#func_set_avatar()

func_check_invite()
func_set_status()
func_add_stats("startup_count")
func_check_client_update()
func_notify_rooms_get()

func_write_to_log("Startup complete...", "INFO", "startup_finished")
while True:
  time.sleep(1)

  # check for new update of ts client
  elapsed_time = time.time() - start_time
  if elapsed_time >= interval: 
    start_time = time.time()
    func_check_client_update()

  next_batch = sync_response["next_batch"]
  sync_url = config.matrix_base_url + "/_matrix/client/v3/sync?timeout=1000&since=" + next_batch
  # make a request to the sync API to check for new events
  response = requests.get(sync_url, headers=sync_headers)
  
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
          for room_id in sync_response["rooms"]["join"]:
            # Loop through all new events in the room
            for event in sync_response["rooms"]["join"][room_id]["timeline"]["events"]:
              # check if the event is a message
              if event["type"] == "m.room.message" and event["sender"] != matrix_self:
                # Print the message body, need to changed to loggin into a file
                matrix_sender = event["sender"]
                matrix_received_message = event["content"]["body"]
                matrix_room = room_id
                func_write_to_log(matrix_sender  + ": " + matrix_received_message +" (room: "+ matrix_room +")", "INFO", "main_loop")
                func_write_to_log(json.dumps(event,sort_keys=True, indent=4), "DEBUG", "main_loop")

                #print(json.dumps(event,sort_keys=True, indent=4))

                #############################################
                # check what if content matches any command #
                #############################################

                # gif command
                if config.command_prefix + config.command_gif in matrix_received_message:
                  if config.commands_overview[config.command_gif]["command_enabled"] == True:
                    func_add_stats("gifs_count")
                    func_send_gif()
                  else:
                    func_send_message(command_disabled_message)
                elif config.command_prefix + config.command_btc in matrix_received_message:
                  if config.commands_overview[config.command_btc]["command_enabled"] == True:
                    btc_base_url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies="
                    
                    btc_gbp_respond = requests.get(btc_base_url + "gbp")
                    btc_gbp = btc_gbp_respond.json()["bitcoin"]["gbp"]

                    btc_eur_respond = requests.get(btc_base_url + "eur")
                    btc_eur = btc_eur_respond.json()["bitcoin"]["eur"]

                    btc_usd_respond = requests.get(btc_base_url + "usd")
                    btc_usd = btc_usd_respond.json()["bitcoin"]["usd"]
                    func_send_message("__**Prices are not so precise**__\nCurrent Price of BTC: \
                    \nEuro: "+str(btc_eur)+" \nGBP: "+str(btc_gbp)+" \nUSD: "+str(btc_usd)+" \
                    \nfrom https://www.coingecko.com/")

                    func_add_stats("btc_command_count")
                  else:
                    func_send_message(command_disabled_message)
                    
                elif config.command_prefix + config.command_eth in matrix_received_message:
                  if config.commands_overview[config.command_eth]["command_enabled"] == True:
                    eth_base_url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies="
                    
                    eth_gbp_respond = requests.get(eth_base_url + "gbp")
                    eth_gbp = eth_gbp_respond.json()["ethereum"]["gbp"]

                    eth_eur_respond = requests.get(eth_base_url + "eur")
                    eth_eur = eth_eur_respond.json()["ethereum"]["eur"]

                    eth_usd_respond = requests.get(eth_base_url + "usd")
                    eth_usd = eth_usd_respond.json()["ethereum"]["usd"]
                    func_send_message("__**Prices are not so precise**__\nCurrent Price of ETH: \
                    \nEuro: "+str(eth_eur)+" \nGBP: "+str(eth_gbp)+" \nUSD: "+str(eth_usd)+" \
                    \nfrom https://www.coingecko.com/")

                    func_add_stats("eth_command_count")
                  else:
                    func_send_message(command_disabled_message)

                # help
                elif config.command_prefix + config.command_help in matrix_received_message:
                  if config.commands_overview[config.command_help]["command_enabled"] == True:
                    matrix_prepare_message = "Here is help, dont worry!\n"
                    for key in config.commands_overview:
                      if config.commands_overview[key]["command_enabled"] == True:
                        matrix_prepare_message += "**" + config.command_prefix + key + ":** " + config.commands_overview[key]["description"] + "\n"
                    func_send_message(matrix_prepare_message)
                    func_add_stats("help_command_count")
                  else:
                    func_send_message(command_disabled_message)

                # public stats
                elif config.command_prefix + config.command_stats in matrix_received_message:
                  if config.commands_overview[config.command_stats]["command_enabled"] == True:
                    if config.stats_visible == "public" or  config.stats_visible == "admin" and matrix_sender in config.bot_admin:
                      params = {"filter": "{\"presence\":{\"types\":[\"m.presence\"]},\"account_data\":{\"types\":[\"m.direct\"]},\"room\":{\"rooms\":[],\"account_data\":{\"types\":[\"m.tag\",\"m.space\"]},\"state\":{\"types\":[\"m.room.member\"],\"lazy_load_members\":true},\"timeline\":{\"types\":[\"m.room.message\",\"m.room.encrypted\",\"m.sticker\",\"m.reaction\"]}}}", "timeout": 0}

                      friend_response = requests.get(config.matrix_base_url + "/_matrix/client/r0/sync", headers=sync_headers, params=params)
                      if friend_response.status_code == 200:
                          matrix_friends = friend_response.json()
                          matrix_friends = matrix_friends.get("account_data", {}).get("events", [])
                          matrix_friend_count = len(matrix_friends)
                      else:
                          func_write_to_log("Failed to retrieve friend list. %s" % response.text, "ERROR", "main_loop")

                      #pretty print
                      #print(json.dumps(matrix_friends,sort_keys=True, indent=4))

                      matrix_prepare_message = "Number of friends (all time): **" + str(matrix_friend_count) + "**"
                      for key in stat_dict:
                        matrix_prepare_message += "\n"+stats_description[key]+": **" + str(stat_dict[key]) + "**"
                      func_send_message(matrix_prepare_message)

                    else:
                      func_send_message("the stats are currently admin only :eyes:")
                  else:
                    func_send_message(command_disabled_message)

                # whoami
                elif config.command_prefix + config.command_whoami in matrix_received_message:
                  if config.commands_overview[config.command_whoami]["command_enabled"] == True:
                    request_sender_name = requests.get(config.matrix_base_url + "/_matrix/client/r0/profile/"+ matrix_sender, headers=sync_headers)
                    matrix_sender_name = request_sender_name.json()["displayname"]
                    user_rank = "User"
                    if matrix_sender in config.bot_admin: 
                      user_rank = "Admin"
                    func_send_message("Your identifier is: "+ matrix_sender + "\nYour name is: " + matrix_sender_name \
                    + "\nI see you as a " + user_rank)
                    matrix_sender_name = ""

                    func_add_stats("whoami_command_count")
                  else:
                    func_send_message(command_disabled_message)

                # whois
                elif config.command_prefix + config.command_whois in matrix_received_message:
                  if config.commands_overview[config.command_whois]["command_enabled"] == True:
                    user_rank = "User"

                    message_index = matrix_received_message.find(" ")
                    # get search string, if available
                    matrix_identifier = matrix_received_message[message_index+1:] 
                    if matrix_identifier:
                      request_sender_name = requests.get(config.matrix_base_url + "/_matrix/client/r0/profile/" + matrix_identifier, headers=sync_headers)
                      repsonse_name = request_sender_name.json()

                      check_identifier_name = str(repsonse_name.get("displayname"))
                      if check_identifier_name != "None":
                        matrix_sender_name = repsonse_name["displayname"]
                      else:
                        matrix_sender_name = "**Couldnt find Name**"
                        user_rank = "Unknown"

                      if matrix_identifier in config.bot_admin: 
                        user_rank = "Admin"

                      func_send_message("The identifier is: "+ matrix_identifier + "\nThe name is: " + matrix_sender_name \
                      + "\nI see that person as a " + user_rank)
                      matrix_sender_name = ""
                      func_add_stats("whois_command_count")
                    else:
                      matrix_sender_name = rank_error_message
                  else:
                    func_send_message(command_disabled_message)

                # polls
                elif config.command_prefix + config.command_poll in matrix_received_message :
                  if config.commands_overview[config.command_poll]["command_enabled"] == True:
                    func_add_stats("poll_command_count")
                    poll_choices = ""
                    poll_count = 0

                    poll_question = matrix_received_message.split("\n")[0] 
                    poll_question = poll_question.split()  
                    poll_question = ' '.join(poll_question[1:])
                    if not poll_question: 
                      poll_question = "Do you like polls ?"
                    poll_choices_raw = matrix_received_message.split("\n")

                    for choice in poll_choices_raw:
                      if choice != poll_choices_raw[0]:
                        if not choice.startswith(":") and choice:
                          choice = str(poll_emojis[poll_count]) + " " + str(choice)
                          if poll_count >= 5:
                            poll_count = 0
                          poll_count += 1
                        poll_choices += str(choice) + "\n"
                    if not poll_choices:
                      poll_choices = ":+1: yes \n :-1: no"

                    func_send_message("a new poll just started! \n\nQuestion: \"__" + poll_question + "__\"\n" \
                    + "Choose the reaction from below to vote\n\n Choices:\n" + poll_choices)
                  else:
                    func_send_message(command_disabled_message)


                # dice
                elif config.command_prefix + config.command_dice in matrix_received_message :
                  if config.commands_overview[config.command_dice]["command_enabled"] == True:
                    func_add_stats("roll_command_count")
                    dice_number = random.randint(1, 6)
                    func_send_message("You rolled a **" + str(dice_number) + "** :exploding_head:")
                  else:
                    func_send_message(command_disabled_message)
                    

                # admin help
                elif config.command_prefix + config.command_admin_help in matrix_received_message or config.command_prefix + config.command_admin_base == matrix_received_message + " ":
                  if config.admin_commands_overview[config.command_admin_help]["command_enabled"] == True:
                    if matrix_sender in config.bot_admin:
                      matrix_prepare_message = "Here is __special__ help, dont worry!\n"
                      for key in config.admin_commands_overview:
                        if config.admin_commands_overview[key]["command_enabled"] == True:
                          matrix_prepare_message += "**" + config.command_prefix + key + ":** " + config.admin_commands_overview[key]["description"] + "\n"
                      func_send_message(matrix_prepare_message)
                    else:
                      func_send_message(rank_error_message)
                  else:
                    func_send_message(command_disabled_message)

                # admin auto join toggle
                elif config.command_prefix + config.command_admin_autojoin == matrix_received_message:
                  if config.admin_commands_overview[config.command_admin_autojoin]["command_enabled"] == True:
                    if matrix_sender in config.bot_admin:
                      func_toggle_autojoin()
                      func_send_message("Toggled auto join to " + str(config.matrix_join_rooms))
                    else:
                      func_send_message(rank_error_message)
                  else:
                    func_send_message(command_disabled_message)

                # admin reload
                elif config.command_prefix + config.command_admin_reload == matrix_received_message:
                  if config.admin_commands_overview[config.command_admin_reload]["command_enabled"] == True:
                    if matrix_sender in config.bot_admin:
                      importlib.reload(config)
                      func_set_status()
                      func_send_message("Reloaded Config")
                    else:
                      func_send_message(rank_error_message)
                  else:
                    func_send_message(command_disabled_message)

                # admin leave room
                elif config.command_prefix + config.command_admin_leave == matrix_received_message:
                  if config.admin_commands_overview[config.command_admin_leave]["command_enabled"] == True:
                    if matrix_sender in config.bot_admin:
                      response = requests.post(config.matrix_base_url + "/_matrix/client/r0/rooms/" + matrix_room + "/leave", headers=sync_headers)

                      if response.status_code == 200:
                          func_write_to_log("Successfully left room " + room_id, "INFO", "main_loop")
                      else:
                          func_write_to_log("Failed to leave room %s" % response.text, "ERROR", "main_loop")
                    else:
                      func_send_message(rank_error_message)
                  else:
                    func_send_message(command_disabled_message)

                # admin health
                elif config.command_prefix + config.command_admin_health == matrix_received_message:
                  if config.admin_commands_overview[config.command_admin_health]["command_enabled"] == True:
                    if matrix_sender in config.bot_admin:
                      func_health_check()
                    else:
                      func_send_message(rank_error_message)
                  else:
                    func_send_message(command_disabled_message)

                # admin stop
                elif config.command_prefix + config.command_admin_stop == matrix_received_message:
                  if config.admin_commands_overview[config.command_admin_stop]["command_enabled"] == True:
                    if matrix_sender in config.bot_admin:
                      func_send_message("Good By :wave:")
                      func_bot_stop()
                    else:
                      func_send_message(rank_error_message)
                  else:
                    func_send_message(command_disabled_message)

                # admin restart
                elif config.command_prefix + config.command_admin_restart == matrix_received_message:
                  if config.admin_commands_overview[config.command_admin_restart]["command_enabled"] == True:
                    if matrix_sender in config.bot_admin:
                      func_send_message("See you soon :wave:")
                      func_bot_restart()
                    else:
                      func_send_message(rank_error_message)
                  else:
                    func_send_message(command_disabled_message)

                # admin update-notify
                elif config.command_prefix + config.command_admin_notify == matrix_received_message:
                  if config.admin_commands_overview[config.command_admin_notify]["command_enabled"] == True:
                    if matrix_sender in config.bot_admin:
                      if matrix_room in matrix_notify_rooms:
                        func_notify_room_remove(matrix_room)
                      else:
                        func_notify_room_add(matrix_room)
                    else:
                      func_send_message(rank_error_message)
                  else:
                    func_send_message(command_disabled_message)

                # admin stats
                elif config.command_prefix + config.command_admin_stats == matrix_received_message:
                  if config.admin_commands_overview[config.command_admin_stats]["command_enabled"] == True:
                    if matrix_sender in config.bot_admin:
                      params = {"filter": "{\"presence\":{\"types\":[\"m.presence\"]},\"account_data\":{\"types\":[\"m.direct\"]},\"room\":{\"rooms\":[],\"account_data\":{\"types\":[\"m.tag\",\"m.space\"]},\"state\":{\"types\":[\"m.room.member\"],\"lazy_load_members\":true},\"timeline\":{\"types\":[\"m.room.message\",\"m.room.encrypted\",\"m.sticker\",\"m.reaction\"]}}}", "timeout": 0}

                      friend_response = requests.get(config.matrix_base_url + "/_matrix/client/r0/sync", headers=sync_headers, params=params)
                      if friend_response.status_code == 200:
                          matrix_friends = friend_response.json()
                          matrix_friends = matrix_friends.get("account_data", {}).get("events", [])
                          matrix_friend_count = len(matrix_friends)
                      else:
                        func_write_to_log("Failed to retrieve friend list. %s" % response.text, "ERROR", "main_loop")

                      #pretty print
                      #print(json.dumps(matrix_friends,sort_keys=True, indent=4))

                      matrix_prepare_message = "Number of friends (all time): **" + str(matrix_friend_count) + "**"
                      for key in stat_dict:
                        matrix_prepare_message += "\n"+stats_description[key]+": **" + str(stat_dict[key]) + "**"
                      func_send_message(matrix_prepare_message)
                    else:
                      func_send_message(rank_error_message)
                  else:
                    func_send_message(command_disabled_message)

                # admin version
                elif config.command_prefix + config.command_admin_version == matrix_received_message:
                  if config.admin_commands_overview[config.command_admin_version]["command_enabled"] == True:
                    if matrix_sender in config.bot_admin:
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

                      func_send_message("Current Version of Teampy **" + version + "**"+ \
                        "\n"+compare_version)
                    else:
                      func_send_message(rank_error_message)
                  else:
                    func_send_message(command_disabled_message)

                #!DEBUG - only for testing 
                elif config.command_prefix + "notify_test" in matrix_received_message:
                  func_notify_update()

                # ping 
                elif config.command_prefix + config.command_ping in matrix_received_message:
                  if config.commands_overview[config.command_ping]["command_enabled"] == True:
                    matrix_prepare_message = "!pong"
                    raw_ping = ""
                    if os_name == "Linux":
                      command_output = subprocess.Popen("ping -c 1 chat.teamspeak.com | grep icmp | awk '{print $8}' | sed s/'time='/''/g", stdout=subprocess.PIPE, shell=True)
                      raw_output, _ = command_output.communicate()
                      latency = str(raw_output).strip().replace("\\n", "").replace("b", "").replace("\'", "")
                      func_send_message(matrix_prepare_message + "\nLatency to ts: " + latency + "ms")
                      
                    elif os_name == "Windows":
                      command_output = subprocess.Popen("powershell .\\modules\\ping.ps1 chat.teamspeak.com", stdout=subprocess.PIPE)
                      raw_output, _ = command_output.communicate()
                      raw_output = str(raw_output).strip().split()
                      latency = ""
                      for word in raw_output:
                        if "ms" in word:
                          latency = word.replace("\\r\\n\'", "") # removing EOL from windows
                          break
                      func_send_message(matrix_prepare_message + "\nLatency to ts: " + latency)

                      func_add_stats("ping_command_count")
                  else:
                    func_send_message(command_disabled_message)
                elif matrix_received_message.startswith(config.command_prefix):
                  func_send_message("command not found :thinking: ("+matrix_received_message+")\nif you need more info use `"+config.command_prefix+config.command_help+"`")
                else :
                  func_write_to_log("chat message not directed to bot", "DEBUG", "main_loop")

                # check for bad words
                if config.bad_word_checks == True:
                  for word in bad_words:
                    if word in matrix_received_message:
                      matrix_received_message = "no you"
                      func_send_gif()



    else:
      time.sleep(1)
      response = requests.get(sync_url, headers=sync_headers)

    # check if he got invited into a new room 
    func_check_invite()
  else:
    func_write_to_log("Error getting messages from Matrix: %s" % response.text, "DEBUG", "main_loop")
  

