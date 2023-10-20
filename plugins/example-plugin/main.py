# coding=utf-8
# This is an example plugin, so its better to understand the way the bot handles plugins/external scripts.
# So make sure youve named this file main.py and put it in its own folder in the plugins directory.
#
# When programming on a plugin you dont need to restart the bot, because of the way the bot handels the plugins.


# needed for getting the variables that are being parsed by the bot
import sys

#
# structur of possible values 
# 

# sys.argv[1] = "Hello"      
# - Description: the message the bot got 

# sys.argv[2] = "@ae5vjqrumaladsjkflklöajdsfacg4j5pfquk3bt55z5i===:chat.teamspeak.com" 
# - Description: Contains the matrix user id (MXID), is unique for every user

# sys.argv[3] = "!"       
# - Description: Contains the used command prefix that is in the config of the bot

# sys.argv[4] = "user"    
# - Description: Delivers the rank of the user, if the users matrix identifier is in the admin array the value "admin" will be send else only "user"


# or if you like it smart
# name the variables what you want, so they fit your handwriting
message = sys.argv[1] 
message_sender = sys.argv[2] 
command_prefix = sys.argv[3] 
user_rank = sys.argv[4] 



# !! READ THIS !!
# TLDR;
# print out what you want the bot to send as an answer
#                     
#
# Explanation:
# The bot executes the plugins one by one, as soon he gets an value returend,
# he will stop further execution of plugins and sends the value to the chat as the answer.
# If multiple values are printed by your plugin in diffrent print's they will be send together.
#

# 
# If any values you need are missing, then open an issue on github and i will look if its possible to put it in.
# https://github.com/Wargamer-Senpai/teampy/issues
#
# Have fun



# your script logic	here
if sys.argv[1] == sys.argv[3]+"Hello":
  print("Hello World")
