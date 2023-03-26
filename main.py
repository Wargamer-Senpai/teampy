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
# ChatGPT helped creating the code (¬‿¬)
# Gamer08YT helped with the user agent for the teamspeak Matrix Server

import requests
import json
import time
import random

# import config.py
from config import *

# import bad_words.py
from bad_words import * 

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



#
# functions
#

# check if new invite is available
def func_check_invite():
    global sync_response
    check_current_rooms = str(sync_response.get("rooms"))
    if check_current_rooms != "None" and matrix_join_rooms == True:
      check_invite_key = str(sync_response["rooms"].get("invite"))

      if check_invite_key != "None": 
        matrix_new_room = sync_response["rooms"]["invite"]
        matrix_new_room = list(matrix_new_room.keys())[0]

        # send post request, to join the room
        response = requests.post(matrix_base_url + f"/_matrix/client/r0/join/{matrix_new_room}", headers=sync_headers)
        
        if response.status_code == 200:
          name_url = matrix_base_url + f"/_matrix/client/r0/rooms/{matrix_new_room}/state"
          response = requests.get(name_url, headers=sync_headers)
          room_name = response.json()[6]["content"]["name"]
          print("[INF] successfully joined room (Name: "+room_name+")")
        else:
          print("[ERR] couldnt join room %s" % response.text)

# set avatar
def func_set_avatar():
  if avatar_url:
    avatar_data = {"avatar_url": avatar_url} 
    response = requests.put(matrix_base_url + "/_matrix/client/r0/profile/"+matrix_self+"/avatar_url", headers=sync_headers, json=avatar_data)
    if response.status_code == 200:
      response = requests.get(matrix_base_url + "/_matrix/client/r0/profile/@ae5vjqrumallcuumkvg326ddcqxlsibkcracg4j5pfquk3bt55z5i===:chat.teamspeak.com/avatar_url", headers=sync_headers)
      new_avatar_url = response.json()
      print(f"[INF] Bot avatar changed successfully. ({new_avatar_url})")
    else:
      print("[ERR] Failed to change bot avatar. %s" % response.text)

# set status message and presence 
def func_set_status():
   if status_text and presence_state:
    status_data = {"presence": presence_state, "status_msg": status_text}
    response = requests.put(matrix_base_url + "/_matrix/client/r0/presence/"+matrix_self+"/status", headers=sync_headers, json=status_data)
    if response.status_code == 200:
      print("[INF] Status message updated successfully.")
    else:
      print("[ERR] Failed to update status message. %s" % response.text)

def func_send_gif():
  if giphy_api_key:
    message_index = matrix_received_message.find(" ")
    #get search string, if available
    giphy_search_string = matrix_received_message[message_index+1:] 
    if not command_prefix + command_gif ==  giphy_search_string:
      random_gif = random.randint(0, 30)
      url = f"https://api.giphy.com/v1/gifs/search?api_key={giphy_api_key}&q={giphy_search_string}&limit=1&offset={random_gif}&rating=g&lang=en"
    else:
      url = f"https://api.giphy.com/v1/gifs/random?api_key={giphy_api_key}&tag=&rating=r"

    response = requests.get(url)
    data = response.json()

    if not command_prefix + command_gif ==  giphy_search_string:
      if len(data["data"]) > 0:
        matrix_send_message = data['data'][0]['images']['original']['url'] 
      else:
        matrix_send_message = "ups whoopsy, couldnt find your search string (404)"
    else:
      matrix_send_message = data['data']['images']['original']['url'] 
  else:
    matrix_send_message="i have a problem, the api key is missing in the config, please contact the admin ＞︿＜"
  return matrix_send_message

#
# starting of the script
#
if not matrix_username or not matrix_password:
  print("[ERR] finish configuration step first!")
  exit()

print("starting bot....")
# login to Matrix and get access token and own user id
login_url = matrix_base_url + "/_matrix/client/r0/login"
login_data = {"type": "m.login.password", "user": matrix_username, "password": matrix_password}
login_headers = {"User-Agent": user_agent}
response = requests.post(login_url, json=login_data, headers=login_headers)
access_token = response.json()["access_token"]
matrix_self = response.json()["user_id"]


# prepare first sync
sync_url = matrix_base_url + "/_matrix/client/r0/sync?3000"
sync_headers = {"Authorization": "Bearer " + access_token, "User-Agent": user_agent}
next_batch = None

#make initial request (so he ignores old chats)
response = requests.get(sync_url, headers=sync_headers)
sync_response = json.loads(response.text)
func_check_invite()
next_batch = sync_response["next_batch"]
sync_url = matrix_base_url + "/_matrix/client/v3/sync?timeout=1000&since=" + next_batch



#pretty print
#print(json.dumps(arry,sort_keys=True, indent=4))

# not working 
#func_set_avatar()
func_set_status()

