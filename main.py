#!/usr/bin/env python3
# The TeamPy Bot, a simple Command Bot
# Created 2023-03-16
# by DerSafterXD & WargamerSenpai
#
# Current Features:
# - send gifs
# - set status text
# - show price of eth & btc
# 
# WIP Features: 
# - set avatar
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


# import config.py
import config
# import bad_words.py
from modules.bad_words import * 
# import version.py file
from modules.version import * 


#
# script variables 
#

# special User Agent for teamspeak matrix, dont touch or else not it is broken
user_agent = "Go-http-client/2.0"

# return message
matrix_send_message = ""
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
# url for syncing
sync_url = "/_matrix/client/r0/sync?3000"
# the file where all stats are saved to
stats_file = "stats.txt"
# description for stats
stats_description = {
  "messages_send_count": "How many Messages where sent",
  "gifs_count": "How many gifs where sent",
  "startup_count": "How many times the bot started",
  "help_command_count": "help Command Count", 
  "btc_command_count": "BTC Command Count",
  "eth_command_count": "ETH Command Count",
  "whoami_command_count": "whoami Command Count",
  "whois_command_count": "whois Command Count",
  "ping_command_count": "ping Command Count"
}

#
# functions
#

# check if new invite is available
def func_check_invite():
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
          #print(json.dumps(sync_response["rooms"]["invite"][room]["invite_state"]["events"][3]["content"],sort_keys=True, indent=4))
          if check_for_privat != "None":
            matrix_privat_request += room +" "
            #print(json.dumps(sync_response["rooms"]["invite"][room]["invite_state"]["events"][3]["content"],sort_keys=True, indent=4))

        # send post request, to join the room
        for room in sync_response["rooms"]["invite"]:
          if room in matrix_privat_request:
            params = {"membership": "join"}
            response = requests.post(config.matrix_base_url + "/_matrix/client/r0/join/"+matrix_new_room, headers=sync_headers, params=params)
            if response.status_code == 200:
              print("[INF] successfully joined direct chat")
            else:
              print("[ERR] couldnt join direct chat ("+matrix_new_room+") %s" % response.text)
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
              print("[INF] successfully joined room (Name: "+room_name+")")
            else:
              print("[ERR] couldnt join room ("+matrix_new_room+") %s" % response.text)
        time.sleep(1)
        response = requests.get(sync_url, headers=sync_headers)
        next_batch = sync_response["next_batch"]
        sync_url = config.matrix_base_url + "/_matrix/client/r0/sync?since=" + next_batch
        response = requests.get(sync_url, headers=sync_headers)
        next_batch = sync_response["next_batch"]

# set avatar
def func_set_avatar():
  if config.avatar_url:
    avatar_data = {"avatar_url": config.avatar_url} 
    response = requests.put(config.matrix_base_url + "/_matrix/client/r0/profile/"+matrix_self+"/avatar_url", headers=sync_headers, json=avatar_data)
    if response.status_code == 200:
      response = requests.get(config.matrix_base_url + "/_matrix/client/r0/profile/"+matrix_self+"/avatar_url", headers=sync_headers)
      new_avatar_url = response.json()
      print("[INF] Bot avatar changed successfully. ("+ new_avatar_url +")")
    else:
      print("[ERR] Failed to change bot avatar. %s" % response.text)

# set status message and presence 
def func_set_status():
   if config.status_text and config.presence_state:
    status_data = {"presence": config.presence_state, "status_msg": config.status_text}
    response = requests.put(config.matrix_base_url + "/_matrix/client/r0/presence/"+matrix_self+"/status", headers=sync_headers, json=status_data)
    if response.status_code == 200:
      print("[INF] Status message updated successfully.")
    else:
      print("[ERR] Failed to update status message. %s" % response.text)

# send gif with giphy api
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
        matrix_send_message = data['data'][0]['images']['original']['url'] 
      else:
        matrix_send_message = "couldnt find your search string (404)"
    else:
      matrix_send_message = data['data']['images']['original']['url'] 
  else:
    matrix_send_message="i have a problem, the api key is missing in the config, please contact the admin :anxious:"
  return matrix_send_message

