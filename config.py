# Matrix Homeserver URL
matrix_base_url = "https://chat.teamspeak.com"

# Matrix User Credentials, get via TS5Extractor (https://github.com/Gamer08YT/TS5Extractor)
# Recommended to use a second account, which isnt that important
# Example:
# matrix_username = aefaefaefaefaefa354354354354===
# matrix_password = JkFpIopKKKtdf55uimne69
matrix_username = ""
matrix_password = ""

# Bot admin/s
# How to get you identifier:
# ask the bot !whoami and copy paste the identifier
# Example: 
# bot_admin = ["@rf5vjqmalallfdf48vg32420rrxlsibkrackg4j5pfquk3bt69zii===:chat.teamspeak.com", "@rf5vjqrumallfdf48vg32644rrxlsibkcracg4j5pfquk3bt69zii===:chat.teamspeak.com"]
bot_admin = [""]

# set if bot is allowed to join new groups he gets invited to 
# Example:
# matrix_join_rooms = True / matrix_join_rooms = False
matrix_join_rooms = True

# giphy api key
# if left empty, module wont work/is disabled
# Example:
# giphy_api_key="JukUjkllöpop69I134Verr694523Rinn"
giphy_api_key="DNfeltInmrTesyYnk02MqdrE5LB2FCpW"


# set avatar url here
# WIP, not working 
#avatar_url = "currently broken (ㆆ_ㆆ)"

# set status text
status_text = "✨ vibing ヾ(•ω•`)o ✨" 

# set presence
# Only insert "online", "offline", "unavailable"
# WIP, only shows online
presence_state = "online"

# stats to normal user visible
# the bot gathers some data anonymously
# for example how many times he got pinged and ponged, how many gifs did he sent, etc...
# Example: 
# stats_visible = "public" or "admins"
stats_visible = "public"

# check if in conversation is a bad word
# if set to True, the bot will search out an gif, with the context of "no you"
# only works if gihpy api is not empty
bad_word_checks = False

# set message when the bot detects a new version 
# you can use <@_|everyone> to ping everyone
# the new found version will always be added later on, when sending the message, it will look like this:
# @everyone it looks like a new update arrived, Version: beta74
matrix_update_message = "<@_|everyone> it looks like a new update arrived, Version: " 

# enable plugins
# in the folder plugins, here can be put addiotonal code
# Default: plugins_on
plugins_on = True


# command prefix 
command_prefix = "!"

#general commands
command_gif = "gif"
command_stats = "stats"
command_help = "help"
command_ping = "ping"
command_btc = "btc"
command_eth = "eth"
command_whoami = "whoami"
command_whois = "whois"
command_dice = "roll"
command_poll = "poll"

#admin commands
command_base_admin = "admin " 
command_admin_base = command_base_admin + "help"
command_admin_help = command_base_admin + "help"
command_admin_status = command_base_admin + "status"
command_admin_version = command_base_admin + "version"
command_admin_health = command_base_admin + "health"
command_admin_stop = command_base_admin + "stop"
command_admin_restart = command_base_admin + "restart"
command_admin_leave = command_base_admin + "leave-room"
command_admin_stats = command_base_admin + "stats"
command_admin_reload = command_base_admin + "reload"
command_admin_autojoin = command_base_admin + "autojoin"
command_admin_notify = command_base_admin + "update-notify"

# normal user command overview
# toggle command with True or False
commands_overview = {
    command_gif: {"description": "send random gif or use search tag `!gif <search>`", "command_enabled": True},
    command_stats: {"description": "display gathered stats", "command_enabled": True},
    command_help: {"description": "display this list", "command_enabled": True},
    command_ping: {"description": "lets ping pong", "command_enabled": True},
    command_btc: {"description": "display prices of Bitcoin", "command_enabled": True},
    command_eth: {"description": "display prices of Ethereum", "command_enabled": True},
    command_whoami: {"description": "tells you your identifier and name and if your admin", "command_enabled": True},
    command_whois: {"description": "parse the matrix identifier and i will find the name of the person `"+ command_prefix + command_whois+" <identifier>`", "command_enabled": True},
    command_dice: {"description": "roll a number between 1 and 6", "command_enabled": True},
    command_poll: {"description": "start a poll with emojis to vote, example `!poll should we do polls?` \
                    more info [here](https://github.com/Wargamer-Senpai/teampy/wiki/Overview#poll-string)", "command_enabled": True}
    }

# admin command overview 
# toggle command with True or False
admin_commands_overview = {
    command_admin_help: {"description": "display this admin help", "command_enabled": True},
    command_admin_version: {"description": "display version of bot, and checks for new version", "command_enabled": True},
    command_admin_health: {"description": "checks health of bot, if there is a problem it hopefully will display it", "command_enabled": True},
    command_admin_stop: {"description": "stops the bot", "command_enabled": True},
    command_admin_restart: {"description": "restarts the bot", "command_enabled": True},
    command_admin_leave: {"description": "tells the bot to leave the current room", "command_enabled": True},
    command_admin_stats: {"description": "display gathered stats", "command_enabled": True},
    command_admin_reload: {"description": "reload current config", "command_enabled": True},
    command_admin_autojoin: {"description": "toggle auto join for rooms and direct chats on invite to on or off", "command_enabled": True},
    command_admin_notify: {"description": "toggle notifcation, for room the command was entered in", "command_enabled": True}
    }   



#
# set log level 
#
# Possible values: CRITICAL, ERROR, WARNING, INFO, DEBUG
# default and recommended: "INFO" 
log_level="INFO"