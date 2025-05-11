import random
import subprocess
import ping3
import os

from modules.matrix import *
from modules.utils import func_fetch_coin_prices

def func_handle_gif(command_prefix, command_gif, giphy_api_key, matrix_received_message):
  """Handle the gif command and send a random gif or a gif based on a search string to the chat

  Args:
      command_prefix (str): command prefix for the bot commands
      command_gif (str): command name for the gif command
      giphy_api_key (str): Giphy API key for fetching gifs
      matrix_received_message (str): received message from chat
  
  Returns:
      str: URL of the gif to be sent to the chat
  """
  if giphy_api_key:
    message_index = matrix_received_message.find(" ")
    #get search string, if available
    giphy_search_string = matrix_received_message[message_index+1:] 

    if not command_prefix + command_gif == giphy_search_string:
      random_gif = random.randint(0, 30)
      url = "https://api.giphy.com/v1/gifs/search?api_key="+giphy_api_key+"&q="+giphy_search_string+"&limit=1&offset="+str(random_gif)+"&rating=g&lang=en"
    else:
      url = "https://api.giphy.com/v1/gifs/random?api_key="+giphy_api_key+"&tag=&rating=r"

    response = requests.get(url)
    data = response.json()

    if not command_prefix + command_gif ==  giphy_search_string:
      if len(data["data"]) > 0:
        return(data['data'][0]['images']['original']['url'])
      else:
        return("couldnt find your search string (404)")
    else:
      return(data['data']['images']['original']['url'])
  else:
    return("i have a problem, the api key is missing in the config, please contact the admin :anxious:")


def func_handle_crypto(crypto_currency):
  """Handle the crypto command and send the current price of the specified cryptocurrency in GBP, EUR, and USD

  Args:
      crypto_currency (str): the cryptocurrency to fetch prices for (e.g. "bitcoin" or "ethereum")
  
  Returns:
      str: formatted message with the current prices of the cryptocurrency
  """
  prices = func_fetch_coin_prices(crypto_currency, ["gbp", "eur", "usd"])
  response_msg = (
      f"__**Prices are not so precise**__\nCurrent Price of {crypto_currency}:\n" +
      "\n".join(f"{cur.upper()}: {price}" for cur, price in prices.items()) +
      "\nfrom https://www.coingecko.com/"
  )
  return(response_msg)


def func_handle_help(commands_overview,command_prefix):
  """Handle the help command and send a list of available commands to the user

  Args:
      commands_overview (dict): dictionary with command names and their descriptions
      command_prefix (str): command prefix for the bot commands
  
  Returns:
      str: formatted message with the list of available commands
  """
  matrix_prepare_message = "Here is help, dont worry!\n"
  for key in commands_overview:
    if commands_overview[key]["command_enabled"] == True:
      matrix_prepare_message += "**" + command_prefix + key + ":** " + commands_overview[key]["description"] + "\n"
  return(matrix_prepare_message)


def func_handle_whoami(matrix_base_url,sync_headers,bot_admin,matrix_sender):
  """Handle the whoami command and send to the user the identifier and name of the user who sent the message

  Args:
      matrix_base_url (str): the base URL of the Matrix server
      sync_headers (dict): the HTTP headers used for the sync request
      bot_admin (list): list of uuids of bot admins
      matrix_sender (str): the sender of the message

  Returns: 
      str: formatted message with the identifier and name of the user
  """
  matrix_sender_name = func_get_username(matrix_base_url,matrix_sender,sync_headers)
  user_rank = "User"
  if matrix_sender in bot_admin: 
    user_rank = "Admin"
  return("Your identifier is: "+ matrix_sender + "\nYour name is: " + matrix_sender_name \
  + "\nI see you as a " + user_rank)