# toggle auto join
def func_toggle_autojoin():
  # invert Boolean
  matrix_join_rooms_new = not config.matrix_join_rooms
  print("[DBG] Toggling auto Join to " + str(matrix_join_rooms_new))

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

def func_health_check():
  global matrix_send_message
  bot_health_check_config = ""
  print("[INF] Checking health")

  if os.path.isfile("config.py"):
    bot_health_check_config = "Config file found"
    print("[INF] Config File found")

    if os.path.isfile("config.py"):
      bot_health_check_badwords = "File was found" 
    else:
      bot_health_check_badwords = "**File was not found**" 

    if config.matrix_base_url == "https://chat.teamspeak.com":
      bot_health_check_baseurl = "URL is set correct"
      print("[INF] URL set correctly")
    else:
      bot_health_check_baseurl = "**URL is not correct**"
      print("[ERR] URL empty or pointing to wrong matrix homebase")

    if config.matrix_username:
      bot_health_check_username = "Username is set"
      print("[INF] Username is set" )
    else:
      bot_health_check_username = "**Username is empty**"
      print("[ERR] Username wasnt found, error in config")

    if config.matrix_password:
      bot_health_check_password = "Password is set"
      print("[INF] Password is set" )
    else:
      bot_health_check_password = "**Password is empty**"
      print("[ERR] Password wasnt found, error in config")

  else: 
    print("[ERR] Config file not found")
    bot_health_check_config = "**Config file not found**"

  matrix_send_message = "Summary of Health Check: \nConfig: " + bot_health_check_config \
  + "\nMatrix Server URL: " + bot_health_check_baseurl + "\nUsername: " + bot_health_check_username \
  + "\nPassword: " + bot_health_check_password + "\nBad Words File: " + bot_health_check_badwords


#
# starting of the script
#

if not config.matrix_username or not config.matrix_password:
  print("[ERR] finish configuration step first!")
  exit()

print("starting bot....")

if os_name == "Windows": 
  print("[DBG] Detected Windows")
elif os_name == "Linux":
  print("[DBG] Detected Linux")
else:
  print("[ERR] Coulndt detect OS ("+os_name+"), script wont work well!")
  
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
access_token = response.json()["access_token"]
matrix_self = response.json()["user_id"]


# prepare first sync
sync_url = config.matrix_base_url + "/_matrix/client/r0/sync?3000"
sync_headers = {"Authorization": "Bearer " + access_token, "User-Agent": user_agent}
next_batch = None

#make initial request (so he ignores old chats)
response = requests.get(sync_url, headers=sync_headers)
sync_response = json.loads(response.text)
func_check_invite()



#pretty print
#print(json.dumps(arry,sort_keys=True, indent=4))

# not working 
#func_set_avatar()
func_set_status()
stat_dict["startup_count"] += 1