while True:
  time.sleep(1)

  # make a request to the sync API to check for new events
  response = requests.get(sync_url, headers=sync_headers)
  
  # check if the response was successful
  if response.status_code == 200:
    # parse the response JSON to extract any new events
    sync_response = json.loads(response.text)

    # prepare next sync
    # get new synctoken
    next_batch = sync_response["next_batch"]
    # update the sync token to the latest value
    sync_url = matrix_base_url + "/_matrix/client/r0/sync?timeout=1000&since=" + next_batch
    
    check_current_rooms = str(sync_response.get("rooms"))
    if check_current_rooms != "None":
      check_active_rooms = str(sync_response["rooms"].get("join"))
      if check_active_rooms != "None":
        # check if in any room is something new, if not just wait and retry
        if "rooms" in sync_response and sync_response["rooms"] is not None:
          # Check if there are any new messages in the room
          for room_id in sync_response["rooms"]["join"]:
            # Check if this is the room we're interested in
            # Loop through all new events in the room
            for event in sync_response["rooms"]["join"][room_id]["timeline"]["events"]:
              # Check if the event is a message
              if event["type"] == "m.room.message" and event["sender"] != matrix_self:
                # Print the message body
                print("[DBG] "+event["sender"]  + ": " + event["content"]["body"])
                matrix_received_message = event["content"]["body"]
                # check what command was send
                if command_prefix + command_gif in matrix_received_message:
                  matrix_send_message = func_send_gif()
                elif command_prefix + command_btc in matrix_received_message:
                  btc_base_url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies="
                  
                  btc_gbp_respond = requests.get(btc_base_url + "gbp")
                  btc_gbp = btc_gbp_respond.json()["bitcoin"]["gbp"]

                  btc_eur_respond = requests.get(btc_base_url + "eur")
                  btc_eur = btc_eur_respond.json()["bitcoin"]["eur"]

                  btc_usd_respond = requests.get(btc_base_url + "usd")
                  btc_usd = btc_usd_respond.json()["bitcoin"]["usd"]

                  matrix_send_message = f"__**Prices are not so precise**__\nCurrent Price of BTC: \
                  \nEuro: {btc_eur} \nGBP: {btc_gbp} \nUSD: {btc_usd} \
                  \nfrom https://www.coingecko.com/"

                elif command_prefix + command_eth in matrix_received_message:
                  eth_base_url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies="
                  
                  eth_gbp_respond = requests.get(eth_base_url + "gbp")
                  eth_gbp = eth_gbp_respond.json()["ethereum"]["gbp"]

                  eth_eur_respond = requests.get(eth_base_url + "eur")
                  eth_eur = eth_eur_respond.json()["ethereum"]["eur"]

                  eth_usd_respond = requests.get(eth_base_url + "usd")
                  eth_usd = eth_usd_respond.json()["ethereum"]["usd"]

                  matrix_send_message = f"__**Prices are not so precise**__\nCurrent Price of ETH: \
                  \nEuro: {eth_eur} \nGBP: {eth_gbp} \nUSD: {eth_usd} \
                  \nfrom https://www.coingecko.com/"

                elif command_prefix + command_help in matrix_received_message:
                    matrix_send_message = "Here is help, dont worry!\n"
                    for key in help_display:
                      matrix_send_message += "**" + command_prefix + key + ":** " + help_display[key] + "\n"

                elif command_prefix + command_ping in matrix_received_message:
                    matrix_send_message = "!pong"
               
                elif matrix_received_message.startswith(command_prefix):
                    matrix_send_message = "command not found ＞︿＜ ("+matrix_received_message+")\nif you need more info use `"+command_prefix+command_help+"`"

                else :
                  print("[DBG] chat message not directed to bot")
                for word in bad_words:
                  if word in matrix_received_message:
                    matrix_received_message = "no you"
                    matrix_send_message = func_send_gif()

                if matrix_send_message:
                  # Send message to Matrix Room
                  message_url = matrix_base_url + "/_matrix/client/r0/rooms/" + room_id + "/send/m.room.message"
                  message_data = {"msgtype": "m.text", "body": matrix_send_message}
                  message_headers = {"Authorization": "Bearer " + access_token, "User-Agent": user_agent}
                  response = requests.post(message_url, json=message_data, headers=message_headers)
                  matrix_send_message=""
                  if response.status_code == 200:
                      print("[DBG] Message sent successfully!")
                  else:
                      print("[ERR] Error sending message to Matrix: %s" % response.text)
                      time.sleep(2)


                  # set message to read, only works in privat chat
                  payload = {"m.fully_read": event["event_id"], "m.read": event["event_id"]}
                  receiptType="m.fully_read"
                  response = requests.post(matrix_base_url + f"/_matrix/client/r0/rooms/{room_id}/read_markers", headers=message_headers, json=payload)
                  
                  if response.status_code == 200:
                      print("[DBG] Message successfully set to read!" )
                  else:
                      print("[ERR] Error setting message to Read: %s" % response.text)
                      time.sleep(2)

                  time.sleep(1)

      # check if he got invited into a new room 
      func_check_invite()

    else:
      #print("[DBG] no new question found")
      time.sleep(1)
      response = requests.get(sync_url, headers=sync_headers)

  else:
      print("Error getting messages from Matrix: %s" % response.text)
  