def func_handle_whois(matrix_base_url,sync_headers,matrix_received_message,bot_admin):
  """Handle the whois command and send to the user the identifier and name of the user he has requested

  Args:
      matrix_base_url (str): the base URL of the Matrix server
      sync_headers (dict): the HTTP headers used for the sync request
      matrix_received_message (str): received message from chat
      bot_admin (list): list with uuids of bot admins

  Returns:
      str: formatted message with the identifier and name of the requested user
  """
  user_rank = "User"

  message_index = matrix_received_message.find(" ")
  # get search string, if available
  matrix_identifier = matrix_received_message[message_index+1:] 
  if matrix_identifier:
    request_sender_name = requests.get(matrix_base_url + "/_matrix/client/r0/profile/" + matrix_identifier, headers=sync_headers)
    repsonse_name = request_sender_name.json()

    check_identifier_name = str(repsonse_name.get("displayname"))
    if check_identifier_name != "None":
      matrix_sender_name = repsonse_name["displayname"]
    else:
      matrix_sender_name = "**Couldnt find Name**"
      user_rank = "Unknown"

    if matrix_identifier in bot_admin: 
      user_rank = "Admin"

    return("The identifier is: "+ matrix_identifier + "\nThe name is: " + matrix_sender_name \
    + "\nI see that person as a " + user_rank)
  else:
    return("I need a identifier to search for, please use the command like this: `!whois <identifier>`") 

def func_handle_stats(stats_visible,stat_dict,bot_admin,stats_description,matrix_sender):
  """Handle the stats command and send the stats to the chat

  Args:
      stats_visible (str): visibility of the stats (public, admin)
      stat_dict (dict): dictionary with stats 
      bot_admin (list): list of uuids of bot admins
      stats_description (dict): dictionary with descriptions of the stats
      matrix_sender (str): the sender of the message

  Returns:
      str: formatted stats message
  """
  matrix_prepare_message = "Here are some stats, enjoy!\n"
  if stats_visible == "public" or  stats_visible == "admin" and matrix_sender in bot_admin:
    for key in stat_dict:
      matrix_prepare_message += "\n"+stats_description[key]+": **" + str(stat_dict[key]) + "**"
    return(matrix_prepare_message)
  else:
    return("the stats are currently only visible for admins :eyes:")


def func_handle_ping():
  """Ping the Teamspeak server and return the latency

  Returns:
      str: latency message
  """
  matrix_prepare_message = "!pong"
  # Ping returns the round-trip time in seconds (or None if the host is unreachable)
  latency = ping3.ping("chat.teamspeak.com", timeout=2)
  if not latency is None:
    # Convert latency to milliseconds
    latency_ms = latency * 1000
    return(matrix_prepare_message + "\nLatency to ts: {:.2f}ms".format(latency_ms))
  else:
    return(matrix_prepare_message + "\nFailed to ping chat.teamspeak.com")


def func_handle_roll():
  """Roll a dice and send the result to the chat

  Returns:
      str: result of the dice roll
  """
  dice_number = random.randint(1, 6)
  return("You rolled a **" + str(dice_number) + "** :exploding_head:")


def func_handle_poll(matrix_received_message,poll_emojis):
  """Create a poll based on the received message

  Args:
      matrix_received_message (str): received message from chat
      poll_emojis (list): list of emojis to use for the poll

  Returns:
      str: formatted poll message
  """
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

  return("a new poll just started! \n\nQuestion: \"__" + poll_question + "__\"\n" \
  + "Choose the reaction from below to vote\n\n Choices:\n" + poll_choices)


def func_handle_plugins(matrix_sender,bot_admin,main_script_path,matrix_received_message,command_prefix):
  """Execute plugins based on a received Matrix message

  Args:
      bot_admin (list): list of uuids of bot admins
      main_script_path (str): fullpath to main script
      matrix_received_message (str): received message from chat
      command_prefix (str): command prefix for the bot commands

  Returns:
      str: Output from the executed plugin, if any
  """
  if matrix_sender in bot_admin:
    plugin_rank="admin"
  else:
    plugin_rank="user"
  for subdir, _, _ in os.walk(os.path.join(main_script_path,"plugins")):
    plugin_path = os.path.join(subdir, "main.py")
    if os.path.exists(plugin_path):
      try:
        plugin_output = subprocess.check_output(["python3", plugin_path, matrix_received_message, matrix_sender, command_prefix,plugin_rank], text=True).strip()
        if plugin_output:
          return plugin_output
        else:
          return None
      except subprocess.CalledProcessError as e:
        func_write_to_log("There was an error executing a plugin, Path: " + str(plugin_path) + " Error: " + str(e), "ERROR", "func_handle_plugins")