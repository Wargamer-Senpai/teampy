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


# command prefix 
command_prefix = "!"

#general commands
command_gif = "gif"
command_help = "help"
command_ping = "ping"
command_btc = "btc"
command_eth = "eth"
command_whoami = "whoami"
command_whois = "whois"

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

# normal user help page 
help_display = {
    command_gif: "send random gif or use search tag `!gif <search>`",
    command_help: "display this list",
    command_ping: "lets ping pong",
    command_btc: "display prices of Bitcoin",
    command_eth: "display prices of Ethereum",
    command_whoami: "tells you your identifier and name and if your admin",
    command_whois: "parse the matrix identifier and i will find the name of the person `"+ command_prefix + command_whois+" <identifier>`"
    }

# admin help page 
admin_help_display = {
    command_admin_help: "display this admin help",
    command_admin_version: "display version of bot, and checks for new version",
    command_admin_health: "checks health of bot, if there is a problem it hopefully will display it",
    command_admin_stop: "stops the bot",
    command_admin_restart: "restarts the bot",
    command_admin_leave: "tells the bot to leave the current room",
    command_admin_stats: "display gathered stats",
    command_admin_reload: "reload current config",
    command_admin_autojoin: "toggle auto join for rooms and direct chats on invite to on or off"
    }   
