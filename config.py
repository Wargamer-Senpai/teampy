# Matrix Homeserver URL
matrix_base_url = "https://chat.teamspeak.com"

# Matrix User Credentials, get via TS5Extractor (https://github.com/Gamer08YT/TS5Extractor)
# Recommended to use a second account, which isnt that important
# Example:
# matrix_username = aefaefaefaefaefa354354354354===
# matrix_password = JkFpIopKKKtdf55uimne69
matrix_username = ""
matrix_password = ""

# set if bot is allowed to join new groups he gets invited to 
# Example:
# matrix_join_rooms = True / matrix_join_rooms = False
matrix_join_rooms = True

# giphy api key
# if left empty, module wont work/is disabled
# Example:
# giphy_api_key="JukUjkllöpop69I134Verr694523Rinn"
giphy_api_key=""

# change command prefix if wanted
command_prefix = "!"

# set avatar url here
# WIP, not working 
#avatar_url = "currently broken (ㆆ_ㆆ)"

# set status text
# WIP, not working 
status_text = "✨ vibing ヾ(•ω•`)o ✨" 


# set presence
# WIP, not working 
# Only insert "online", "offline", "unavailable"
presence_state = "online"

# check if in conversation is a bad word
# if set to True, the bot will search out an gif, with the context of "no you"
# only works if gihpy api is not empty
bad_word_checks = False

#commands, change if you want 
command_gif = "gif"
command_help = "help"
command_ping = "ping"
command_btc = "btc"
command_eth = "eth"


#the commands that get displayed when !help was ommited
help_display = {
              command_gif: "send random gif or use search tag `!gif <search>`",
              command_help: "display this list",
              command_ping: "lets ping pong",
              command_btc: "display prices of Bitcoin",
              command_eth: "display prices of Ethereum" }