while True:
  time.sleep(1)

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
                print("[DBG] "+event["sender"]  + ": " + event["content"]["body"])
                matrix_sender = event["sender"]
                matrix_received_message = event["content"]["body"]
                matrix_room = room_id


                # check what command was send
                # gif command
                if config.command_prefix + config.command_gif in matrix_received_message:
                  stat_dict["gifs_count"] += 1
                  matrix_send_message = func_send_gif()
                elif config.command_prefix + config.command_btc in matrix_received_message:
                  btc_base_url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies="
                  
                  btc_gbp_respond = requests.get(btc_base_url + "gbp")
                  btc_gbp = btc_gbp_respond.json()["bitcoin"]["gbp"]

                  btc_eur_respond = requests.get(btc_base_url + "eur")
                  btc_eur = btc_eur_respond.json()["bitcoin"]["eur"]

                  btc_usd_respond = requests.get(btc_base_url + "usd")
                  btc_usd = btc_usd_respond.json()["bitcoin"]["usd"]

                  matrix_send_message = "__**Prices are not so precise**__\nCurrent Price of BTC: \
                  \nEuro: "+str(btc_eur)+" \nGBP: "+str(btc_gbp)+" \nUSD: "+str(btc_usd)+" \
                  \nfrom https://www.coingecko.com/"

                  stat_dict["btc_command_count"] += 1
                  
                elif config.command_prefix + config.command_eth in matrix_received_message:
                  eth_base_url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies="
                  
                  eth_gbp_respond = requests.get(eth_base_url + "gbp")
                  eth_gbp = eth_gbp_respond.json()["ethereum"]["gbp"]

                  eth_eur_respond = requests.get(eth_base_url + "eur")
                  eth_eur = eth_eur_respond.json()["ethereum"]["eur"]

                  eth_usd_respond = requests.get(eth_base_url + "usd")
                  eth_usd = eth_usd_respond.json()["ethereum"]["usd"]

                  matrix_send_message = "__**Prices are not so precise**__\nCurrent Price of ETH: \
                  \nEuro: "+str(eth_eur)+" \nGBP: "+str(eth_gbp)+" \nUSD: "+str(eth_usd)+" \
                  \nfrom https://www.coingecko.com/"

                  stat_dict["eth_command_count"] += 1

                # help
                elif config.command_prefix + config.command_help in matrix_received_message:
                  matrix_send_message = "Here is help, dont worry!\n"
                  for key in config.help_display:
                    matrix_send_message += "**" + config.command_prefix + key + ":** " + config.help_display[key] + "\n"
                  stat_dict["help_command_count"] += 1
                  

                # whoami
                elif config.command_prefix + config.command_whoami in matrix_received_message:
                  request_sender_name = requests.get(config.matrix_base_url + "/_matrix/client/r0/profile/"+ matrix_sender, headers=sync_headers)
                  matrix_sender_name = request_sender_name.json()["displayname"]
                  user_rank = "User"
                  if matrix_sender in config.bot_admin: 
                    user_rank = "Admin"
                  matrix_send_message = "Your identifier is: "+ matrix_sender + "\nYour name is: " + matrix_sender_name \
                  + "\nI see you as a " + user_rank
                  matrix_sender_name = ""

                  stat_dict["whoami_command_count"] += 1

                # whois
                elif config.command_prefix + config.command_whois in matrix_received_message :
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

                    matrix_send_message = "The identifier is: "+ matrix_identifier + "\nThe name is: " + matrix_sender_name \
                    + "\nI see that person as a " + user_rank
                    matrix_sender_name = ""
                    stat_dict["whois_command_count"] += 1
                  else:
                    matrix_sender_name = rank_error_message

                # admin help
                elif config.command_prefix + config.command_admin_help in matrix_received_message or config.command_prefix + config.command_admin_base == matrix_received_message + " ":
                  if matrix_sender in config.bot_admin:
                    matrix_send_message = "Here is __special__ help, dont worry!\n"
                    for key in config.admin_help_display:
                      matrix_send_message += "**" + config.command_prefix + key + ":** " + config.admin_help_display[key] + "\n"
                  else:
                    matrix_send_message = rank_error_message

                # admin auto join toggle
                elif config.command_prefix + config.command_admin_autojoin == matrix_received_message:
                  if matrix_sender in config.bot_admin:
                    func_toggle_autojoin()
                    matrix_send_message = "Toggled auto join to " + str(config.matrix_join_rooms)
                  else:
                    matrix_send_message = rank_error_message

                # admin reload
                elif config.command_prefix + config.command_admin_reload == matrix_received_message:
                  if matrix_sender in config.bot_admin:
                    importlib.reload(config)
                    matrix_send_message = "Reloaded Config"
                  else:
                    matrix_send_message = rank_error_message

                # admin health
                elif config.command_prefix + config.command_admin_leave == matrix_received_message:
                  if matrix_sender in config.bot_admin:
                    response = requests.post(config.matrix_base_url + "/_matrix/client/r0/rooms/" + matrix_room + "/leave", headers=sync_headers)

                    if response.status_code == 200:
                        print("[INF] Successfully left room "+room_id)
                    else:
                        print("[ERR] Failed to leave room %s" % response.text)                 
                  else:
                    matrix_send_message = rank_error_message

                # admin leave room
                elif config.command_prefix + config.command_admin_health == matrix_received_message:
                  if matrix_sender in config.bot_admin:
                    func_health_check()
                  else:
                    matrix_send_message = rank_error_message

                # admin stop
                elif config.command_prefix + config.command_admin_stop == matrix_received_message:
                  if matrix_sender in config.bot_admin:
                    matrix_send_message = "Good By :wave:"
                  else:
                    matrix_send_message = rank_error_message

                # admin restart
                elif config.command_prefix + config.command_admin_restart == matrix_received_message:
                  if matrix_sender in config.bot_admin:
                    matrix_send_message = "See you soon :wave:"
                  else:
                    matrix_send_message = rank_error_message

                # admin stats
                elif config.command_prefix + config.command_admin_stats == matrix_received_message:
                  if matrix_sender in config.bot_admin:
                    params = {"filter": "{\"presence\":{\"types\":[\"m.presence\"]},\"account_data\":{\"types\":[\"m.direct\"]},\"room\":{\"rooms\":[],\"account_data\":{\"types\":[\"m.tag\",\"m.space\"]},\"state\":{\"types\":[\"m.room.member\"],\"lazy_load_members\":true},\"timeline\":{\"types\":[\"m.room.message\",\"m.room.encrypted\",\"m.sticker\",\"m.reaction\"]}}}", "timeout": 0}

                    friend_response = requests.get(config.matrix_base_url + "/_matrix/client/r0/sync", headers=sync_headers, params=params)
                    if friend_response.status_code == 200:
                        matrix_friends = friend_response.json()
                        matrix_friends = matrix_friends.get("account_data", {}).get("events", [])
                        matrix_friend_count = len(matrix_friends)
                    else:
                        print("Failed to retrieve friend list. %s" % response.text)          

                    #pretty print
                    #print(json.dumps(matrix_friends,sort_keys=True, indent=4))

                    matrix_send_message = "Number of friends (all time): **" + str(matrix_friend_count) + "**"
                    for key in stat_dict:
                      matrix_send_message += "\n"+stats_description[key]+": **" + str(stat_dict[key]) + "**"
                  else:
                    matrix_send_message = rank_error_message

                # admin version
                elif config.command_prefix + config.command_admin_version == matrix_received_message:
                  if matrix_sender in config.bot_admin:
                    repo_api_url = "https://api.github.com/repos/Wargamer-Senpai/teampy/releases/latest"
                    github_response = requests.get(repo_api_url)
                    github_response_json = github_response.json()
                    check_github = str(github_response_json.get("tag_name"))

                    if check_github != "None":
                      github_version = github_response_json["tag_name"]

                      if github_response.status_code == 200:
                          # Extrahiere das Release-Tag aus der JSON-Antwort
                          print("Latest release tag is "+ github_version)
                      else:
                          print("Error trying to fetch tag name from repo.")

                      if LooseVersion(version) > LooseVersion(github_version):
                          compare_version = "looks like your using an unreleased version :eyes:"
                      elif LooseVersion(version) < LooseVersion(github_version):
                          compare_version = "New Version on [GitHub](https://github.com/Wargamer-Senpai/teampy/releases/latest) available :eyes:"
                      else:
                          compare_version = ":sparkles: Your using the latest release :sparkles:"
                    else:
                      compare_version = "__Error while trying to fetch info from GitHub__"

                    matrix_send_message = "Current Version of Teampy **" + version + "**"+ \
                      "\n"+compare_version
                    print(matrix_send_message)
                  else:
                    matrix_send_message = rank_error_message

                elif config.command_prefix + config.command_ping in matrix_received_message:
                  matrix_send_message = "!pong"
                  raw_ping = ""
                  if os_name == "Linux":
                    command_output = subprocess.Popen("ping -c 1 chat.teamspeak.com | grep icmp | awk '{print $8}' | sed s/'time='/''/g", stdout=subprocess.PIPE, shell=True)
                    raw_output, _ = command_output.communicate()
                    latency = str(raw_output).strip().replace("\\n", "").replace("b", "").replace("\'", "")
                    matrix_send_message += "\nLatency to ts: " + latency + "ms"
                    
                  elif os_name == "Windows":
                    command_output = subprocess.Popen("powershell .\\modules\\ping.ps1 chat.teamspeak.com", stdout=subprocess.PIPE)
                    raw_output, _ = command_output.communicate()
                    raw_output = str(raw_output).strip().split()
                    latency = ""
                    for word in raw_output:
                        if "ms" in word:
                            latency = word.replace("\\r\\n\'", "") # removing EOL from windows
                            break
                        
                    matrix_send_message += "\nLatency to ts: " + latency

                    stat_dict["ping_command_count"] += 1
                elif matrix_received_message.startswith(config.command_prefix):
                  matrix_send_message = "command not found :thinking: ("+matrix_received_message+")\nif you need more info use `"+config.command_prefix+config.command_help+"`"

                else :
                  print("[DBG] chat message not directed to bot")

                # check for bad words
                if config.bad_word_checks == True:
                  for word in bad_words:
                    if word in matrix_received_message:
                      matrix_received_message = "no you"
                      matrix_send_message = func_send_gif()

                if matrix_send_message:
                  # Send message to Matrix Room
                  message_url = config.matrix_base_url + "/_matrix/client/r0/rooms/" + room_id + "/send/m.room.message"
                  message_data = {"msgtype": "m.text", "body": matrix_send_message}
                  message_headers = {"Authorization": "Bearer " + access_token, "User-Agent": user_agent}
                  response = requests.post(message_url, json=message_data, headers=message_headers)
                  matrix_send_message=""
                  if response.status_code == 200:
                    print("[DBG] Message sent successfully!")
                    stat_dict["messages_send_count"] += 1
                  else:
                    print("[ERR] Error sending message to Matrix: %s" % response.text)
                    time.sleep(2)

                  # set message to read, only works in privat chat
                  payload = {"m.fully_read": event["event_id"], "m.read": event["event_id"]}
                  receiptType="m.fully_read"
                  response = requests.post(config.matrix_base_url + "/_matrix/client/r0/rooms/" + room_id + "/read_markers", headers=message_headers, json=payload)
                  
                  if response.status_code == 200:
                    print("[DBG] Message successfully set to read!" )
                  else:
                    print("[ERR] Error setting message to Read: %s" % response.text)
                    time.sleep(2)
                  # write new stats to file
                  with open(stats_file, "w") as f:
                      for key, value in stat_dict.items():
                          f.write(f"{key}={value}\n")

                  time.sleep(1)

                  if config.command_prefix + config.command_admin_stop == matrix_received_message and matrix_sender in config.bot_admin:
                    exit(0)
                  elif config.command_prefix + config.command_admin_restart == matrix_received_message and matrix_sender in config.bot_admin:

                    # splitted linux and windows if function shouldnt work, TODO: test on linux
                    if os_name == "Linux":
                      python_executable = sys.executable
                      script_path = os.path.dirname(os.path.abspath(__file__))
                      script_file = os.path.join(script_path, "./modules/restart.py")
                      os.system(python_executable + " " + script_file + " " + os_name )
                    if os_name == "Windows":
                      python_executable = sys.executable
                      script_file = script_path +".\\modules\\restart.py" 
                      subprocess.call([python_executable, script_file, os_name])

                    else:
                      exit(255)
                  matrix_sender = "" #clear sender of message


    else:
      #print("[DBG] no new question found")
      time.sleep(1)
      response = requests.get(sync_url, headers=sync_headers)

    # check if he got invited into a new room 
    func_check_invite()
  else:
      print("Error getting messages from Matrix: %s" % response.text)
  

